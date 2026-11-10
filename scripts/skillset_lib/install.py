"""Exact source acquisition and installation-only, whole-set activation."""

from copy import deepcopy
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import uuid

from .core import Error, atomic_write, contained, copy_tree, fingerprint, publish_locks, read_json, write_many


_COMMIT = re.compile(r'[0-9a-f]{40}\Z')
_FINGERPRINT = re.compile(r'[0-9a-f]{64}\Z')
_SCOPES = ('shared', 'private')


def _git(*arguments, cwd=None, code=3, allow_failure=False):
    environment = {**os.environ, 'GIT_TERMINAL_PROMPT': '0', 'GIT_OPTIONAL_LOCKS': '0'}
    try:
        result = subprocess.run(
            ['git', '-c', 'core.hooksPath=/dev/null', '-c', 'core.fsmonitor=false', *arguments],
            cwd=cwd, env=environment, text=True, capture_output=True,
        )
    except OSError as exc:
        raise Error(f'Cannot run Git: {exc}', code) from exc
    if result.returncode and not allow_failure:
        diagnostic = result.stderr.strip() or result.stdout.strip() or 'Git command failed'
        raise Error(diagnostic, code)
    return result


def _key(source_id):
    return hashlib.sha256(source_id.encode()).hexdigest()


def _store_path(paths, relative):
    """Generated store directories may not be redirected through symlinks."""
    result = paths.data / relative
    current = paths.data
    if current.is_symlink() or current.exists() and not current.is_dir():
        raise Error('The installation data root was replaced by a non-directory', 4)
    components = Path(relative).parts
    for index, component in enumerate(components):
        current = current / component
        if current.is_symlink():
            raise Error(f'Managed store path is unexpectedly symlinked: {current}', 4)
        if index < len(components) - 1 and current.exists() and not current.is_dir():
            raise Error(f'Managed store directory was replaced by a file: {current}', 4)
    contained(paths.data, relative)
    return result


def _mkdir(path, root):
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    if root.is_symlink() or not root.is_dir():
        raise Error(f'Managed store root is not a directory: {root}', 4)
    current = root
    for component in path.relative_to(root).parts:
        current = current / component
        if current.is_symlink():
            raise Error(f'Managed store path is unexpectedly symlinked: {current}', 4)
        current.mkdir(exist_ok=True, mode=0o700)


def _cache_path(model, source_id, source, revision):
    return _store_path(model.paths, f'{source["visibility"]}/cache/{_key(source_id)}/{revision}')


def _fetch(tree, url, revision):
    _git('init', '-q', str(tree))
    _git('-C', str(tree), 'fetch', '--quiet', '--no-tags', '--depth=1', '--', url, revision)
    resolved = _git('-C', str(tree), 'rev-parse', '--verify', 'FETCH_HEAD^{commit}').stdout.strip()
    if not _COMMIT.fullmatch(resolved):
        raise Error('Remote target is not a supported exact Git commit', 3)
    return resolved


def _resolve_tracking(source_id, source):
    ref = source['ref']
    if ref.startswith(('refs/heads/', 'refs/tags/')):
        names = [ref]
    elif ref.startswith('refs/'):
        raise Error(f'Source {source_id} must track a branch or tag', 2)
    else:
        names = [f'refs/heads/{ref}', f'refs/tags/{ref}']
    patterns = [name for name in names]
    patterns.extend(name + '^{}' for name in names if name.startswith('refs/tags/'))
    advertised = _git('ls-remote', '--', source['url'], *patterns).stdout
    revisions = {}
    for line in advertised.splitlines():
        fields = line.split('\t', 1)
        if len(fields) == 2 and fields[1] in patterns:
            if not _COMMIT.fullmatch(fields[0]):
                raise Error(f'Unsupported Git object format for source {source_id}', 3)
            revisions[fields[1]] = fields[0]
    matches = [name for name in names if name in revisions]
    if not matches:
        raise Error(f'Tracking branch or tag is unavailable for source {source_id}: {ref}', 3)
    if len(matches) != 1:
        raise Error(f'Tracking ref is ambiguous between branch and tag for source {source_id}: {ref}', 3)
    name = matches[0]
    # Resolve the advertised object, not a ref that could move between the two requests.
    with tempfile.TemporaryDirectory(prefix='skillset-update-') as temporary:
        resolved = _fetch(Path(temporary) / 'repository', source['url'], revisions[name])
    expected = revisions.get(name + '^{}', revisions[name])
    if resolved != expected:
        raise Error(f'Tracking target is not an unambiguous commit for source {source_id}', 3)
    return resolved


