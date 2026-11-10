"""Validated configuration and local selection; no acquisition or harness discovery."""

from contextlib import contextmanager
from copy import deepcopy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile


class Error(Exception):
    def __init__(self, message, code=2):
        super().__init__(message)
        self.code = code


def private_directory(path):
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.chmod(0o700)


class Paths:
    def __init__(self, repo, home=None):
        self.repo = Path(repo).resolve()
        self.home = Path(home or Path.home()).resolve()
        self.shared = self.repo / 'skillset'
        self.config = self._xdg('XDG_CONFIG_HOME', self.home / '.config') / 'skillset'
        self.data = self._xdg('XDG_DATA_HOME', self.home / '.local/share') / 'skillset'
        discovery = [self.home / p for p in (
            '.claude/skills', '.agents/skills', '.codex/skills', '.pi/agent/skills',
            '.omp/skills', '.config/omp/skills', '.config/opencode/skills', '.hermes/skills',
        )]
        for root in (self.config, self.data):
            if root.is_relative_to(self.repo) or any(root.is_relative_to(p.resolve()) for p in discovery):
                raise Error('Local Skillset roots must be outside dotfiles and harness discovery roots')
        if self.config == self.data or self.config.is_relative_to(self.data) or self.data.is_relative_to(self.config):
            raise Error('Configuration and data roots must be separate')

    @staticmethod
    def _xdg(key, fallback):
        path = Path(os.environ.get(key) or fallback).expanduser()
        if not path.is_absolute():
            raise Error(f'{key} must be absolute')
        return path.resolve()


def read_json(path, default):
    try:
        value = json.loads(path.read_text(), object_pairs_hook=_unique_keys)
    except FileNotFoundError:
        return deepcopy(default)
    except (ValueError, UnicodeError) as exc:
        raise Error(f'Invalid JSON in {path}: {exc}') from exc
    if not isinstance(value, dict) or type(value.get('schema_version')) is not int or value['schema_version'] != 1:
        raise Error(f'Unsupported or missing schema_version in {path}')
    return value


def _unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate key: {key}')
        result[key] = value
    return result


def _stage(path, value):
    private_directory(path.parent)
    if path.is_symlink():
        raise Error(f'Refusing to replace symlinked state file: {path}', 4)
    fd, filename = tempfile.mkstemp(prefix='.skillset-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        Path(filename).unlink(missing_ok=True)
        raise
    return Path(filename)


def _publish(staged, path):
    os.replace(staged, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_write(path, value):
    staged = _stage(path, value)
    try:
        _publish(staged, path)
    finally:
        staged.unlink(missing_ok=True)


def write_many(documents):
    """Prepare every document before publishing; rollback ordinary publication failures."""
    staged, originals, published = {}, {}, []
    try:
        for path, value in documents.items():
            originals[path] = path.read_bytes() if path.exists() else None
            staged[path] = _stage(path, value)
        for path, temporary in staged.items():
            published.append(path)
            _publish(temporary, path)
    except BaseException:
        for path in reversed(published):
            if originals[path] is None:
                path.unlink(missing_ok=True)
            else:
                fd, filename = tempfile.mkstemp(prefix='.rollback-', dir=path.parent)
                with os.fdopen(fd, 'wb') as stream:
                    stream.write(originals[path])
                    stream.flush()
                    os.fsync(stream.fileno())
                _publish(Path(filename), path)
        raise
    finally:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)


@contextmanager
def locked(paths):
    """A repo lock also serializes distinct homes sharing the same checkout."""
    descriptors = []
    try:
        for directory in (paths.shared, paths.config):
            private_directory(directory)
            lock = directory / '.mutation.lock'
            if lock.is_symlink():
                raise Error('Refusing symlinked mutation lock', 4)
            fd = os.open(lock, os.O_CREAT | os.O_RDWR, 0o600)
            descriptors.append(fd)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise Error('Another Skillset mutation is in progress', 4) from exc
        yield
    finally:
        for fd in reversed(descriptors):
            os.close(fd)


def contained(root, relative):
    if not isinstance(relative, str) or not relative or '\x00' in relative:
        raise Error('Source-relative path must be a nonempty string')
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts:
        raise Error('Source-relative paths cannot be absolute or traverse parents')
    root = root.resolve()
    result = (root / path).resolve()
    if not result.is_relative_to(root):
        raise Error('Source-relative path escapes its declared source')
    return result


def fingerprint(root):
    root = root.resolve()
    if not root.is_dir():
        raise Error(f'Source directory is unavailable: {root}', 3)
    digest = hashlib.sha256()
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d != '.git')
        for name in sorted(dirs + [f for f in files if f != '.git']):
            path = Path(directory) / name
            relative = path.relative_to(root).as_posix()
            info = path.lstat()
            digest.update(relative.encode() + b'\0')
            if path.is_symlink():
                if not path.resolve().is_relative_to(root):
                    raise Error(f'Source link escapes its declared root: {relative}')
                digest.update(b'L' + os.readlink(path).encode() + b'\0')
            elif stat.S_ISDIR(info.st_mode):
                digest.update(b'D\0')
            elif stat.S_ISREG(info.st_mode):
                digest.update(b'F' + str(info.st_mode & 0o111).encode() + b'\0')
                with path.open('rb') as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b''):
                        digest.update(block)
                digest.update(b'\0')
            else:
                raise Error(f'Unsupported filesystem object in source: {relative}')
    return digest.hexdigest()


