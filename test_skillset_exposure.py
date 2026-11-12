"""Managed discovery contracts with real installations and isolated homes."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent / 'scripts'))
from skillset_lib.core import Model, Paths, atomic_write, locked
from skillset_lib.install import sync


class ExposureTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.home = self.root / 'home'
        self.repo = self.root / 'repo'
        self.home.mkdir()
        self.repo.mkdir()
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        self.environment = patch.dict(os.environ, {
            'HOME': str(self.home), 'XDG_CONFIG_HOME': str(self.home / '.config'),
            'XDG_DATA_HOME': str(self.home / '.local/share'),
            'PATH': str(self.bin) + os.pathsep + os.environ.get('PATH', ''),
            'PI_CONFIG_FILES': '', 'OMP_PROFILE': '', 'PI_PROFILE': '',
            'PI_CODING_AGENT_DIR': str(self.home / '.omp/agent'),
        })
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.paths = Paths(self.repo, self.home)
        self.source = self.repo / 'skills/library'
        for name in ('alpha', 'beta'):
            directory = self.source / name
            directory.mkdir(parents=True)
            (directory / 'SKILL.md').write_text(
                f'---\nname: {name}\ndescription: Standalone fixture\n---\n{name} instructions\n')
            (directory / 'reference.txt').write_text(name + ' companion\n')
        atomic_write(self.paths.shared / 'catalog.json', {
            'schema_version': 1,
            'sources': {'library': {'type': 'directory', 'path': 'skills/library', 'provenance': 'authored'}},
            'skills': {name: {'source': 'library', 'path': name} for name in ('alpha', 'beta')},
        })
        self.select('alpha')
        # External OMP process boundary; a separate smoke proof exercises the installed CLI.
        executable = self.bin / 'omp'
        executable.write_text('#!' + sys.executable + '\n' + r'''
import json, os, sys
from pathlib import Path
args=sys.argv[1:]
settings_file=Path.home()/'omp-fixture.json'
settings=json.loads(settings_file.read_text()) if settings_file.exists() else {}
if args==['--version']:
    print(settings.get('version','omp/18.18.8'))
elif args==['config','path']:
    print(Path.home()/'.omp/agent')
elif args[:2]==['config','get']:
    overlays=os.environ.get('PI_CONFIG_FILES','')
    global_file=Path.home()/'.omp/agent/config.yml'
    if overlays:
        for value in overlays.split(os.pathsep):
            if not isinstance(json.loads(Path(value).read_text()),dict):
                sys.exit(1)
    elif global_file.exists():
        try:
            json.loads(global_file.read_text())
        except ValueError:
            global_file.rename(global_file.with_suffix('.broken'))
            sys.exit(1)
    defaults={'skills.customDirectories':[], 'enabledProviders':[], 'skills.enablePiUser':True,
              'skills.enablePiProject':True, 'skills.enableClaudeUser':True,
              'skills.enableClaudeProject':True, 'skills.enableAgentsUser':True,
              'skills.enableAgentsProject':True, 'skills.enableCodexUser':True}
    print(json.dumps({'key':args[2], 'value':settings.get(args[2],defaults.get(args[2]))}))
elif args==['skill','list','--json']:
    config=json.loads(Path(os.environ['PI_CONFIG_FILES'].split(os.pathsep)[-1]).read_text())
    paths=[]
    for root in config['skills']['customDirectories']:
        directory=Path(root).expanduser()
        if directory.is_dir():
            paths.extend({'filePath':str(path)} for path in directory.glob('*/SKILL.md')
                         if path.parent.name not in settings.get('hiddenSkills',[]))
    print(json.dumps({'skills':paths,'warnings':[]}))
else:
    sys.exit(2)
''')
        executable.chmod(0o700)

    def select(self, *names):
        atomic_write(self.paths.config / 'machine.json', {
            'schema_version': 1, 'profiles': [], 'overrides': {name: 'enabled' for name in names},
        })

    def activate(self):
        with locked(self.paths):
            sync(Model(self.paths), offline=True)

    def cli(self, *arguments):
        return subprocess.run([str(Path(__file__).parent / 'scripts/skillset'),
                               '--repo', str(self.repo), 'expose', *arguments],
                              cwd=self.repo, capture_output=True, text=True)

    def current(self):
        return self.paths.data / 'exposure/omp/current'

    def test_apply_exposes_only_installed_selection_with_companions(self):
        self.activate()
        result = self.cli('apply', '--target', 'omp')
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual('applied', json.loads(result.stdout)['targets'][0]['status'])
        root = self.current() / 'skills'
        self.assertEqual(['alpha'], sorted(path.name for path in root.iterdir()))
        self.assertEqual('alpha companion\n', (root / 'alpha/reference.txt').read_text())
        self.assertTrue((self.source / 'beta/SKILL.md').is_file())
        self.assertFalse((self.home / '.agents').exists())

    def test_pending_and_failed_installation_retain_the_applied_generation(self):
        self.activate()
        self.assertEqual(0, self.cli('apply', '--target', 'omp').returncode)
        before = os.readlink(self.current())
        self.select('beta')
        pending = self.cli('apply', '--target', 'omp')
        self.assertEqual(3, pending.returncode, pending.stdout)
        self.assertEqual(before, os.readlink(self.current()))
        (self.source / 'beta/SKILL.md').unlink()
        failed = self.cli('apply', '--target', 'omp')
        self.assertEqual(3, failed.returncode, failed.stdout)
        self.assertEqual(before, os.readlink(self.current()))
        self.assertEqual('alpha companion\n', (self.current() / 'skills/alpha/reference.txt').read_text())

    def test_empty_activation_removes_only_managed_exposure(self):
        foreign = self.home / 'independent'
        (foreign / 'external').mkdir(parents=True)
        marker = foreign / 'external/SKILL.md'
        marker.write_text('independent instructions\n')
        settings = self.home / 'omp-fixture.json'
        settings.write_text(json.dumps({'skills.customDirectories': [str(self.source), str(foreign)]}))
        original_settings = settings.read_bytes()
        self.activate()
        self.assertEqual(0, self.cli('apply', '--target', 'omp').returncode)
        retained = (self.current() / 'skills/alpha').resolve()
        self.select()
        self.activate()
        empty = self.cli('apply', '--target', 'omp')
        self.assertEqual(0, empty.returncode, empty.stdout)
        self.assertEqual([], list((self.current() / 'skills').iterdir()))
        configuration = json.loads((self.current() / 'config.json').read_text())
        self.assertEqual([str(foreign), str(self.current().resolve() / 'skills')],
                         configuration['skills']['customDirectories'])
        self.assertEqual(original_settings, settings.read_bytes())
        self.assertEqual('independent instructions\n', marker.read_text())
        self.assertEqual('alpha companion\n', (retained / 'reference.txt').read_text())
        self.assertTrue((self.source / 'alpha/SKILL.md').is_file())

    def test_conflicting_entries_and_malformed_applied_state_are_never_overwritten(self):
        self.activate()
        self.assertEqual(0, self.cli('apply', '--target', 'omp').returncode)
        current = self.current()
        target = os.readlink(current)
        config = current.resolve() / 'config.json'
        original_config = config.read_bytes()
        for label, payload in [('non-object', b'[]'), ('wrong-shape', b'{"mcp": {}}'),
                               ('malformed', b'{'), ('duplicate-key', b'{"skills":{},"skills":{}}')]:
            with self.subTest(label=label):
                config.write_bytes(payload)
                result = self.cli('apply', '--target', 'omp')
                self.assertEqual(4, result.returncode, result.stdout)
                self.assertEqual(payload, config.read_bytes())
                self.assertEqual(target, os.readlink(current))
                config.write_bytes(original_config)
        current.unlink()
        current.write_bytes(b'unowned operator note\n')
        result = self.cli('apply', '--target', 'omp')
        self.assertEqual(4, result.returncode, result.stdout)
        self.assertEqual(b'unowned operator note\n', current.read_bytes())

    def test_shared_legacy_root_blocks_only_omp_without_mutating_the_pool(self):
        pool = self.home / '.agents/skills'
        pool.mkdir(parents=True)
        legacy = pool / 'library'
        legacy.symlink_to(self.source)
        settings = self.home / 'omp-fixture.json'
        settings.write_text(json.dumps({'enabledProviders': ['agents']}))
        original = settings.read_bytes()
        self.activate()
        result = self.cli('apply', '--target', 'omp')
        self.assertEqual(4, result.returncode, result.stdout)
        self.assertEqual(str(self.source), os.readlink(legacy))
        self.assertEqual(original, settings.read_bytes())
        self.assertFalse(self.current().exists())

    def test_interruption_exposes_either_complete_generation_never_a_partial_set(self):
        self.activate()
        self.assertEqual(0, self.cli('apply', '--target', 'omp').returncode)
        self.select('beta')
        self.activate()
        for phase, expected in [('before', ['alpha']), ('after', ['beta'])]:
            with self.subTest(phase=phase):
                # Filesystem boundary: terminate the real child at the atomic route switch.
                program = '''
import os, signal, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from skillset_lib.cli import main
original = os.replace
def interrupt(source, destination):
    selected = Path(destination).name == 'current'
    if selected and sys.argv[3] == 'before':
        os.kill(os.getpid(), signal.SIGKILL)
    original(source, destination)
    if selected and sys.argv[3] == 'after':
        os.kill(os.getpid(), signal.SIGKILL)
os.replace = interrupt
raise SystemExit(main(['--repo', sys.argv[2], 'expose', 'apply', '--target', 'omp']))
'''
                child = subprocess.run([sys.executable, '-B', '-c', program,
                                        str(Path(__file__).parent / 'scripts'), str(self.repo), phase],
                                       cwd=self.repo, capture_output=True, text=True)
                self.assertEqual(-9, child.returncode, child.stdout + child.stderr)
                self.assertEqual(expected, sorted(path.name for path in (self.current() / 'skills').iterdir()))
                observed = self.cli('status', '--target', 'omp')
                self.assertEqual(0, observed.returncode, observed.stdout)
                self.assertEqual(1, json.loads(observed.stdout)['targets'][0]['count'])

    def test_rollback_requires_available_retained_content(self):
        self.activate()
        self.assertEqual(0, self.cli('apply', '--target', 'omp').returncode)
        prior = os.readlink(self.current())
        prior_tree = (self.current() / 'skills/alpha').resolve().parent
        self.select('beta')
        (self.source / 'beta/reference.txt').write_text('new companion\n')
        self.activate()
        self.assertEqual(0, self.cli('apply', '--target', 'omp').returncode)
        self.assertEqual(0, self.cli('rollback', '--target', 'omp').returncode)
        self.assertEqual(prior, os.readlink(self.current()))
        self.assertEqual('alpha companion\n', (self.current() / 'skills/alpha/reference.txt').read_text())
        self.assertEqual(0, self.cli('apply', '--target', 'omp').returncode)
        current = os.readlink(self.current())
        import shutil
        shutil.rmtree(prior_tree)
        failed = self.cli('rollback', '--target', 'omp')
        self.assertEqual(4, failed.returncode, failed.stdout)
        self.assertEqual(current, os.readlink(self.current()))
        self.assertEqual('new companion\n', (self.current() / 'skills/beta/reference.txt').read_text())

    def test_rollback_rechecks_native_capabilities_before_changing_exposure(self):
        self.activate()
        self.assertEqual(0, self.cli('apply', '--target', 'omp').returncode)
        self.select('beta')
        self.activate()
        self.assertEqual(0, self.cli('apply', '--target', 'omp').returncode)
        current = os.readlink(self.current())
        settings = self.home / 'omp-fixture.json'
        settings.write_text(json.dumps({'version': 'omp/99.0.0'}))
        before = settings.read_bytes()

        failed = self.cli('rollback', '--target', 'omp')

        self.assertEqual(3, failed.returncode, failed.stdout)
        self.assertEqual('unsupported', json.loads(failed.stdout)['targets'][0]['status'])
        self.assertEqual(current, os.readlink(self.current()))
        self.assertEqual('beta companion\n', (self.current() / 'skills/beta/reference.txt').read_text())
        self.assertEqual(before, settings.read_bytes())

    def test_rollback_retains_the_current_route_when_external_discovery_changes(self):
        self.activate()
        self.assertEqual(0, self.cli('apply', '--target', 'omp').returncode)
        self.select('beta')
        self.activate()
        self.assertEqual(0, self.cli('apply', '--target', 'omp').returncode)
        current = os.readlink(self.current())
        independent = self.home / 'independent'
        (independent / 'external').mkdir(parents=True)
        marker = independent / 'external/SKILL.md'
        marker.write_text('independent instructions\n')
        settings = self.home / 'omp-fixture.json'
        settings.write_text(json.dumps({'skills.customDirectories': [str(independent)]}))
        before = settings.read_bytes()

        failed = self.cli('rollback', '--target', 'omp')

        self.assertEqual(4, failed.returncode, failed.stdout)
        self.assertEqual(current, os.readlink(self.current()))
        self.assertEqual('beta companion\n', (self.current() / 'skills/beta/reference.txt').read_text())
        self.assertEqual(before, settings.read_bytes())
        self.assertEqual('independent instructions\n', marker.read_text())

    def test_rollback_requires_native_discovery_of_the_retained_selection(self):
        self.activate()
        self.assertEqual(0, self.cli('apply', '--target', 'omp').returncode)
        self.select('beta')
        self.activate()
        self.assertEqual(0, self.cli('apply', '--target', 'omp').returncode)
        current = os.readlink(self.current())
        (self.home / 'omp-fixture.json').write_text(json.dumps({'hiddenSkills': ['alpha']}))

        failed = self.cli('rollback', '--target', 'omp')

        self.assertEqual(3, failed.returncode, failed.stdout)
        self.assertEqual(current, os.readlink(self.current()))
        self.assertEqual('beta companion\n', (self.current() / 'skills/beta/reference.txt').read_text())

    def test_failed_publication_rollback_blocks_apply_until_explicit_recovery(self):
        from skillset_lib.exposure import run
        self.activate()
        self.assertEqual(0, self.cli('apply', '--target', 'omp').returncode)
        prior = os.readlink(self.current())
        self.select('beta')
        self.activate()
        original = os.replace
        # Filesystem boundary: a write completes but its completion cannot be confirmed.
        def uncertain_replace(source, destination):
            original(source, destination)
            if Path(destination).name == 'current':
                raise OSError('fixture publication durability failure')
        with patch('os.replace', uncertain_replace), locked(self.paths):
            result = run(Model(self.paths), 'apply', ['omp'])
        self.assertEqual(4, result['exit_code'])
        self.assertEqual('recovery-needed', result['targets'][0]['status'])
        self.assertEqual(4, self.cli('apply', '--target', 'omp').returncode)
        recovered = self.cli('rollback', '--target', 'omp')
        self.assertEqual(0, recovered.returncode, recovered.stdout)
        self.assertEqual(prior, os.readlink(self.current()))
        self.assertEqual('alpha companion\n', (self.current() / 'skills/alpha/reference.txt').read_text())

    def test_unsupported_target_does_not_undo_the_isolated_omp_success(self):
        self.activate()
        result = self.cli('apply', '--target', 'omp', '--target', 'codex')
        self.assertEqual(3, result.returncode, result.stdout)
        self.assertEqual(['applied', 'unsupported'],
                         [entry['status'] for entry in json.loads(result.stdout)['targets']])
        self.assertEqual('alpha companion\n', (self.current() / 'skills/alpha/reference.txt').read_text())

    def test_unsupported_build_leaves_the_applied_generation_unchanged(self):
        self.activate()
        self.assertEqual(0, self.cli('apply', '--target', 'omp').returncode)
        prior = os.readlink(self.current())
        (self.home / 'omp-fixture.json').write_text(json.dumps({'version': 'omp/99.0.0'}))
        result = self.cli('apply', '--target', 'omp')
        self.assertEqual(3, result.returncode, result.stdout)
        self.assertEqual('unsupported', json.loads(result.stdout)['targets'][0]['status'])
        self.assertEqual(prior, os.readlink(self.current()))

    def test_selected_private_content_is_local_and_unselected_content_is_retained(self):
        private = self.root / 'private-original'
        private.mkdir(mode=0o700)
        (private / 'SKILL.md').write_text('---\nname: private-fixture\ndescription: Generic private fixture\n---\nPrivate fixture.\n')
        (private / 'reference.txt').write_text('private companion\n')
        shared = (self.paths.shared / 'catalog.json').read_bytes()
        atomic_write(self.paths.config / 'catalog.json', {
            'schema_version': 1,
            'sources': {'private-fixture': {'type': 'directory', 'path': str(private), 'provenance': 'authored'}},
            'skills': {'private-fixture': {'source': 'private-fixture', 'path': '.'}},
        })
        self.select('alpha', 'private-fixture')
        self.activate()
        result = self.cli('apply', '--target', 'omp')
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertEqual('private companion\n', (self.current() / 'skills/private-fixture/reference.txt').read_text())
        self.assertNotIn('private-fixture', result.stdout)
        self.assertNotIn(str(private), result.stdout)
        self.assertEqual(shared, (self.paths.shared / 'catalog.json').read_bytes())
        self.assertEqual(0o600, (self.current() / 'manifest.json').stat().st_mode & 0o777)
        self.assertEqual(0o700, self.current().resolve().stat().st_mode & 0o777)
        self.select('alpha')
        self.activate()
        self.assertEqual(0, self.cli('apply', '--target', 'omp').returncode)
        self.assertEqual(['alpha'], sorted(path.name for path in (self.current() / 'skills').iterdir()))
        self.assertEqual('private companion\n', (private / 'reference.txt').read_text())

    def test_native_discovery_cannot_contain_machine_local_state(self):
        from skillset_lib.core import Error
        for root in ('.omp/agent/skills', '.omp/agent/managed-skills'):
            with self.subTest(root=root), patch.dict(os.environ, {'XDG_DATA_HOME': str(self.home / root)}):
                with self.assertRaises(Error) as raised:
                    Paths(self.repo, self.home)
                self.assertEqual(2, raised.exception.code)

    def test_instruction_symlinks_keep_the_original_source_boundary(self):
        marker = self.source / 'alpha/SKILL.md'
        shared = self.source / 'instructions.md'
        shared.write_bytes(marker.read_bytes())
        marker.unlink()
        marker.symlink_to('../instructions.md')
        self.activate()
        result = self.cli('apply', '--target', 'omp')
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertEqual(shared.read_bytes(), (self.current() / 'skills/alpha/SKILL.md').read_bytes())
        self.assertTrue((self.current() / 'skills/alpha/SKILL.md').is_symlink())

    def test_invalid_native_settings_are_preserved_before_normal_inspection(self):
        self.activate()
        self.assertEqual(0, self.cli('apply', '--target', 'omp').returncode)
        prior = os.readlink(self.current())
        config = self.home / '.omp/agent/config.yml'
        config.parent.mkdir(parents=True)
        for label, payload in [('syntax', 'skills: [unterminated\n'), ('shape', '[]')]:
            with self.subTest(label=label):
                config.write_text(payload)
                failed = self.cli('apply', '--target', 'omp')
                self.assertEqual(3, failed.returncode, failed.stdout)
                self.assertTrue(config.is_file())
                self.assertEqual(payload, config.read_text())
                self.assertEqual(['config.yml'], sorted(path.name for path in config.parent.iterdir()))
                self.assertEqual(prior, os.readlink(self.current()))

    def test_legacy_native_settings_require_independent_migration(self):
        self.activate()
        config = self.home / '.omp/agent/settings.json'
        config.parent.mkdir(parents=True)
        config.write_bytes(b'{"skills":{"customDirectories":[]}}')
        before = config.read_bytes()
        failed = self.cli('apply', '--target', 'omp')
        self.assertEqual(3, failed.returncode, failed.stdout)
        self.assertEqual('unsupported', json.loads(failed.stdout)['targets'][0]['status'])
        self.assertEqual(before, config.read_bytes())
        self.assertFalse(self.current().exists())

    def test_native_runtime_database_without_legacy_settings_allows_exposure(self):
        import sqlite3
        database = self.home / '.omp/agent/agent.db'
        database.parent.mkdir(parents=True)
        connection = sqlite3.connect(database)
        try:
            with connection:
                connection.execute('CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
                connection.execute('CREATE TABLE runtime (value TEXT NOT NULL)')
                connection.execute('INSERT INTO runtime VALUES (?)', ('generic retained runtime state',))
        finally:
            connection.close()
        original = database.read_bytes()
        self.activate()

        applied = self.cli('apply', '--target', 'omp')

        self.assertEqual(0, applied.returncode, applied.stdout)
        self.assertEqual('alpha companion\n', (self.current() / 'skills/alpha/reference.txt').read_text())
        unchanged = self.cli('apply', '--target', 'omp')
        self.assertEqual(0, unchanged.returncode, unchanged.stdout)
        self.assertEqual('unchanged', json.loads(unchanged.stdout)['targets'][0]['status'])
        self.assertEqual(original, database.read_bytes())
        self.assertFalse((database.parent / 'config.yml').exists())

    def test_legacy_database_settings_in_wal_are_retained_without_migration(self):
        import sqlite3
        database = self.home / '.omp/agent/agent.db'
        database.parent.mkdir(parents=True)
        connection = sqlite3.connect(database)
        self.addCleanup(connection.close)
        connection.execute('PRAGMA journal_mode=WAL')
        connection.execute('CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
        connection.commit()
        connection.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        with connection:
            connection.execute('INSERT INTO settings VALUES (?, ?)', ('skills', '{"customDirectories": []}'))
        wal = database.with_name('agent.db-wal')
        before = (database.read_bytes(), wal.read_bytes())
        self.activate()

        failed = self.cli('apply', '--target', 'omp')

        self.assertEqual(3, failed.returncode, failed.stdout)
        self.assertEqual('unsupported', json.loads(failed.stdout)['targets'][0]['status'])
        self.assertEqual(before, (database.read_bytes(), wal.read_bytes()))
        self.assertFalse((database.parent / 'config.yml').exists())
        self.assertFalse(self.current().exists())

    def test_uninspectable_native_databases_are_retained_without_exposure(self):
        import sqlite3
        database = self.home / '.omp/agent/agent.db'
        database.parent.mkdir(parents=True)
        other = self.root / 'unknown-schema.db'
        connection = sqlite3.connect(other)
        try:
            with connection:
                connection.execute('CREATE TABLE unrelated (value TEXT)')
        finally:
            connection.close()
        original_other = other.read_bytes()
        self.activate()
        for shape in ('malformed', 'unknown-schema', 'redirected'):
            with self.subTest(shape=shape):
                if shape == 'redirected':
                    database.symlink_to(other)
                else:
                    database.write_bytes(b'not a database' if shape == 'malformed' else original_other)
                before = database.read_bytes()

                failed = self.cli('apply', '--target', 'omp')

                self.assertEqual(3, failed.returncode, failed.stdout)
                self.assertEqual('unsupported', json.loads(failed.stdout)['targets'][0]['status'])
                self.assertEqual(before, database.read_bytes())
                if shape == 'redirected':
                    self.assertTrue(database.is_symlink())
                    self.assertEqual(str(other), os.readlink(database))
                self.assertFalse((database.parent / 'config.yml').exists())
                self.assertFalse(self.current().exists())
                database.unlink()
        self.assertEqual(original_other, other.read_bytes())

    def test_legacy_roots_through_checkout_aliases_do_not_expose_relocated_originals(self):
        original = self.root / 'relocated-original'
        (original / 'unselected').mkdir(parents=True)
        marker = original / 'unselected/SKILL.md'
        marker.write_text('retained unselected instructions\n')
        (self.repo / 'skills/relocated-alias').symlink_to(original)
        checkout_alias = self.root / 'checkout-alias'
        checkout_alias.symlink_to(self.repo, target_is_directory=True)
        legacy = checkout_alias / 'skills/relocated-alias'
        (self.home / 'omp-fixture.json').write_text(json.dumps({'skills.customDirectories': [str(legacy)]}))
        self.activate()
        result = self.cli('apply', '--target', 'omp')
        self.assertEqual(0, result.returncode, result.stdout)
        configuration = json.loads((self.current() / 'config.json').read_text())
        self.assertEqual([str(self.current().resolve() / 'skills')], configuration['skills']['customDirectories'])
        self.assertEqual('retained unselected instructions\n', marker.read_text())




if __name__ == '__main__':
    unittest.main()