def update(model, source_ids, all_sources=False):
    """Resolve every explicit target before transactionally publishing any lock."""
    model.validate(selection=False)
    if all_sources and source_ids:
        raise Error('Choose explicitly named sources or --all, not both')
    if not all_sources and not source_ids:
        raise Error('Update requires source IDs or --all')
    targets = sorted(set(source_ids) if not all_sources else
                     {key for key, source in model.sources.items() if source['type'] == 'git'})
    for source_id in targets:
        source = model.sources.get(source_id)
        if source is None or source['type'] != 'git':
            raise Error(f'Update target is not a registered remote source: {source_id}')
    documents, updates = {}, []
    for source_id in targets:
        source = model.sources[source_id]
        scope = source['visibility']
        revision = _resolve_tracking(source_id, source)
        if scope not in documents:
            documents[scope] = deepcopy(model.locks[scope])
        old = documents[scope]['sources'].get(source_id)
        documents[scope]['sources'][source_id] = revision
        updates.append({'source': source_id, 'visibility': scope,
                        'old_revision': old, 'new_revision': revision})
    roots = {'shared': model.paths.shared, 'private': model.paths.config}
    try:
        publish_locks(model.paths, {roots[scope] / 'lock.json': doc for scope, doc in documents.items()})
    except OSError as exc:
        raise Error(f'Cannot publish revision locks: {exc}', 3) from exc
    for scope, document in documents.items():
        model.locks[scope] = document
    return {'schema_version': 1, 'updates': updates}


def _working_state(root):
    repository = _git('-C', str(root), 'rev-parse', '--is-inside-work-tree', allow_failure=True)
    if repository.returncode or repository.stdout.strip() != 'true':
        return None, 'unversioned'
    status = _git('-C', str(root), 'status', '--porcelain', '--untracked-files=all',
                  '--ignored', '--', '.')
    dirty = bool(status.stdout.strip())
    return dirty, 'dirty' if dirty else 'clean'


def _check_cache(model, source_id, source, revision, cache):
    _store_path(model.paths, str(cache.relative_to(model.paths.data)))
    if not cache.is_dir():
        raise Error(f'Managed source cache was replaced by a non-directory: {source_id}', 4)
    metadata_path = cache / 'metadata.json'
    if metadata_path.is_symlink() or metadata_path.exists() and not metadata_path.is_file():
        raise Error(f'Managed source metadata was replaced or redirected: {source_id}', 4)
    metadata = read_json(metadata_path, {'schema_version': 1})
    if (metadata.get('source') != source_id or metadata.get('revision') != revision or
            metadata.get('url') != source['url'] or metadata.get('visibility') != source['visibility'] or
            not isinstance(metadata.get('fingerprint'), str) or
            not _FINGERPRINT.fullmatch(metadata['fingerprint'])):
        raise Error(f'Managed source metadata conflicts with the configured source: {source_id}', 4)
    tree = cache / 'tree'
    if tree.is_symlink() or not tree.is_dir() or not (tree / '.git').is_dir() or (tree / '.git').is_symlink():
        raise Error(f'Managed fetched source was removed or redirected: {source_id}', 4)
    try:
        actual = fingerprint(tree)
    except (Error, OSError) as exc:
        raise Error(f'Managed fetched source has invalid local modifications: {source_id}: {exc}', 4) from exc
    if actual != metadata['fingerprint']:
        raise Error(f'Managed fetched source has local modifications: {source_id}', 4)
    head = _git('-C', str(tree), 'rev-parse', '--verify', 'HEAD^{commit}', code=4).stdout.strip()
    status = _git('-C', str(tree), 'status', '--porcelain', '--untracked-files=all', '--ignored', code=4)
    if head != revision or status.stdout.strip():
        raise Error(f'Managed fetched source does not match its locked revision: {source_id}', 4)
    return tree, actual


