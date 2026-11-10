"""Interrupted revision updates recover locally without publishing private state."""

from contextlib import contextmanager
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import uuid

sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from skillset_lib.core import Error, Model, Paths, atomic_write, locked, publish_locks
from skillset_lib.install import update


SCRIPTS = Path(__file__).parent / 'scripts'
CLI = SCRIPTS / 'skillset'
OLD_SHARED, OLD_PRIVATE, NEW = '1' * 40, '2' * 40, '3' * 40


@contextmanager
def world():
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        home, repo = root / 'home', root / 'repo'
        home.mkdir()
        repo.mkdir()
        environment = {
            'HOME': str(home), 'XDG_CONFIG_HOME': str(home / '.config'),
            'XDG_DATA_HOME': str(home / '.local/share'),
            # Keep version-manager probes from writing into this fixture's HOME.
            'PATH': str(Path(sys.executable).resolve().parent) + os.pathsep + os.environ.get('PATH', ''),
            'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': str(home / '.gitconfig'),
            'GIT_AUTHOR_NAME': 'Fixture', 'GIT_COMMITTER_NAME': 'Fixture',
            'GIT_AUTHOR_EMAIL': 'fixture@example.invalid',
            'GIT_COMMITTER_EMAIL': 'fixture@example.invalid',
        }
        # Environment and Git subprocesses are real, isolated machine boundaries.
        with patch.dict(os.environ, environment):
            paths = Paths(repo, home)
            upstream = root / 'upstream'
            upstream.mkdir()
            subprocess.run(['git', 'init', '-q', '--initial-branch=main', str(upstream)], check=True)
            (upstream / 'original.txt').write_text('fixture source remains unchanged\n')
            subprocess.run(['git', '-C', str(upstream), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(upstream), 'commit', '-qm', 'Fixture'], check=True)
            revision = subprocess.run(['git', '-C', str(upstream), 'rev-parse', 'HEAD'],
                                      check=True, text=True, capture_output=True).stdout.strip()
            portable = 'https://fixtures.invalid/portable'
            subprocess.run(['git', 'config', '--global', f'url.{upstream}.insteadOf', portable], check=True)
            for scope, source_id, url, old in (
                ('shared', 'portable', portable, OLD_SHARED),
                ('private', 'local-only', str(upstream), OLD_PRIVATE),
            ):
                directory = paths.shared if scope == 'shared' else paths.config
                atomic_write(directory / 'catalog.json', {
                    'schema_version': 1, 'sources': {source_id: {
                        'type': 'git', 'url': url, 'ref': 'main', 'provenance': 'third-party'}},
                    'skills': {},
                })
                # Noncanonical bytes and distinct permissions must survive rollback exactly.
                (directory / 'lock.json').write_text(
                    json.dumps({'sources': {source_id: old}, 'schema_version': 1}) + '\n\n')
                (directory / 'lock.json').chmod(0o640 if scope == 'shared' else 0o600)
            yield paths, revision, upstream


def lock_bytes(paths):
    return {scope: ((root / 'lock.json').read_bytes(), (root / 'lock.json').stat().st_mode & 0o777)
            for scope, root in (('shared', paths.shared), ('private', paths.config))}


def inventory(root):
    return {str(path.relative_to(root)): (path.lstat().st_mode, path.lstat().st_mtime_ns,
                                         path.read_bytes() if path.is_file() else None)
            for path in root.rglob('*') if not path.is_symlink()}


def crash_update(paths, during_rollback=False):
    # os.replace is the filesystem boundary; kill a real process after a real replacement.
    script = r'''
import os
from pathlib import Path
import signal
import sys
from skillset_lib.core import Model, Paths, locked
from skillset_lib.install import update
paths = Paths(sys.argv[1], sys.argv[2])
replace = os.replace
rollback = sys.argv[3] == 'rollback'
private_replacements = 0
def interrupted_replace(source, target):
    global private_replacements
    replace(source, target)
    if rollback and Path(target) == paths.config / 'lock.json':
        private_replacements += 1
        if private_replacements == 1:
            raise OSError('fixture publication failure after replacement')
        os.kill(os.getpid(), signal.SIGKILL)
    if not rollback and Path(target) == paths.shared / 'lock.json':
        os.kill(os.getpid(), signal.SIGKILL)
os.replace = interrupted_replace
with locked(paths):
    update(Model(paths), [], all_sources=True)
'''
    result = subprocess.run([sys.executable, '-c', script, str(paths.repo), str(paths.home),
                             'rollback' if during_rollback else 'publication'],
                            env={**os.environ, 'PYTHONPATH': str(SCRIPTS)}, capture_output=True, text=True)
    if result.returncode != -signal.SIGKILL:
        raise AssertionError(f'Fixture child did not reach interruption: {result.returncode}: {result.stderr}')


