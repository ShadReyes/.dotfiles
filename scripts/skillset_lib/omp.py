"""OMP-only discovery overlays; never edit global settings or plugin state."""

from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import tempfile

from .core import Error


VERIFIED_VERSIONS = {'omp/18.18.8', 'omp/18.18.9', 'omp/18.19.0'}


class Unsupported(Error):
    def __init__(self, message):
        super().__init__(message, 3)


def _run(*arguments, overlay=None, json_output=False, environment=None, cwd=None):
    environment = dict(os.environ if environment is None else environment)
    if overlay is not None:
        previous = environment.get('PI_CONFIG_FILES', '')
        environment['PI_CONFIG_FILES'] = (previous + os.pathsep if previous else '') + str(overlay)
    try:
        result = subprocess.run(['omp', *arguments], capture_output=True, text=True,
                                env=environment, cwd=cwd, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Error('OMP discovery inspection is unavailable', 3) from exc
    if result.returncode:
        raise Error('OMP rejected discovery inspection; existing exposure retained', 3)
    try:
        return json.loads(result.stdout) if json_output else result.stdout.strip()
    except ValueError as exc:
        raise Error('OMP returned an unsupported discovery response', 3) from exc


def _setting(key):
    value = _run('config', 'get', key, '--json', json_output=True)
    if not isinstance(value, dict) or value.get('key') != key or 'value' not in value:
        raise Error('OMP returned an unsupported settings response', 3)
    return value['value']


def _strings(value):
    if not isinstance(value, list) or any(not isinstance(item, str) or not item or '\x00' in item for item in value):
        raise Error('Unsupported OMP discovery setting; no setting was changed', 3)
    return value


def _path(value):
    return Path(os.path.abspath(os.path.expanduser(value)))


def _legacy(path, repo):
    root = repo / 'skills'
    if path.is_relative_to(root):
        return True
    # Resolve checkout aliases before a relocated child can leave the repository.
    for ancestor in reversed(path.parents):
        if ancestor.resolve() == repo:
            return path.relative_to(ancestor).parts[0] == 'skills'
    return path.resolve().is_relative_to(root.resolve())


def _legacy_root(root, repo):
    if _legacy(root, repo):
        return True
    if root.is_dir():
        for entry in root.iterdir():
            if entry.is_symlink():
                target = Path(os.readlink(entry))
                target = target if target.is_absolute() else entry.parent / target
                if _legacy(_path(str(target)), repo):
                    return True
    return False


def _project_directories(home):
    project = Path.cwd().resolve()
    boundary = home if project.is_relative_to(home) else Path(project.anchor)
    git = subprocess.run(['git', '-C', str(project), 'rev-parse', '--show-toplevel'],
                         capture_output=True, text=True)
    if git.returncode == 0:
        boundary = Path(git.stdout.strip()).resolve()
    directories = []
    for directory in (project, *project.parents):
        directories.append(directory)
        if directory == boundary:
            break
    return directories


def _validate_database(path):
    # Runtime/auth databases also exist without legacy configuration.
    # Only inspect whether settings rows exist; never read credential values.
    if path.is_symlink() or not path.is_file():
        raise Unsupported('OMP runtime database is not a readable regular file')
    try:
        with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True, timeout=1)) as database:
            legacy = database.execute('SELECT 1 FROM settings LIMIT 1').fetchone() is not None
    except sqlite3.Error as exc:
        raise Unsupported('OMP runtime database cannot be safely inspected') from exc
    if legacy:
        raise Unsupported('Legacy OMP settings require independent migration before managed exposure')


def _validate_settings(agent, projects):
    """Strict overlay parsing cannot quarantine originals, unlike normal OMP startup."""
    candidates = []
    for directory in (agent, *(project / '.omp' for project in projects)):
        present = [directory / name for name in ('config.yml', 'config.yaml')
                   if (directory / name).exists() or (directory / name).is_symlink()]
        if present:
            if not present[0].is_file():
                raise Unsupported('OMP configuration is not a readable regular file')
            candidates.append(present[0])
        elif any((directory / name).exists() for name in ('settings.json', 'config.json', 'config.jsonc')):
            raise Unsupported('Legacy OMP settings require independent migration before managed exposure')
        elif (directory / 'agent.db').exists() or (directory / 'agent.db').is_symlink():
            _validate_database(directory / 'agent.db')
    if not candidates:
        return
    with tempfile.TemporaryDirectory(prefix='skillset-omp-validate-') as temporary:
        home = Path(temporary)
        environment = {**os.environ, 'HOME': temporary, 'OMP_PROFILE': '', 'PI_PROFILE': '',
                       'PI_CODING_AGENT_DIR': str(home / '.omp/agent'), 'PI_CONFIG_FILES': '',
                       'CLAUDE_CONFIG_DIR': str(home / '.claude'),
                       'XDG_CONFIG_HOME': str(home / '.config'), 'XDG_DATA_HOME': str(home / '.local/share'),
                       'XDG_STATE_HOME': str(home / '.local/state'), 'XDG_CACHE_HOME': str(home / '.cache')}
        for candidate in candidates:
            _run('config', 'get', 'skills.customDirectories', '--json', overlay=candidate,
                 json_output=True, environment=environment, cwd=home)