def _acquire(model, source_id, source, revision):
    cache = _cache_path(model, source_id, source, revision)
    if cache.exists():
        return _check_cache(model, source_id, source, revision, cache)
    _mkdir(cache.parent, model.paths.data)
    temporary = cache.parent / ('.prepare-' + uuid.uuid4().hex)
    temporary.mkdir(mode=0o700)
    try:
        tree = temporary / 'tree'
        resolved = _fetch(tree, source['url'], revision)
        if resolved != revision:
            raise Error(f'Fetched object does not match the exact lock for source {source_id}', 3)
        _git('-C', str(tree), 'checkout', '--quiet', '--detach', '--no-recurse-submodules', revision)
        actual = fingerprint(tree)
        atomic_write(temporary / 'metadata.json', {
            'schema_version': 1, 'source': source_id, 'visibility': source['visibility'],
            'url': source['url'], 'revision': revision, 'fingerprint': actual,
        })
        if cache.exists() or cache.is_symlink():
            raise Error(f'Managed source cache appeared during acquisition: {source_id}', 4)
        temporary.rename(cache)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return _check_cache(model, source_id, source, revision, cache)


def _source(model, source_id, acquire=False, offline=False):
    source = model.sources[source_id]
    if source['type'] == 'directory':
        root = model.source_path(source)
        actual = fingerprint(root)
        dirty, working = _working_state(root)
        return {'root': root, 'fingerprint': actual, 'revision': None,
                'dirty': dirty, 'working_state': working}
    revision = model.locks[source['visibility']]['sources'].get(source_id)
    if revision is None:
        raise Error(f'No exact revision lock exists for selected source: {source_id}', 3)
    cache = _cache_path(model, source_id, source, revision)
    if not cache.exists():
        if not acquire or offline:
            raise Error(f'Exact locked source content is not cached: {source_id} at {revision}', 3)
        root, actual = _acquire(model, source_id, source, revision)
    else:
        root, actual = _check_cache(model, source_id, source, revision, cache)
    return {'root': root, 'fingerprint': actual, 'revision': revision,
            'dirty': False, 'working_state': 'locked'}


def _selection_shape(selection):
    if not isinstance(selection, dict):
        raise Error('Retained selection must be an object')
    for field in ('selected', 'profiles', 'disabled'):
        items = selection.get(field)
        if (not isinstance(items, list) or any(not isinstance(item, str) for item in items) or
                len(items) != len(set(items))):
            raise Error(f'Invalid retained selection {field}')
    reasons, overrides = selection.get('reasons'), selection.get('overrides')
    if not isinstance(reasons, dict) or set(reasons) != set(selection['selected']):
        raise Error('Invalid retained selection reasons')
    for values in reasons.values():
        if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
            raise Error('Invalid retained selection reason list')
    if (not isinstance(overrides, dict) or
            any(not isinstance(key, str) or value not in ('enabled', 'disabled')
                for key, value in overrides.items())):
        raise Error('Invalid retained selection overrides')
    return selection


def _last_good(model):
    document = read_json(model.paths.config / 'last-selection.json', {'schema_version': 1, 'selection': None})
    selection = document.get('selection')
    return None if selection is None else _selection_shape(selection)


def _snapshot_path(model, snapshot, check_store=True):
    scope, directory = snapshot.get('visibility'), snapshot.get('directory')
    if scope not in _SCOPES or not isinstance(directory, str) or not Path(directory).is_absolute():
        raise Error('Invalid active snapshot location')
    root = model.paths.data / scope / 'snapshots'
    path = Path(directory)
    if '..' in path.parts or '\x00' in directory:
        raise Error('Invalid active snapshot path')
    if path == root or not path.is_relative_to(root):
        raise Error('Active snapshot must be inside its scoped snapshot store')
    return _store_path(model.paths, str(path.relative_to(model.paths.data))) if check_store else path


