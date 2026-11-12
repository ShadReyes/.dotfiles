"""Explicit, machine-local OMP launch exposure over complete installations.

One atomic pointer publishes links, configuration, and applied state together.
Retained generations support rollback; no shared discovery root is mutated.
"""

import os
import json
from pathlib import Path
import re
import uuid

from . import omp
from .core import Error, atomic_write, valid_id, _fsync_directory, _unique_keys
from .install import (_mkdir, _store_path, _validate_active,
                      exposure_installation, validate_installation)


_GENERATION = re.compile(r'[0-9a-f]{32}\Z')


class RecoveryNeeded(Error):
    def __init__(self, message):
        super().__init__(message, 4)


def _root(model):
    return _store_path(model.paths, 'exposure/omp')


def _identity(model):
    return {key: str(getattr(model.paths, key)) for key in ('repo', 'home', 'data')}


def _generation(value):
    if not isinstance(value, str) or not _GENERATION.fullmatch(value):
        raise Error('Invalid managed exposure generation', 4)
    return value


def _target(root):
    path = root / 'current'
    if not path.is_symlink():
        if path.exists():
            raise Error('Unowned managed exposure entry; original retained', 4)
        return None
    target = os.readlink(path)
    if not target.startswith('generations/'):
        raise Error('Unowned managed exposure link; original retained', 4)
    _generation(target.removeprefix('generations/'))
    return target


def _document(path):
    if path.is_symlink() or not path.is_file():
        raise Error('Managed exposure state was removed or redirected', 4)
    document = json.loads(path.read_text(), object_pairs_hook=_unique_keys)
    if not isinstance(document, dict):
        raise Error('Managed exposure document must be an object', 4)
    return document


def _load(model, target, content=True):
    root = _root(model)
    generation = _generation(target.removeprefix('generations/'))
    directory = _store_path(model.paths, f'exposure/omp/generations/{generation}')
    if not directory.is_dir() or {path.name for path in directory.iterdir()} != {'manifest.json', 'config.json', 'skills'}:
        raise Error('Managed exposure generation is incomplete or modified', 4)
    document = _document(directory / 'manifest.json')
    if (document.get('schema_version') != 1 or
            set(document) != {'schema_version', 'generation', 'identity', 'previous', 'context', 'installation'} or
            document['generation'] != generation or document['identity'] != _identity(model)):
        raise Error('Managed exposure belongs to another checkout/home or was modified', 4)
    if document['previous'] is not None:
        _generation(document['previous'])
        if document['previous'] == generation:
            raise Error('Invalid managed exposure predecessor', 4)
    context = document['context']
    if (not isinstance(context, dict) or
            set(context) != {'version', 'directories', 'cwd', 'profile', 'agent', 'overlays'} or
            any(not isinstance(context[key], str) for key in ('version', 'cwd', 'profile', 'agent', 'overlays')) or
            not isinstance(context['directories'], list) or
            any(not isinstance(value, str) or not value or '\x00' in value for value in context['directories'])):
        raise Error('Invalid managed exposure launch context', 4)
    if any(omp._legacy(omp._path(value), model.paths.repo) for value in context['directories']):
        raise Error('A managed exposure configuration reintroduced the legacy library', 4)
    config = {'skills': {'customDirectories': [*context['directories'], str(directory / 'skills')]}}
    if _document(directory / 'config.json') != config:
        raise Error('Managed exposure configuration was modified', 4)
    active = document['installation']
    if not isinstance(active, dict) or active.get('schema_version') != 1:
        raise Error('Invalid applied installation record', 4)
    _validate_active(model, active)
    skills = directory / 'skills'
    if skills.is_symlink() or not skills.is_dir():
        raise Error('Managed skill root was redirected or removed', 4)
    links = {valid_id(entry['id']): entry['installed_directory'] for entry in active['active']}
    if {path.name for path in skills.iterdir()} != set(links):
        raise Error('Managed exposure membership was modified', 4)
    for identity, installed in links.items():
        path = skills / identity
        if not path.is_symlink() or os.readlink(path) != installed:
            raise Error('Managed skill link was modified; original retained', 4)
    if content:
        validate_installation(model, active)
    return document


def _recovery(root):
    path = root / 'recovery.json'
    if not path.exists() and not path.is_symlink():
        return None
    document = _document(path)
    if document.get('schema_version') != 1 or set(document) != {'schema_version', 'before', 'after'}:
        raise Error('Invalid managed exposure recovery record', 4)
    for value in (document['before'], document['after']):
        if value is not None:
            if not isinstance(value, str) or not value.startswith('generations/'):
                raise Error('Invalid recovery target', 4)
            _generation(value.removeprefix('generations/'))
    return document


def _current(model):
    try:
        root = _root(model)
        if _recovery(root) is not None:
            raise Error('Owned publication needs explicit rollback', 4)
        target = _target(root)
        return target, _load(model, target) if target is not None else None
    except (Error, OSError, ValueError, TypeError, KeyError) as exc:
        raise RecoveryNeeded('Managed OMP state needs recovery; no route was overwritten') from exc


def _flip(root, target, expected):
    if _target(root) != expected:
        raise Error('Managed exposure changed before publication', 4)
    temporary = root / ('.next-' + uuid.uuid4().hex)
    try:
        if target is None:
            if expected is not None:
                (root / 'current').unlink()
        else:
            temporary.symlink_to(target, target_is_directory=True)
            os.replace(temporary, root / 'current')
        _fsync_directory(root)
    finally:
        temporary.unlink(missing_ok=True)