def copy_tree(source, dest):
    before = fingerprint(source)
    shutil.copytree(source, dest, symlinks=True, ignore=shutil.ignore_patterns('.git'))
    if fingerprint(source) != before or fingerprint(dest) != before:
        raise Error('Source changed while preparing a snapshot; original retained', 4)


def valid_id(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:-]*', value):
        raise Error('IDs must start with an alphanumeric character and contain only letters, digits, dot, underscore, colon or hyphen')
    return value


def _mapping(doc, name):
    value = doc.get(name)
    if not isinstance(value, dict):
        raise Error(f'{name} must be an object')
    for key, record in value.items():
        valid_id(key)
        if not isinstance(record, dict):
            raise Error(f'{name} entries must be objects')
    return value


def _ids(value, label):
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise Error(f'{label} must be a list of IDs')
    for item in value:
        valid_id(item)
    if len(set(value)) != len(value):
        raise Error(f'{label} contains duplicate IDs')
    return value


class Model:
    def __init__(self, paths, shared_only=False):
        self.paths = paths
        self.shared_only = shared_only
        self.catalogs, self.profile_docs, self.locks = {}, {}, {}
        for scope, root in [('shared', paths.shared)] + ([] if shared_only else [('private', paths.config)]):
            self.catalogs[scope] = read_json(root / 'catalog.json', {'schema_version': 1, 'sources': {}, 'skills': {}})
            self.profile_docs[scope] = read_json(root / 'profiles.json', {'schema_version': 1, 'profiles': {}})
            self.locks[scope] = read_json(root / 'lock.json', {'schema_version': 1, 'sources': {}})
        self.machine = ({'schema_version': 1, 'profiles': [], 'overrides': {}} if shared_only else
                        read_json(paths.config / 'machine.json', {'schema_version': 1, 'profiles': [], 'overrides': {}}))
        self.sources = self._merge(self.catalogs, 'sources')
        self.skills = self._merge(self.catalogs, 'skills')
        self.profiles = self._merge(self.profile_docs, 'profiles')

    @staticmethod
    def _merge(documents, name):
        combined = {}
        for scope, doc in documents.items():
            for key, record in _mapping(doc, name).items():
                if key in combined:
                    raise Error(f'Duplicate {name} identity across catalogs: {key}')
                combined[key] = {**record, 'visibility': scope}
        return combined

    def source_path(self, source):
        path = source.get('path')
        if not isinstance(path, str) or not path or '\x00' in path:
            raise Error('Directory source requires a path')
        if source['visibility'] == 'shared':
            result = contained(self.paths.repo, path)
            if result == self.paths.repo:
                raise Error('Declare a dedicated source directory, not the entire dotfiles checkout')
            return result
        result = Path(path).expanduser()
        if not result.is_absolute():
            raise Error('Private directory source paths must be absolute')
        result = result.resolve()
        if result.is_relative_to(self.paths.repo):
            raise Error('Private source contents must live outside dotfiles; use an approved import plan')
        return result

    def validate(self, selection=True):
        self.sources = self._merge(self.catalogs, 'sources')
        self.skills = self._merge(self.catalogs, 'skills')
        self.profiles = self._merge(self.profile_docs, 'profiles')
        for source in self.sources.values():
            if source.get('provenance') not in ('authored', 'third-party'):
                raise Error('Source provenance must be authored or third-party')
            if source.get('upstream') is not None and not isinstance(source['upstream'], str):
                raise Error('Source upstream must be a string')
            if source.get('type') == 'directory':
                self.source_path(source)
            elif source.get('type') == 'git':
                for key in ('url', 'ref'):
                    if not isinstance(source.get(key), str) or not source[key].strip() or source[key].startswith('-') or '\x00' in source[key] or '\n' in source[key]:
                        raise Error(f'Git source requires a valid {key}')
                if source['visibility'] == 'shared':
                    url = source['url']
                    if not (re.match(r'^[A-Za-z][A-Za-z0-9+.-]*://', url) and not url.startswith('file:') or re.match(r'^[^/@:]+@[^/:]+:.+', url)):
                        raise Error('Shared Git sources require portable remote URLs; local remotes must be private')
            else:
                raise Error('Source type must be directory or git')
        for skill in self.skills.values():
            valid_id(skill.get('source'))
            source = self.sources.get(skill.get('source'))
            if source is None or source['visibility'] != skill['visibility']:
                raise Error('Skill references an unknown or differently scoped source')
            # Missing source content affects availability, not identity validity.
            root = self.source_path(source) if source['type'] == 'directory' else Path('/skillset-source')
            contained(root, skill.get('path'))
            if skill.get('upstream_name') is not None and not isinstance(skill['upstream_name'], str):
                raise Error('Skill upstream_name must be a string')
        for profile in self.profiles.values():
            for skill_id in _ids(profile.get('skills'), 'Profile skills'):
                skill = self.skills.get(skill_id)
                if skill is None or skill['visibility'] != profile['visibility']:
                    raise Error('Profile references an unknown or differently scoped skill')
            if 'name' in profile and (not isinstance(profile['name'], str) or not profile['name'].strip()):
                raise Error('Profile display name must be nonempty')
        for scope, lock in self.locks.items():
            revisions = lock.get('sources')
            if not isinstance(revisions, dict):
                raise Error('Lock sources must be an object')
            for key, revision in revisions.items():
                source = self.sources.get(key)
                if source is None or source['visibility'] != scope or source['type'] != 'git':
                    raise Error('Lock references an unknown or differently scoped remote source')
                if not isinstance(revision, str) or not re.fullmatch('[0-9a-f]{40}', revision):
                    raise Error('Lock revisions must be exact 40-character Git commits')
        _ids(self.machine.get('profiles'), 'Selected profiles')
        if not isinstance(self.machine.get('overrides'), dict):
            raise Error('Overrides must be an object')
        if selection:
            self.selection()

    def selection(self):
        profiles = _ids(self.machine.get('profiles'), 'Selected profiles')
        overrides = self.machine.get('overrides')
        if not isinstance(overrides, dict):
            raise Error('Overrides must be an object')
        reasons = {}
        for profile_id in sorted(profiles):
            if profile_id not in self.profiles:
                raise Error(f'Unknown selected profile: {profile_id}')
            for skill_id in _ids(self.profiles[profile_id].get('skills'), 'Profile skills'):
                if skill_id not in self.skills:
                    raise Error(f'Unknown skill in selected profile: {skill_id}')
                reasons.setdefault(skill_id, []).append(f'profile:{profile_id}')
        disabled = []
        for skill_id, override in sorted(overrides.items()):
            if skill_id not in self.skills:
                raise Error(f'Unknown skill override: {skill_id}')
            if override not in ('enabled', 'disabled'):
                raise Error('Override must be enabled or disabled; remove it to inherit')
            if override == 'enabled':
                reasons.setdefault(skill_id, []).append('override:enabled')
            else:
                reasons.pop(skill_id, None)
                disabled.append(skill_id)
        return {'selected': sorted(reasons), 'reasons': reasons, 'profiles': sorted(profiles),
                'overrides': deepcopy(overrides), 'disabled': disabled}

    def save_machine(self, machine):
        previous = self.machine
        self.machine = machine
        try:
            self.validate()
            selection = self.selection()
            write_many({self.paths.config / 'machine.json': machine,
                        self.paths.config / 'last-selection.json': {'schema_version': 1, 'selection': selection}})
        except BaseException:
            self.machine = previous
            raise
        return selection