def _active(model):
    manifest_path = _store_path(model.paths, 'active.json')
    document = read_json(manifest_path, {
        'schema_version': 1, 'generation': None, 'selection': None, 'active': [], 'snapshots': [],
    })
    active, snapshots = document.get('active'), document.get('snapshots')
    if not isinstance(active, list) or not isinstance(snapshots, list):
        raise Error('Active manifest requires active and snapshots lists')
    generation = document.get('generation')
    if generation is not None and (not isinstance(generation, str) or not generation):
        raise Error('Invalid active generation')
    if document.get('selection') is not None:
        _selection_shape(document['selection'])
    index = {}
    for snapshot in snapshots:
        if not isinstance(snapshot, dict) or not isinstance(snapshot.get('source'), str):
            raise Error('Invalid active snapshot record')
        _snapshot_path(model, snapshot, check_store=False)
        actual, revision = snapshot.get('fingerprint'), snapshot.get('revision')
        if not isinstance(actual, str) or not _FINGERPRINT.fullmatch(actual):
            raise Error('Invalid active snapshot fingerprint')
        if revision is not None and (not isinstance(revision, str) or not _COMMIT.fullmatch(revision)):
            raise Error('Invalid active snapshot revision')
        key = (snapshot['visibility'], snapshot['source'])
        if key in index:
            raise Error('Duplicate source in active snapshots')
        index[key] = snapshot
    identities = set()
    used = set()
    for entry in active:
        if not isinstance(entry, dict):
            raise Error('Invalid active skill record')
        for field in ('id', 'source', 'path', 'visibility', 'installed_directory'):
            if not isinstance(entry.get(field), str):
                raise Error(f'Active skill record requires {field}')
        if entry['id'] in identities:
            raise Error('Duplicate skill in active manifest')
        identities.add(entry['id'])
        key = (entry['visibility'], entry['source'])
        snapshot = index.get(key)
        if snapshot is None:
            raise Error('Active skill references an unknown snapshot')
        used.add(key)
        relative = Path(entry['path'])
        installed = Path(entry['installed_directory'])
        if not entry['path'] or '\x00' in entry['path'] or relative.is_absolute() or '..' in relative.parts:
            raise Error('Invalid active source-relative skill path')
        if (not installed.is_absolute() or '..' in installed.parts or
                not installed.is_relative_to(Path(snapshot['directory']))):
            raise Error('Active skill directory escapes its snapshot')
        if (entry.get('required_revision') != snapshot['revision'] or
                entry.get('required_fingerprint') != snapshot['fingerprint']):
            raise Error('Active skill requirements disagree with its snapshot')
        if not isinstance(entry.get('reasons'), list) or any(not isinstance(reason, str) for reason in entry['reasons']):
            raise Error('Invalid active selection reasons')
    if used != set(index):
        raise Error('Active manifest includes an unreferenced snapshot')
    if document.get('selection') is not None and set(document['selection']['selected']) != identities:
        raise Error('Active selection does not match active skill membership')
    if identities and (generation is None or document.get('selection') is None):
        raise Error('Active skill membership requires a generation and selection')
    return document


def _check_active_paths(active, skip=()):
    snapshots = {(snapshot['visibility'], snapshot['source']): snapshot for snapshot in active['snapshots']}
    for entry in active['active']:
        key = (entry['visibility'], entry['source'])
        if key in skip:
            continue
        expected = contained(Path(snapshots[key]['directory']), entry['path'])
        if str(expected) != entry['installed_directory']:
            raise Error('Active skill directory does not match its source-relative path')


def _skill_directory(root, skill_id, relative):
    directory = contained(root, relative)
    marker = contained(root, str(Path(relative) / 'SKILL.md'))
    if not directory.is_dir() or not marker.is_file():
        raise Error(f'Selected skill requires a directory with a readable SKILL.md: {skill_id}', 3)
    try:
        with marker.open('rb') as stream:
            stream.read(1)
    except OSError as exc:
        raise Error(f'Selected skill SKILL.md is unreadable: {skill_id}', 3) from exc
    return directory


def _check_snapshot(model, snapshot):
    root = _snapshot_path(model, snapshot)
    metadata_path = root.parent / 'metadata.json'
    if metadata_path.is_symlink() or metadata_path.exists() and not metadata_path.is_file():
        raise Error(f'Generated installation metadata was replaced or redirected: {snapshot["source"]}', 4)
    metadata = read_json(metadata_path, {'schema_version': 1})
    if metadata != {'schema_version': 1, **snapshot}:
        raise Error(f'Generated installation metadata was modified: {snapshot["source"]}', 4)
    if not root.is_dir():
        raise Error(f'Generated installation snapshot was removed: {snapshot["source"]}', 4)
    try:
        actual = fingerprint(root)
    except (Error, OSError) as exc:
        raise Error(f'Generated installation has invalid local modifications: {snapshot["source"]}: {exc}', 4) from exc
    if actual != snapshot['fingerprint']:
        raise Error(f'Generated installation has local modifications: {snapshot["source"]}', 4)


