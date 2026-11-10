"""Reviewed local imports and recoverable, discovery-preserving private relocation."""

import base64
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib
import uuid

from .core import (Error, Model, atomic_write, contained, copy_tree, fingerprint,
                   private_directory, read_json, valid_id, write_many)


_HARNESSES = ('.claude', '.agents', '.codex', '.pi/agent', '.omp',
              '.config/omp', '.config/opencode')
_MAX_CONFIG = 1024 * 1024


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _file_state(path):
    if path.is_symlink():
        return {'link': os.readlink(path), 'resolved': str(path.resolve()),
                'content': hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None}
    if not path.exists():
        return None
    if not path.is_file():
        raise Error(f'Expected a regular configuration file: {path}')
    return {'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def _git(paths, *arguments, required=False):
    result = subprocess.run(['git', '-C', str(paths.repo), *arguments],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode and required:
        raise Error('Private migration requires a working dotfiles Git checkout', 4)
    return result


def _exclude_path(paths):
    result = _git(paths, 'rev-parse', '--git-path', 'info/exclude')
    if result.returncode:
        return None
    path = Path(os.fsdecode(result.stdout).strip())
    return path if path.is_absolute() else paths.repo / path


def _configuration(paths):
    files = [root / name for root in (paths.shared, paths.config)
             for name in ('catalog.json', 'profiles.json', 'lock.json')]
    files += [paths.config / 'machine.json', paths.config / 'last-selection.json',
              paths.repo / 'sync-skills.sh', paths.repo / '.gitignore']
    exclude = _exclude_path(paths)
    if exclude is not None:
        files.append(exclude)
    return {str(path): _file_state(path) for path in files}


def _skills(root):
    found = []
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(name for name in dirs if name != '.git')
        if 'SKILL.md' in files:
            path = Path(directory)
            if not (path / 'SKILL.md').is_file():
                raise Error('Discovered SKILL.md must be a regular file')
            found.append(path.relative_to(root).as_posix())
    return sorted(found)


def _inventory(paths):
    root = paths.repo / 'skills'
    if not root.exists():
        return []
    if root.is_symlink() or not root.is_dir():
        raise Error('The legacy skills root must be a real repository directory')
    inventory = []
    for source in sorted(root.iterdir()):
        if source.name.startswith('.') or not source.is_dir():
            continue
        skills = _skills(source)
        if not skills:
            continue
        relative = source.relative_to(paths.repo).as_posix()
        tracked = _git(paths, 'ls-files', '-z', '--', relative)
        inventory.append({'path': relative, 'fingerprint': fingerprint(source),
                          'skills': skills, 'link': os.readlink(source) if source.is_symlink() else None,
                          'tracked': bool(tracked.stdout) if not tracked.returncode else None})
    return inventory


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _strings(child)


def _references(paths, inventory):
    sources = {item['path']: paths.repo / item['path'] for item in inventory}
    references = []
    for relative_root in _HARNESSES:
        root = paths.home / relative_root
        if root.is_symlink():
            target = root.resolve()
            affected = sorted(key for key, source in sources.items()
                              if target == source.resolve() or target.is_relative_to(source.resolve()))
            if affected:
                references.append({'kind': 'symlink', 'path': str(root),
                                   'target': os.readlink(root), 'resolved': str(target),
                                   'sources': affected})
        if not root.is_dir():
            continue
        for directory, dirs, files in os.walk(root, followlinks=False):
            current = Path(directory)
            depth = len(current.relative_to(root).parts)
            names = sorted(dirs + files)
            dirs[:] = [name for name in dirs if name not in
                       ('sessions', 'projects', 'history', 'logs', 'cache', '.git')
                       and not (current / name).is_symlink()
                       and depth < 3 and current.name != 'skills']
            for name in names:
                path = current / name
                if path.is_symlink():
                    target = path.resolve()
                    affected = sorted(key for key, source in sources.items()
                                      if target == source.resolve() or target.is_relative_to(source.resolve()))
                    if affected:
                        references.append({'kind': 'symlink', 'path': str(path),
                                           'target': os.readlink(path), 'resolved': str(target),
                                           'sources': affected})
                    continue
                if not path.is_file() or current.name == 'skills' or path.stat().st_size > _MAX_CONFIG:
                    continue
                try:
                    text = path.read_text()
                except UnicodeError:
                    continue
                value, configuration_format = None, 'unsupported'
                try:
                    if path.suffix == '.json':
                        value, configuration_format = json.loads(text), 'json'
                    elif path.suffix == '.toml':
                        value, configuration_format = tomllib.loads(text), 'toml'
                except ValueError:
                    pass
                searchable = text + '\n' + '\n'.join(_strings(value))
                needles = {}
                for key, source in sources.items():
                    forms = [str(source), key]
                    if source.is_relative_to(paths.home):
                        forms.append('~/' + source.relative_to(paths.home).as_posix())
                    if any(form in searchable for form in forms):
                        needles[key] = forms
                if not needles:
                    continue
                reference = {'kind': 'configuration', 'path': str(path),
                             'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                             'sources': sorted(needles), 'format': 'unsupported', 'paths': []}
                try:
                    reference['format'] = configuration_format
                    if configuration_format == 'unsupported':
                        raise ValueError('Unknown configuration format')
                    for string in _strings(value):
                        matching = [key for key, forms in needles.items()
                                    if any(form in string for form in forms)]
                        if not matching:
                            continue
                        candidate = Path(string).expanduser() if not string.startswith('~/') else paths.home / string[2:]
                        if not candidate.is_absolute() or not any(
                                candidate.resolve() == sources[key].resolve() or
                                candidate.resolve().is_relative_to(sources[key].resolve())
                                for key in matching):
                            raise ValueError('Cannot safely interpret a configuration reference')
                        reference['paths'].append(str(candidate))
                    if not reference['paths']:
                        raise ValueError('Reference is not a structured path value')
                    reference['paths'] = sorted(set(reference['paths']))
                except (ValueError, tomllib.TOMLDecodeError):
                    reference['format'] = 'unsupported'
                references.append(reference)
    return sorted(references, key=lambda reference: reference['path'])


def plan(model):
    """Inventory only; every source requires explicit local classification and IDs."""
    model.validate(selection=False)
    paths = model.paths
    inventory = _inventory(paths)
    document = {
        'schema_version': 1, 'kind': 'skillset-import', 'id': uuid.uuid4().hex,
        'repository': str(paths.repo), 'home': str(paths.home), 'data': str(paths.data),
        'inventory': inventory, 'configuration': _configuration(paths),
        'references': _references(paths, inventory),
        'reference_scan': {'roots': list(_HARNESSES), 'maximum_depth': 4,
                           'maximum_file_bytes': _MAX_CONFIG,
                           'excluded_directories': ['sessions', 'projects', 'history', 'logs', 'cache', '.git'],
                           'follows_directory_links': False},
        'instructions': [
            'Review only entries; inventory, configuration and references are change guards.',
            'Set classification to shared or private, source_id, provenance (authored or third-party), and every skill id.',
            'Optional upstream and upstream_name preserve known attribution; no upstream is inferred.',
            'Private relocation requires private_approved: true; tracked private content is refused.',
            'Existing path aliases preserve discovery; affected unsupported configuration formats block relocation.',
        ],
        'entries': [{'path': item['path'], 'classification': 'unclassified',
                     'source_id': None, 'provenance': None, 'private_approved': False,
                     'skills': [{'path': relative, 'id': None} for relative in item['skills']]}
                    for item in inventory],
    }
    destination = contained(paths.data, 'plans/' + document['id'] + '.json')
    atomic_write(destination, document)
    return {'plan': str(destination), 'unclassified': len(inventory)}


def _assert_current(paths, snapshot):
    inventory = _inventory(paths)
    if inventory != snapshot.get('inventory'):
        raise Error('Import inventory or source content changed; prepare a new plan', 4)
    if _configuration(paths) != snapshot.get('configuration'):
        raise Error('Import configuration changed; prepare a new plan', 4)
    if _references(paths, inventory) != snapshot.get('references'):
        raise Error('Import discovery references changed; prepare a new plan', 4)


def _proposal(model, document):
    entries = document.get('entries')
    inventory = {item['path']: item for item in document['inventory']}
    if not isinstance(entries, list) or any(not isinstance(entry, dict) or
            not isinstance(entry.get('path'), str) for entry in entries):
        raise Error('Import entries must be a list of reviewed source paths')
    if len(entries) != len(inventory) or {entry.get('path') for entry in entries} != set(inventory):
        raise Error('Reviewed entries must exactly match discovered source directories')
    candidate = deepcopy(model)
    source_ids, skill_ids = set(), set()
    relocations = []
    touched = set()
    for entry in entries:
        scope = entry.get('classification')
        if scope not in ('shared', 'private'):
            raise Error('Every discovered source requires explicit shared or private classification')
        source_id = valid_id(entry.get('source_id'))
        if source_id in source_ids:
            raise Error(f'Duplicate reviewed source identity: {source_id}')
        source_ids.add(source_id)
        if entry.get('provenance') not in ('authored', 'third-party'):
            raise Error('Every imported source requires explicit authored or third-party provenance')
        item = inventory[entry['path']]
        original = model.paths.repo / entry['path']
        if scope == 'shared':
            if not original.resolve().is_relative_to(model.paths.repo) or original.resolve() == model.paths.repo:
                raise Error('Shared import requires a dedicated, repository-contained source directory')
            source_path = entry['path']
        existing_source = model.sources.get(source_id)
        if existing_source is not None:
            if (existing_source['visibility'] != scope or existing_source.get('type') != 'directory' or
                    existing_source.get('provenance') != entry['provenance'] or
                    model.source_path(existing_source) != original.resolve() or
                    ('upstream' in entry and entry['upstream'] != existing_source.get('upstream'))):
                raise Error(f'Import cannot overwrite source identity: {source_id}')
        elif scope == 'private':
            if entry.get('private_approved') is not True:
                raise Error('Private relocation requires explicit private_approved: true')
            if item['tracked'] is not False:
                raise Error('Refusing tracked private content; relocation cannot erase Git history', 4)
            if original.is_symlink():
                raise Error('Private import requires an original directory, not an already relocated alias', 4)
            for reference in document['references']:
                if entry['path'] in reference['sources'] and reference.get('format') == 'unsupported':
                    raise Error('Affected configuration format cannot be safely verified; original retained', 4)
            source_path = str(contained(model.paths.data, 'private/originals/' + source_id))
            recovery = contained(model.paths.data, 'private/recovery/' + document['id'] + '/' + source_id)
            relocations.append({'original': str(original), 'destination': source_path,
                                'recovery': str(recovery),
                                'retired': str(original.parent / ('.skillset-retired-' + document['id'] + '-' + source_id)),
                                'fingerprint': item['fingerprint']})
        if existing_source is None:
            source = {'type': 'directory', 'path': source_path, 'provenance': entry['provenance']}
            if 'upstream' in entry:
                source['upstream'] = entry['upstream']
            candidate.catalogs[scope]['sources'][source_id] = source
            touched.add(scope)
        skills = entry.get('skills')
        if not isinstance(skills, list) or any(not isinstance(skill, dict) or
                not isinstance(skill.get('path'), str) for skill in skills):
            raise Error('Reviewed skills must be a list of source-relative paths')
        if len(skills) != len(item['skills']) or {skill.get('path') for skill in skills} != set(item['skills']):
            raise Error('Reviewed skills must exactly match discovered SKILL.md directories')
        for skill in skills:
            skill_id = valid_id(skill.get('id'))
            if skill_id in skill_ids:
                raise Error(f'Duplicate reviewed skill identity: {skill_id}')
            skill_ids.add(skill_id)
            existing_skill = model.skills.get(skill_id)
            if existing_skill is not None:
                if (existing_skill['visibility'] != scope or existing_skill.get('source') != source_id or
                        existing_skill.get('path') != skill['path'] or
                        ('upstream_name' in skill and skill['upstream_name'] != existing_skill.get('upstream_name'))):
                    raise Error(f'Import cannot overwrite skill identity: {skill_id}')
            else:
                record = {'source': source_id, 'path': skill['path']}
                if 'upstream_name' in skill:
                    record['upstream_name'] = skill['upstream_name']
                candidate.catalogs[scope]['skills'][skill_id] = record
                touched.add(scope)
    candidate.validate(selection=False)
    documents = {(model.paths.shared if scope == 'shared' else model.paths.config) / 'catalog.json':
                 candidate.catalogs[scope] for scope in touched}
    return documents, relocations


def _ensure_copy(source, destination, expected):
    private_directory(destination.parent)
    if destination.exists() or destination.is_symlink():
        if destination.is_symlink() or fingerprint(destination) != expected:
            raise Error('Retained migration copy conflicts with reviewed source; original retained', 4)
        return
    temporary = destination.parent / ('.copy-' + uuid.uuid4().hex)
    try:
        copy_tree(source, temporary)
        if fingerprint(temporary) != expected:
            raise Error('Source changed while retaining migration recovery; original retained', 4)
        temporary.rename(destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def _raw_write(path, content):
    if path.is_symlink():
        raise Error('Refusing to overwrite a symlinked migration state file', 4)
    private_directory(path.parent)
    fd, filename = tempfile.mkstemp(prefix='.migration-', dir=path.parent)
    temporary = Path(filename)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _saved_file(path, new_bytes):
    if path.is_symlink():
        raise Error('Refusing to replace symlinked migration configuration', 4)
    return {'path': str(path), 'before': base64.b64encode(path.read_bytes()).decode() if path.exists() else None,
            'after': base64.b64encode(new_bytes).decode()}


def _restore(journal):
    # Never overwrite concurrent edits during recovery; verified copies remain local.
    for record in reversed(journal['files']):
        path = Path(record['path'])
        before = base64.b64decode(record['before']) if record['before'] is not None else None
        after = base64.b64decode(record['after'])
        current = path.read_bytes() if path.exists() and not path.is_symlink() else None
        if current == before:
            continue
        if path.is_symlink() or current != after:
            raise Error('Migration rollback found independently changed configuration; recovery retained', 4)
        if before is None:
            path.unlink(missing_ok=True)
        else:
            _raw_write(path, before)
    for relocation in reversed(journal['relocations']):
        original, retired = Path(relocation['original']), Path(relocation['retired'])
        destination, recovery = Path(relocation['destination']), Path(relocation['recovery'])
        if original.is_dir() and not original.is_symlink():
            if fingerprint(original) != relocation['fingerprint']:
                raise Error('Original changed during migration recovery; retained copies are available', 4)
            continue
        if original.is_symlink() and original.resolve() != destination.resolve():
            raise Error('Original alias changed independently; recovery retained', 4)
        if original.exists() and not original.is_symlink():
            raise Error('Original path conflicts with migration recovery', 4)
        if not retired.exists():
            _ensure_copy(recovery, retired, relocation['fingerprint'])
        if fingerprint(retired) != relocation['fingerprint']:
            raise Error('Retired original changed; recovery retained', 4)
        if original.is_symlink():
            original.unlink()
        retired.rename(original)


def _verify_discovery(paths, references, relocations):
    for relocation in relocations:
        original, destination = Path(relocation['original']), Path(relocation['destination'])
        if not original.is_symlink() or original.resolve() != destination.resolve():
            raise Error('Relocated source alias failed discovery verification', 4)
        if fingerprint(original) != relocation['fingerprint']:
            raise Error('Relocated source contents failed verification', 4)
    private_paths = {str(Path(item['original']).relative_to(paths.repo)) for item in relocations}
    for reference in references:
        if not private_paths.intersection(reference['sources']):
            continue
        path = Path(reference['path'])
        if reference['kind'] == 'symlink':
            if not path.is_symlink() or os.readlink(path) != reference['target'] or not path.exists():
                raise Error('Existing discovery link failed verification; original retained', 4)
        elif reference['format'] in ('json', 'toml'):
            if hashlib.sha256(path.read_bytes()).hexdigest() != reference['sha256']:
                raise Error('Affected configuration changed during migration', 4)
            if any(not Path(value).exists() for value in reference['paths']):
                raise Error('Affected configuration path cannot be verified; original retained', 4)
        else:
            raise Error('Affected configuration format cannot be verified', 4)


def _exclusion(paths, relocations):
    if not relocations:
        return None
    top = _git(paths, 'rev-parse', '--show-toplevel', required=True)
    if Path(os.fsdecode(top.stdout).strip()).resolve() != paths.repo:
        raise Error('Private migration requires dotfiles to be its Git checkout root', 4)
    exclude = _exclude_path(paths)
    if exclude is None or exclude.is_symlink():
        raise Error('Private migration requires a regular Git-local exclude file', 4)
    content = exclude.read_bytes() if exclude.exists() else b''
    additions = []
    for relocation in relocations:
        for field in ('original', 'retired'):
            relative = Path(relocation[field]).relative_to(paths.repo).as_posix()
            if '\n' in relative or '\r' in relative:
                raise Error('Private source path cannot be safely represented in Git-local excludes')
            # Directory-only ignore rules stop matching after replacement by a symlink.
            # Also keep the temporary retired directory out of accidental Git staging.
            escaped = ''.join('\\' + char if char in '\\*?[]#! ' else char for char in relative)
            rule = '/' + escaped
            if rule.encode() not in content.splitlines():
                additions.append(rule + '\n')
    if not additions:
        return None
    return _saved_file(exclude, content + (b'\n' if content and not content.endswith(b'\n') else b'') +
                       ''.join(additions).encode())


def apply(model, plan_path):
    """Apply one named reviewed plan under the caller's mutation lock."""
    paths = model.paths
    plan_path = Path(plan_path).resolve()
    if plan_path.is_relative_to(paths.repo):
        raise Error('Import plans containing private details must remain outside dotfiles')
    document = read_json(plan_path, {})
    if document.get('kind') != 'skillset-import' or any(document.get(key) != str(value)
            for key, value in (('repository', paths.repo), ('home', paths.home), ('data', paths.data))):
        raise Error('Import plan does not belong to this checkout and machine')
    identifier = document.get('id')
    if not isinstance(identifier, str) or len(identifier) != 32 or any(char not in '0123456789abcdef' for char in identifier):
        raise Error('Import plan has an invalid identity')
    plans_directory = contained(paths.data, 'plans')
    private_directory(plans_directory)
    receipt_path = plans_directory / (identifier + '.applied.json')
    journal_path = plans_directory / (identifier + '.journal.json')
    review_digest = _digest(document)
    if receipt_path.exists():
        receipt = read_json(receipt_path, {})
        if receipt.get('review_digest') != review_digest:
            raise Error('Applied import plan changed; prepare a new plan', 4)
        _assert_current(paths, receipt)
        return receipt['result']
    if journal_path.exists():
        journal = read_json(journal_path, {})
        if journal.get('review_digest') != review_digest:
            raise Error('Interrupted import has a different review; recover using its original plan', 4)
        _restore(journal)
        journal_path.unlink()
        model = Model(paths)
    model.validate(selection=False)
    _assert_current(paths, document)
    documents, relocations = _proposal(model, document)
    exclusion = _exclusion(paths, relocations)
    for relocation in relocations:
        original = Path(relocation['original'])
        _ensure_copy(original, Path(relocation['recovery']), relocation['fingerprint'])
        _ensure_copy(original, Path(relocation['destination']), relocation['fingerprint'])
        if Path(relocation['retired']).exists() or Path(relocation['retired']).is_symlink():
            raise Error('Retired migration path already exists; original retained', 4)
    # Recheck after potentially slow copies and before publishing any changes.
    _assert_current(paths, document)
    files = [_saved_file(path, (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n').encode())
             for path, value in documents.items()]
    if exclusion:
        files.append(exclusion)
    journal = {'schema_version': 1, 'review_digest': review_digest,
               'files': files, 'relocations': relocations}
    atomic_write(journal_path, journal)
    try:
        if exclusion:
            _raw_write(Path(exclusion['path']), base64.b64decode(exclusion['after']))
        for relocation in relocations:
            original, retired = Path(relocation['original']), Path(relocation['retired'])
            original.rename(retired)
            original.symlink_to(relocation['destination'], target_is_directory=True)
        _verify_discovery(paths, document['references'], relocations)
        for relocation in relocations:
            if _git(paths, 'check-ignore', '-q', '--', relocation['original']).returncode:
                raise Error('Private source alias is not Git-excluded; original retained', 4)
        write_many(documents)
        Model(paths).validate(selection=False)
        for relocation in relocations:
            retired = Path(relocation['retired'])
            if fingerprint(retired) != relocation['fingerprint']:
                raise Error('Retired original changed; verified recovery retained', 4)
            shutil.rmtree(retired)
        _verify_discovery(paths, document['references'], relocations)
        result = {'sources': len(document['entries']),
                  'skills': sum(len(entry['skills']) for entry in document['entries']),
                  'recovery': [entry['recovery'] for entry in relocations]}
        inventory = _inventory(paths)
        receipt = {'schema_version': 1, 'review_digest': review_digest,
                   'inventory': inventory, 'configuration': _configuration(paths),
                   'references': _references(paths, inventory), 'result': result}
        atomic_write(receipt_path, receipt)
    except BaseException:
        receipt_path.unlink(missing_ok=True)
        _restore(journal)
        journal_path.unlink(missing_ok=True)
        raise
    journal_path.unlink(missing_ok=True)
    return result