def _publish(root, target, before):
    try:
        _flip(root, target, before)
    except OSError as exc:
        try:
            actual = _target(root)
            if actual != before:
                if actual != target:
                    raise Error('Publication ownership changed', 4)
                _flip(root, before, actual)
        except (Error, OSError):
            atomic_write(root / 'recovery.json', {'schema_version': 1, 'before': before, 'after': target})
            raise RecoveryNeeded('Publication rollback could not be verified; explicit rollback required') from exc
        raise Error('Exposure publication failed; previous route restored', 3) from exc


def _result(model, status, document=None):
    result = {'target': 'omp', 'status': status, 'scope': 'explicit-overlay',
              'default_discovery': 'unchanged', 'loaded_in_session': False,
              'count': len(document['installation']['active']) if document else 0}
    if document is not None:
        config = _root(model) / 'current/config.json'
        result.update(generation=document['generation'], installation_generation=document['installation']['generation'],
                      config=str(config), refresh='Start a new OMP session with the supplied --config overlay; existing sessions are not reloaded.',
                      launch=['omp', '--cwd', document['context']['cwd'], '--profile',
                              document['context']['profile'].strip() or 'default', '--config', str(config)])
    return result


def apply(model):
    before, previous = _current(model)
    active = exposure_installation(model)
    root = _root(model)
    previous_skills = root / before / 'skills' if before else None
    context = omp.configuration(model, previous_skills)
    if previous is not None and previous['installation'] == active and previous['context'] == context:
        omp.verify(root / before / 'config.json', active, model.paths.repo)
        return _result(model, 'unchanged', previous)
    _mkdir(root / 'generations', model.paths.data)
    generation = uuid.uuid4().hex
    directory = root / 'generations' / generation
    directory.mkdir(mode=0o700)
    skills = directory / 'skills'
    skills.mkdir(mode=0o700)
    for entry in active['active']:
        identity = valid_id(entry['id'])
        (skills / identity).symlink_to(entry['installed_directory'], target_is_directory=True)
    document = {'schema_version': 1, 'generation': generation, 'identity': _identity(model),
                'previous': previous['generation'] if previous else None, 'context': context,
                'installation': active}
    atomic_write(directory / 'config.json', {
        'skills': {'customDirectories': [*context['directories'], str(skills)]},
    })
    atomic_write(directory / 'manifest.json', document)
    _fsync_directory(skills)
    _fsync_directory(directory)
    _fsync_directory(directory.parent)
    candidate = 'generations/' + generation
    _load(model, candidate)
    omp.verify(directory / 'config.json', active, model.paths.repo)
    if exposure_installation(model) != active or omp.configuration(model, previous_skills) != context:
        raise Error('Installation or OMP launch context changed during preparation', 4)
    _publish(root, candidate, before)
    return _result(model, 'applied', document)


def rollback(model):
    root = _root(model)
    recovery = _recovery(root)
    before = _target(root)
    if recovery is not None:
        if before not in (recovery['before'], recovery['after']):
            raise RecoveryNeeded('Recovery ownership changed; unowned route retained')
        target = recovery['before']
    elif before is None:
        return _result(model, 'unchanged')
    else:
        previous = _load(model, before, content=False)['previous']
        target = 'generations/' + previous if previous else None
    document = _load(model, target) if target else None
    if document is not None:
        previous_skills = root / before / 'skills' if before else None
        context = omp.configuration(model, previous_skills)
        if context != document['context']:
            raise Error('OMP launch context changed; retained exposure cannot be safely restored', 4)
        omp.verify(root / target / 'config.json', document['installation'], model.paths.repo)
        _load(model, target)
        if omp.configuration(model, previous_skills) != context:
            raise Error('OMP launch context changed during rollback preparation', 4)
    if target != before:
        _publish(root, target, before)
    if recovery is not None:
        (root / 'recovery.json').unlink()
        _fsync_directory(root)
    return _result(model, 'rolled-back', document)


def status(model):
    _, document = _current(model)
    if document is None:
        return _result(model, 'unchanged')
    result = _result(model, 'applied', document)
    try:
        active = exposure_installation(model)
        if active != document['installation']:
            result['status'] = 'pending'
    except Error:
        result['status'] = 'pending'
    return result


def run(model, action, targets):
    results, code = [], 0
    for target in dict.fromkeys(targets):
        if target != 'omp':
            results.append({'target': target, 'status': 'unsupported', 'loaded_in_session': False})
            code = max(code, 3)
            continue
        try:
            results.append({'apply': apply, 'rollback': rollback, 'status': status}[action](model))
        except RecoveryNeeded as exc:
            results.append({'target': target, 'status': 'recovery-needed', 'error': str(exc)})
            code = max(code, exc.code)
        except Error as exc:
            results.append({'target': target, 'status': 'unsupported' if isinstance(exc, omp.Unsupported) else 'pending', 'error': str(exc)})
            code = max(code, exc.code)
        except (OSError, ValueError, TypeError, KeyError) as exc:
            results.append({'target': target, 'status': 'recovery-needed', 'error': 'Managed exposure cannot be safely inspected or restored'})
            code = max(code, 4)
    return {'schema_version': 1, 'targets': results, 'exit_code': code}