def _snapshot(model, generation, source_id, source, state, previous):
    if (previous is not None and previous['fingerprint'] == state['fingerprint'] and
            previous['revision'] == state['revision']):
        return deepcopy(previous)
    relative = f'{source["visibility"]}/snapshots/{generation}/{_key(source_id)}'
    parent = _store_path(model.paths, relative)
    _mkdir(parent.parent, model.paths.data)
    try:
        parent.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise Error(f'Installation snapshot path already exists: {parent}', 4) from exc
    tree = parent / 'tree'
    try:
        copy_tree(state['root'], tree)
        if fingerprint(tree) != state['fingerprint']:
            raise Error(f'Source changed while preparing installations: {source_id}', 4)
        snapshot = {'source': source_id, 'visibility': source['visibility'], 'directory': str(tree),
                    'fingerprint': state['fingerprint'], 'revision': state['revision']}
        atomic_write(parent / 'metadata.json', {'schema_version': 1, **snapshot})
        return snapshot
    except BaseException:
        # Only this newly allocated, never-activated directory is disposable.
        shutil.rmtree(parent)
        raise


def _membership_diff(desired, previous):
    current = set(desired['selected']) if desired is not None else set()
    before = set(previous['selected']) if previous is not None else set()
    return {'added': sorted(current - before), 'removed': sorted(before - current)}


def sync(model, offline=False):
    """Prepare every selected source and skill before one atomic active-set switch."""
    try:
        model.validate()
        selection = model.selection()
        _last_good(model)  # Validate recovery state before replacing it.
        active = _active(model)
        desired_diff = _membership_diff(selection, active['selection'])
        before_ids = {entry['id'] for entry in active['active']}
        atomic_write(model.paths.config / 'last-selection.json', {'schema_version': 1, 'selection': selection})
        previous = {(entry['visibility'], entry['source']): entry for entry in active['snapshots']}
        for snapshot in active['snapshots']:
            _check_snapshot(model, snapshot)
        _check_active_paths(active)
        source_ids = sorted({model.skills[skill_id]['source'] for skill_id in selection['selected']})
        states = {source_id: _source(model, source_id, acquire=True, offline=offline)
                  for source_id in source_ids}
        for skill_id in selection['selected']:
            skill = model.skills[skill_id]
            _skill_directory(states[skill['source']]['root'], skill_id, skill['path'])
        generation = uuid.uuid4().hex
        snapshots = {}
        for source_id in source_ids:
            source = model.sources[source_id]
            snapshots[source_id] = _snapshot(model, generation, source_id, source, states[source_id],
                                              previous.get((source['visibility'], source_id)))
        records = []
        changed = []
        old_records = {entry['id']: entry for entry in active['active']}
        for skill_id in selection['selected']:
            skill = model.skills[skill_id]
            state = states[skill['source']]
            snapshot = snapshots[skill['source']]
            record = {'id': skill_id, 'source': skill['source'], 'path': skill['path'],
                      'visibility': skill['visibility'], 'reasons': selection['reasons'][skill_id],
                      'required_revision': state['revision'], 'required_fingerprint': state['fingerprint'],
                      'installed_directory': str(contained(Path(snapshot['directory']), skill['path'])),
                      'source_dirty': state['dirty'], 'source_working_state': state['working_state']}
            records.append(record)
            old = old_records.get(skill_id)
            if old is not None and any(old.get(key) != record.get(key) for key in
                                       ('source', 'path', 'required_revision', 'required_fingerprint')):
                changed.append(skill_id)
        for source_id, state in states.items():
            current = _source(model, source_id)
            if current['fingerprint'] != state['fingerprint'] or current['revision'] != state['revision']:
                raise Error(f'Source changed before activation: {source_id}', 4)
        for snapshot in snapshots.values():
            _check_snapshot(model, snapshot)
        if _active(model) != active:
            raise Error('Active installed state changed during preparation', 4)
        manifest = {'schema_version': 1, 'generation': generation, 'selection': selection,
                    'active': records, 'snapshots': list(snapshots.values())}
        if (active['selection'] != selection or active['active'] != records or
                active['snapshots'] != manifest['snapshots'] or active['generation'] is None):
            write_many({model.paths.data / 'active.json': manifest})
        result = inspect(model)
        result['desired_diff'] = desired_diff
        after_ids = set(selection['selected'])
        result['installed_diff'] = {'added': sorted(after_ids - before_ids),
                                    'removed': sorted(before_ids - after_ids), 'changed': changed}
        return result
    except OSError as exc:
        raise Error(f'Cannot prepare or activate the installed set: {exc}', 3) from exc