class LockTransactionTests(unittest.TestCase):
    def assert_conflict(self, function, *args, **kwargs):
        with self.assertRaises(Error) as raised:
            function(*args, **kwargs)
        self.assertEqual(4, raised.exception.code)

    def test_killed_update_restores_exact_old_locks_before_next_mutation(self):
        with world() as (paths, revision, upstream):
            original = lock_bytes(paths)
            source = (upstream / 'original.txt').read_bytes()
            crash_update(paths)
            self.assertNotEqual(original['shared'][0], (paths.shared / 'lock.json').read_bytes())
            self.assertEqual(original['private'][0], (paths.config / 'lock.json').read_bytes())
            token = (paths.shared / '.mutation.lock').read_text()
            self.assertEqual(token, str(uuid.UUID(token)))
            journals = list((paths.config / '.lock-transactions').glob('*.json'))
            self.assertEqual(1, len(journals))
            self.assertEqual(0o700, journals[0].parent.stat().st_mode & 0o777)
            self.assertEqual(0o600, journals[0].stat().st_mode & 0o777)

            # A recovering mutation must never contact an upstream subprocess.
            with patch('subprocess.run', side_effect=AssertionError('Recovery attempted acquisition')), locked(paths):
                model = Model(paths)
                self.assertEqual(original, lock_bytes(paths))
                self.assertEqual(OLD_SHARED, model.locks['shared']['sources']['portable'])
                self.assertEqual(OLD_PRIVATE, model.locks['private']['sources']['local-only'])
                atomic_write(paths.config / 'machine.json', {'schema_version': 1, 'profiles': [], 'overrides': {}})
            self.assertEqual(b'', (paths.shared / '.mutation.lock').read_bytes())
            self.assertFalse(journals[0].exists())
            self.assertEqual(source, (upstream / 'original.txt').read_bytes())

    def test_read_only_commands_reject_pending_update_without_any_writes(self):
        with world() as (paths, _, _):
            crash_update(paths)
            before = inventory(paths.home.parent)
            for arguments in (('list', '--json'), ('status', '--json'), ('resolve', '--json'),
                              ('validate', '--json'), ('validate', '--shared-only', '--json')):
                with self.subTest(arguments=arguments):
                    result = subprocess.run([str(CLI), '--repo', str(paths.repo), *arguments],
                                            capture_output=True, text=True)
                    self.assertEqual(4, result.returncode, result.stderr)
                    self.assertEqual(before, inventory(paths.home.parent))
            self.assert_conflict(Model, paths)
            # Private file reads are forbidden for shared-only validation, even in conflict.
            open_file = os.open
            def shared_only_open(path, *args, **kwargs):
                candidate = Path(path)
                if candidate.is_relative_to(paths.config) or candidate.is_relative_to(paths.data):
                    raise AssertionError('Shared-only validation accessed private state')
                return open_file(path, *args, **kwargs)
            path_open = Path.open
            def shared_only_path_open(path, *args, **kwargs):
                if path.is_relative_to(paths.config) or path.is_relative_to(paths.data):
                    raise AssertionError('Shared-only validation accessed private state')
                return path_open(path, *args, **kwargs)
            with patch('os.open', side_effect=shared_only_open), patch.object(Path, 'open', shared_only_path_open):
                self.assert_conflict(Model, paths, shared_only=True)
            self.assertEqual(before, inventory(paths.home.parent))

    def test_another_home_cannot_recover_or_mutate_a_pending_shared_update(self):
        with world() as (paths, _, _):
            crash_update(paths)
            before = lock_bytes(paths)
            another_home = paths.home.parent / 'another-home'
            with patch.dict(os.environ, {'XDG_CONFIG_HOME': str(another_home / '.config'),
                                        'XDG_DATA_HOME': str(another_home / '.local/share')}):
                another = Paths(paths.repo, another_home)
                with self.assertRaises(Error) as raised:
                    with locked(another):
                        self.fail('Unmatched transaction was allowed to mutate')
                self.assertEqual(4, raised.exception.code)
                self.assertEqual(before, lock_bytes(paths))
                self.assert_conflict(Model, another)
            with locked(paths):
                Model(paths).validate()
            with locked(another):
                model = Model(another)
                self.assertEqual(OLD_SHARED, model.locks['shared']['sources']['portable'])
                self.assertEqual({}, model.locks['private']['sources'])

    def test_successful_update_keeps_private_records_and_journal_outside_checkout(self):
        with world() as (paths, revision, upstream):
            source = inventory(upstream)
            with locked(paths):
                result = update(Model(paths), [], all_sources=True)
            self.assertEqual({'portable', 'local-only'}, {item['source'] for item in result['updates']})
            self.assertEqual(revision, Model(paths).locks['shared']['sources']['portable'])
            self.assertEqual(revision, Model(paths).locks['private']['sources']['local-only'])
            self.assertEqual(b'', (paths.shared / '.mutation.lock').read_bytes())
            self.assertEqual([], list((paths.config / '.lock-transactions').glob('*.json')))
            for path in paths.repo.rglob('*'):
                if path.is_file():
                    content = path.read_bytes()
                    self.assertNotIn(b'local-only', content)
                    self.assertNotIn(str(paths.home).encode(), content)
            self.assertEqual(0o600, (paths.config / 'lock.json').stat().st_mode & 0o777)
            self.assertEqual(source, inventory(upstream))

    def test_ordinary_failure_rolls_back_bytes_and_permissions_and_rethrows_original(self):
        with world() as (paths, _, _):
            original = lock_bytes(paths)
            failure = OSError('fixture failure after second replacement')
            replace = os.replace
            failed = False
            def failing_replace(source, target):
                nonlocal failed
                replace(source, target)
                if Path(target) == paths.config / 'lock.json' and not failed:
                    failed = True
                    raise failure
            documents = {root / 'lock.json': {'schema_version': 1, 'sources': {key: NEW}}
                         for root, key in ((paths.shared, 'portable'), (paths.config, 'local-only'))}
            # os.replace is an external filesystem boundary, including failure after rename.
            with locked(paths), patch('os.replace', side_effect=failing_replace):
                with self.assertRaises(OSError) as raised:
                    publish_locks(paths, documents)
            self.assertIs(failure, raised.exception)
            self.assertEqual(original, lock_bytes(paths))
            self.assertEqual(b'', (paths.shared / '.mutation.lock').read_bytes())

    def test_crash_during_rollback_leaves_recovery_retryable(self):
        with world() as (paths, _, _):
            original = lock_bytes(paths)
            crash_update(paths, during_rollback=True)
            self.assertNotEqual(original, lock_bytes(paths))
            with locked(paths):
                self.assertEqual(original, lock_bytes(paths))
                Model(paths).validate()
            self.assertEqual(b'', (paths.shared / '.mutation.lock').read_bytes())

    def test_journal_without_pending_token_never_rolls_back_later_edits(self):
        with world() as (paths, _, _):
            unlink = os.unlink
            def retain_committed_journal(path, *args, **kwargs):
                if Path(path).parent == paths.config / '.lock-transactions' and Path(path).suffix == '.json':
                    raise OSError('fixture journal cleanup failure')
                return unlink(path, *args, **kwargs)
            # Unlink is the external filesystem cleanup boundary after commit.
            with locked(paths), patch('os.unlink', side_effect=retain_committed_journal):
                update(Model(paths), [], all_sources=True)
            self.assertEqual(1, len(list((paths.config / '.lock-transactions').glob('*.json'))))
            self.assertEqual(b'', (paths.shared / '.mutation.lock').read_bytes())
            atomic_write(paths.shared / 'lock.json', {'schema_version': 1, 'sources': {'portable': NEW}})
            changed = lock_bytes(paths)
            with locked(paths):
                self.assertEqual(changed, lock_bytes(paths))
                Model(paths).validate()

    def test_recovery_refuses_unrecognized_lock_edits_without_overwriting_them(self):
        with world() as (paths, _, _):
            crash_update(paths)
            atomic_write(paths.shared / 'lock.json', {'schema_version': 1, 'sources': {'portable': NEW}})
            before = lock_bytes(paths)
            with self.assertRaises(Error) as raised:
                with locked(paths):
                    self.fail('Modified interrupted locks were overwritten')
            self.assertEqual(4, raised.exception.code)
            self.assertEqual(before, lock_bytes(paths))
            self.assertTrue((paths.shared / '.mutation.lock').read_bytes())

    def test_interrupted_first_update_restores_absence_of_both_lockfiles(self):
        with world() as (paths, _, _):
            (paths.shared / 'lock.json').unlink()
            (paths.config / 'lock.json').unlink()
            crash_update(paths)
            self.assertTrue((paths.shared / 'lock.json').exists())
            with locked(paths):
                self.assertFalse((paths.shared / 'lock.json').exists())
                self.assertFalse((paths.config / 'lock.json').exists())
                self.assertEqual({}, Model(paths).locks['shared']['sources'])

    def test_invalid_journal_fields_fail_closed_without_lock_changes(self):
        for invalid in ('token', 'repo', 'config', 'scope', 'target', 'bytes', 'permissions'):
            with self.subTest(invalid=invalid), world() as (paths, _, _):
                crash_update(paths)
                journal = next((paths.config / '.lock-transactions').glob('*.json'))
                document = json.loads(journal.read_text())
                if invalid == 'token':
                    document['token'] = str(uuid.uuid4())
                elif invalid == 'repo':
                    document['repo'] = str(paths.repo.parent / 'other-repo')
                elif invalid == 'config':
                    document['config'] = str(paths.home / 'other-config')
                elif invalid == 'scope':
                    document['documents']['other'] = document['documents']['shared']
                elif invalid == 'target':
                    document['documents']['shared']['path'] = str(paths.home / 'unrelated')
                elif invalid == 'bytes':
                    document['documents']['shared']['before']['bytes'] = 'not base64!'
                else:
                    document['documents']['private']['after']['mode'] = 0o644
                journal.write_text(json.dumps(document))
                before = lock_bytes(paths)
                with self.assertRaises(Error) as raised:
                    with locked(paths):
                        self.fail('Invalid journal was accepted')
                self.assertEqual(4, raised.exception.code)
                self.assertEqual(before, lock_bytes(paths))
                self.assertTrue((paths.shared / '.mutation.lock').read_bytes())

    def test_unsafe_journal_and_target_files_fail_closed(self):
        for invalid in ('journal-mode', 'journal-symlink', 'journal-hardlink', 'target-symlink', 'token'):
            with self.subTest(invalid=invalid), world() as (paths, _, _):
                crash_update(paths)
                journal = next((paths.config / '.lock-transactions').glob('*.json'))
                outside = paths.home / 'unrelated'
                outside.write_text('fixture bytes must not change\n')
                if invalid == 'journal-mode':
                    journal.chmod(0o644)
                elif invalid == 'journal-symlink':
                    journal.unlink()
                    journal.symlink_to(outside)
                elif invalid == 'journal-hardlink':
                    os.link(journal, paths.home / 'journal-alias')
                elif invalid == 'target-symlink':
                    (paths.config / 'lock.json').unlink()
                    (paths.config / 'lock.json').symlink_to(outside)
                else:
                    (paths.shared / '.mutation.lock').write_text('invalid token')
                before = inventory(paths.home.parent)
                with self.assertRaises(Error) as raised:
                    with locked(paths):
                        self.fail('Unsafe transaction state was accepted')
                self.assertEqual(4, raised.exception.code)
                self.assertEqual(before, inventory(paths.home.parent))
                self.assertEqual('fixture bytes must not change\n', outside.read_text())



if __name__ == '__main__':
    unittest.main()