def configuration(model, previous_skills=None):
    """Preserve foreign custom roots; block legacy routes that an overlay cannot isolate."""
    version = _run('--version')
    if version not in VERIFIED_VERSIONS:
        raise Unsupported('OMP build is not verified for managed exposure (requires 18.18.8, 18.18.9, or 18.19.0)')
    profile = os.environ.get('OMP_PROFILE', os.environ.get('PI_PROFILE', '')).strip()
    if profile not in ('', 'default') or os.environ.get('PI_CONFIG_DIR'):
        raise Unsupported('Only the default native OMP profile/config layout is verified for exposure')
    home = model.paths.home
    agent = _path(os.environ.get('PI_CODING_AGENT_DIR') or str(home / '.omp/agent'))
    projects = _project_directories(home)
    _validate_settings(agent, projects)
    directories = _strings(_setting('skills.customDirectories'))
    if any('$' in value for value in directories):
        raise Unsupported('Environment-dependent custom directory paths are not verified')
    providers = _strings(_setting('enabledProviders'))
    for discovery in (agent / 'skills', agent / 'managed-skills'):
        if any(root.is_relative_to(discovery.resolve()) for root in (model.paths.config, model.paths.data)):
            raise Error('Skillset state must stay outside the active OMP discovery roots', 2)
    roots = [(agent / 'skills', 'skills.enablePiUser')]
    foreign = [
        ('claude', _path(os.environ.get('CLAUDE_CONFIG_DIR') or str(home / '.claude')) / 'skills', 'skills.enableClaudeUser'),
        ('agents', home / '.agents/skills', 'skills.enableAgentsUser'),
        ('agents', home / '.agent/skills', 'skills.enableAgentsUser'),
        ('codex', home / '.codex/skills', 'skills.enableCodexUser'),
        ('opencode', home / '.config/opencode/skills', None),
    ]
    roots.extend((root, toggle) for provider, root, toggle in foreign if provider in providers)
    project = projects[0]
    for directory in projects:
        roots.extend((directory / suffix, toggle) for suffix, toggle in (
            ('.omp/skills', 'skills.enablePiProject'),
            ('.claude/skills', 'skills.enableClaudeProject'),
            ('.agents/skills', 'skills.enableAgentsProject'),
            ('.agent/skills', 'skills.enableAgentsProject'),
            ('.codex/skills', None),
        ))
    for root, toggle in roots:
        if _legacy_root(root, model.paths.repo) and (toggle is None or _setting(toggle) is not False):
            raise Error('A shared/native legacy library route cannot be isolated for OMP; exposure retained', 4)
    managed = model.paths.data / 'exposure/omp'
    retained = []
    for value in directories:
        path = _path(value)
        if previous_skills is not None and path.resolve() == previous_skills.resolve():
            continue
        if path.is_relative_to(managed) or path.resolve().is_relative_to(managed):
            raise Error('An unowned managed-discovery route is already configured', 4)
        if not _legacy(path, model.paths.repo):
            retained.append(value)
    return {'version': version, 'directories': retained, 'cwd': str(project),
            'profile': os.environ.get('OMP_PROFILE', os.environ.get('PI_PROFILE', '')),
            'agent': str(agent), 'overlays': os.environ.get('PI_CONFIG_FILES', '')}


def verify(config, active, repo):
    """Use OMP's real loader, including its frontmatter and user-filter semantics."""
    result = _run('skill', 'list', '--json', overlay=config, json_output=True)
    if not isinstance(result, dict) or not isinstance(result.get('skills'), list):
        raise Error('Unsupported OMP skill inventory', 3)
    markers = set()
    for entry in result['skills']:
        if not isinstance(entry, dict) or not isinstance(entry.get('filePath'), str):
            raise Error('Unsupported OMP skill record', 3)
        path = _path(entry['filePath'])
        if _legacy(path, repo):
            raise Error('Legacy library instructions remain reachable through an independent OMP route', 4)
        markers.add(str(path.resolve()))
    expected = {str((Path(entry['installed_directory']) / 'SKILL.md').resolve()) for entry in active['active']}
    if not expected.issubset(markers):
        raise Error('OMP cannot discover the complete installed selection; exposure retained', 3)