def inspect(model):
    """Describe desired and active state without fetching or writing any files."""
    errors = []
    selection_valid, desired, last_good = True, None, None
    active = {'schema_version': 1, 'generation': None, 'selection': None, 'active': [], 'snapshots': []}
    try:
        model.validate()
        desired = model.selection()
    except Error as exc:
        selection_valid = False
        errors.append(str(exc))
    try:
        last_good = _last_good(model)
    except (Error, OSError) as exc:
        selection_valid = False
        errors.append(str(exc))
    try:
        active = _active(model)
    except (Error, OSError) as exc:
        selection_valid = False
        errors.append(str(exc))
    snapshot_errors = {}
    for snapshot in active['snapshots']:
        try:
            _check_snapshot(model, snapshot)
        except (Error, OSError) as exc:
            snapshot_errors[(snapshot['visibility'], snapshot['source'])] = str(exc)
            errors.append(str(exc))
            if isinstance(exc, Error) and exc.code == 2:
                selection_valid = False
    try:
        _check_active_paths(active, skip=snapshot_errors)
    except (Error, OSError) as exc:
        selection_valid = False
        errors.append(str(exc))
    active_records = []
    for entry in active['active']:
        record = deepcopy(entry)
        record['availability'] = ('conflict' if (entry['visibility'], entry['source']) in snapshot_errors
                                  else 'installed')
        record['desired'] = desired is not None and entry['id'] in desired['selected']
        active_records.append(record)
    old_records = {entry['id']: entry for entry in active['active']}
    states, source_errors = {}, {}
    if desired is not None:
        for source_id in sorted({model.skills[skill_id]['source'] for skill_id in desired['selected']}):
            try:
                states[source_id] = _source(model, source_id)
            except (Error, OSError) as exc:
                source_errors[source_id] = exc
                errors.append(str(exc))
                if isinstance(exc, Error) and exc.code == 2:
                    selection_valid = False
    selected, changed = [], []
    for skill_id in desired['selected'] if desired is not None else []:
        skill = model.skills[skill_id]
        source = model.sources[skill['source']]
        state = states.get(skill['source'])
        revision = (model.locks[source['visibility']]['sources'].get(skill['source'])
                    if source['type'] == 'git' else None)
        record = {'id': skill_id, 'source': skill['source'], 'path': skill['path'],
                  'visibility': skill['visibility'], 'reasons': desired['reasons'][skill_id],
                  'required_revision': revision,
                  'required_fingerprint': state['fingerprint'] if state is not None else None,
                  'source_dirty': state['dirty'] if state is not None else None,
                  'source_working_state': state['working_state'] if state is not None else 'unavailable',
                  'availability': 'not-installed', 'installed_directory': None}
        old = old_records.get(skill_id)
        failure = source_errors.get(skill['source'])
        snapshot_failure = snapshot_errors.get((skill['visibility'], skill['source']))
        if failure is not None:
            record['availability'] = 'conflict' if isinstance(failure, Error) and failure.code == 4 else 'unavailable'
        elif snapshot_failure is not None:
            record['availability'] = 'conflict'
        elif state is not None:
            try:
                _skill_directory(state['root'], skill_id, skill['path'])
                if old is not None:
                    matches = all(old.get(key) == record.get(key) for key in
                                  ('source', 'path', 'visibility', 'required_revision', 'required_fingerprint'))
                    if matches:
                        record['availability'] = 'installed'
                        record['installed_directory'] = old['installed_directory']
                    else:
                        record['availability'] = 'outdated'
            except (Error, OSError) as exc:
                record['availability'] = 'unavailable'
                errors.append(str(exc))
                if isinstance(exc, Error) and exc.code == 2:
                    selection_valid = False
        if old is not None and record['availability'] != 'installed':
            changed.append(skill_id)
        selected.append(record)
    if not selection_valid:
        # Diagnostics retain active state, but no stale path is a current resolution.
        selected = []
        desired = None
        for record in active_records:
            record['desired'] = None
    desired_ids = set(desired['selected']) if desired is not None else set()
    active_ids = set(old_records)
    return {'schema_version': 1, 'selection_valid': selection_valid,
            'stale': not selection_valid and last_good is not None,
            'desired': desired, 'last_good': last_good, 'selected': selected, 'active': active_records,
            'desired_diff': _membership_diff(desired, active['selection']) if desired is not None else {'added': [], 'removed': []},
            'installed_diff': {'added': sorted(desired_ids - active_ids) if desired is not None else [],
                               'removed': sorted(active_ids - desired_ids) if desired is not None else [],
                               'changed': sorted(changed) if desired is not None else []},
            'errors': errors, 'exposure': 'unmanaged', 'data_directory': str(model.paths.data),
            'generation': active['generation'], 'exit_code': 0 if selection_valid else 2}
