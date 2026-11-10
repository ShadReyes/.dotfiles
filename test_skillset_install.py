"""Installation contract exercised with isolated homes and real local Git remotes."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from skillset_lib.core import Error, Model, Paths, atomic_write, locked, read_json
from skillset_lib.install import inspect, sync, update


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.home = self.root / 'home'
        self.repo = self.root / 'dotfiles'
        self.home.mkdir()
        self.repo.mkdir()
        self.environment = patch.dict(os.environ, {
            'HOME': str(self.home), 'XDG_CONFIG_HOME': str(self.home / '.config'),
            'XDG_DATA_HOME': str(self.home / '.local/share'),
            'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': str(self.home / '.gitconfig'),
            'GIT_AUTHOR_NAME': 'Fixture', 'GIT_COMMITTER_NAME': 'Fixture',
            'GIT_AUTHOR_EMAIL': 'fixture@example.invalid',
            'GIT_COMMITTER_EMAIL': 'fixture@example.invalid',
        })
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.paths = Paths(self.repo, self.home)

    def git(self, cwd, *arguments):
        return subprocess.run(['git', '-C', str(cwd), *arguments], check=True,
                              text=True, capture_output=True).stdout.strip()

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def document(self, scope, name, **fields):
        root = self.paths.shared if scope == 'shared' else self.paths.config
        atomic_write(root / name, {'schema_version': 1, **fields})

    def catalog(self, sources, skills, scope='shared'):
        self.document(scope, 'catalog.json', sources=sources, skills=skills)

    def select(self, *skills):
        self.document('private', 'machine.json', profiles=[],
                      overrides={skill: 'enabled' for skill in skills})

    def directory(self, name='library', scope='shared'):
        root = self.repo / name if scope == 'shared' else self.root / name
        self.write(root / 'skills/alpha/SKILL.md', 'original\n')
        self.write(root / 'skills/beta/SKILL.md', 'unselected sibling\n')
        self.write(root / 'assets/reference.txt', 'companion\n')
        source = {'type': 'directory', 'path': name if scope == 'shared' else str(root),
                  'provenance': 'authored'}
        return root, source

    def remote(self, name='upstream', shared=False):
        work = self.root / (name + '-work')
        remote = self.root / (name + '.git')
        work.mkdir()
        self.git(work, 'init', '-q', '--initial-branch=main')
        self.write(work / 'skills/alpha/SKILL.md', 'remote original\n')
        self.write(work / 'skills/beta/SKILL.md', 'remote sibling\n')
        self.write(work / 'assets/reference.txt', 'remote companion\n')
        self.git(work, 'add', '.')
        self.git(work, 'commit', '-qm', 'Fixture source')
        self.git(self.root, 'init', '-q', '--bare', str(remote))
        self.git(work, 'remote', 'add', 'origin', str(remote))
        self.git(work, 'push', '-q', 'origin', 'main')
        revision = self.git(work, 'rev-parse', 'HEAD')
        url = str(remote)
        if shared:
            url = 'https://fixtures.invalid/' + name
            self.git(self.root, 'config', '--global', 'url.' + str(remote) + '.insteadOf', url)
        return work, remote, revision, {'type': 'git', 'url': url, 'ref': 'main',
                                        'provenance': 'third-party'}

    def remote_change(self, work, text='remote changed\n'):
        self.write(work / 'skills/alpha/SKILL.md', text)
        self.git(work, 'add', '.')
        self.git(work, 'commit', '-qm', 'Fixture change')
        self.git(work, 'push', '-q', 'origin', 'main')
        return self.git(work, 'rev-parse', 'HEAD')

    def register_remote(self, name='upstream', shared=False):
        work, remote, revision, source = self.remote(name, shared)
        scope = 'shared' if shared else 'private'
        self.catalog({name: source}, {'alpha': {'source': name, 'path': 'skills/alpha'}}, scope)
        self.document(scope, 'lock.json', sources={name: revision})
        self.select('alpha')
        return work, remote, revision

    def activate(self, offline=False):
        with locked(self.paths):
            return sync(Model(self.paths), offline=offline)

    def revise(self, *sources, all_sources=False):
        with locked(self.paths):
            return update(Model(self.paths), list(sources), all_sources=all_sources)

    def active(self):
        return read_json(self.paths.data / 'active.json', {'schema_version': 1, 'active': []})

    def assert_error(self, code, function, *args, **kwargs):
        with self.assertRaises(Error) as raised:
            function(*args, **kwargs)
        self.assertEqual(code, raised.exception.code)
        return raised.exception

    def inventory(self):
        return {str(path.relative_to(self.root)): (path.lstat().st_mode, path.read_bytes())
                for path in self.root.rglob('*') if path.is_file() and not path.is_symlink()}

    def test_initial_inspection_is_read_only_and_empty_sync_is_valid(self):
        before = self.inventory()
        result = inspect(Model(self.paths))
        self.assertTrue(result['selection_valid'])
        self.assertIsNone(result['last_good'])
        self.assertEqual([], result['selected'])
        self.assertEqual(before, self.inventory())
        self.assertFalse(self.paths.data.exists())
        self.activate(offline=True)
        self.assertEqual([], self.active()['active'])
        self.assertEqual([], inspect(Model(self.paths))['last_good']['selected'])

    def test_directory_install_preserves_layout_assets_and_internal_symlinks(self):
        root, source = self.directory()
        (root / 'skills/alpha/reference').symlink_to('../../assets/reference.txt')
        self.catalog({'library': source}, {'alpha': {'source': 'library', 'path': 'skills/alpha'},
                                          'beta': {'source': 'library', 'path': 'skills/beta'}})
        self.select('alpha')
        discovery = self.home / '.agents/skills/existing'
        discovery.parent.mkdir(parents=True)
        discovery.symlink_to(root / 'skills/alpha')
        self.activate()
        result = inspect(Model(self.paths))
        self.assertEqual(['alpha'], [entry['id'] for entry in result['active']])
        installed = Path(result['selected'][0]['installed_directory'])
        self.assertEqual('original\n', (installed / 'SKILL.md').read_text())
        self.assertTrue((installed / 'reference').is_symlink())
        self.assertEqual('companion\n', (installed / 'reference').read_text())
        self.assertEqual('unselected sibling\n', (installed.parent / 'beta/SKILL.md').read_text())
        self.assertEqual(str(root / 'skills/alpha'), os.readlink(discovery))
        self.assertEqual('unmanaged', result['exposure'])

    def test_deselection_activates_empty_set_and_retains_source_and_snapshots(self):
        root, source = self.directory()
        self.catalog({'library': source}, {'alpha': {'source': 'library', 'path': 'skills/alpha'}})
        self.select('alpha')
        self.activate()
        original = self.active()['active'][0]['installed_directory']
        self.select()
        pending = inspect(Model(self.paths))
        self.assertEqual(['alpha'], pending['installed_diff']['removed'])
        self.assertEqual(['alpha'], [entry['id'] for entry in pending['active']])
        self.activate()
        self.assertEqual([], self.active()['active'])
        self.assertEqual('original\n', (Path(original) / 'SKILL.md').read_text())
        self.assertEqual('original\n', (root / 'skills/alpha/SKILL.md').read_text())

    def test_working_edits_are_dirty_fingerprinted_and_originals_are_not_rewritten(self):
        root, source = self.directory()
        self.git(self.repo, 'init', '-q')
        self.git(self.repo, 'add', 'library')
        self.git(self.repo, 'commit', '-qm', 'Fixture authored source')
        self.catalog({'library': source}, {'alpha': {'source': 'library', 'path': 'skills/alpha'}})
        self.select('alpha')
        self.activate()
        clean = inspect(Model(self.paths))['selected'][0]
        self.assertFalse(clean['source_dirty'])
        self.write(root / 'skills/alpha/SKILL.md', 'uncommitted edit\n')
        pending = inspect(Model(self.paths))['selected'][0]
        self.assertTrue(pending['source_dirty'])
        self.assertNotEqual(clean['required_fingerprint'], pending['required_fingerprint'])
        self.assertEqual('outdated', pending['availability'])
        self.activate()
        installed = Path(inspect(Model(self.paths))['selected'][0]['installed_directory'])
        self.assertEqual('uncommitted edit\n', (installed / 'SKILL.md').read_text())
        self.assertEqual('original\n', (Path(clean['installed_directory']) / 'SKILL.md').read_text())
        self.assertEqual('uncommitted edit\n', (root / 'skills/alpha/SKILL.md').read_text())

    def test_failed_multi_source_sync_preserves_active_but_saves_valid_desired_selection(self):
        _, source = self.directory()
        sources = {'library': source}
        skills = {'alpha': {'source': 'library', 'path': 'skills/alpha'}}
        self.catalog(sources, skills)
        self.select('alpha')
        self.activate()
        previous = (self.paths.data / 'active.json').read_bytes()
        sources['missing'] = {'type': 'directory', 'path': 'not-present', 'provenance': 'authored'}
        skills['missing-skill'] = {'source': 'missing', 'path': '.'}
        self.catalog(sources, skills)
        self.select('alpha', 'missing-skill')
        self.assert_error(3, self.activate)
        self.assertEqual(previous, (self.paths.data / 'active.json').read_bytes())
        result = inspect(Model(self.paths))
        self.assertTrue(result['selection_valid'])
        self.assertFalse(result['stale'])
        self.assertEqual(['alpha', 'missing-skill'], result['last_good']['selected'])
        self.assertEqual(['missing-skill'], result['installed_diff']['added'])
        self.assertEqual('unavailable', result['selected'][1]['availability'])

    def test_profile_membership_diff_survives_failed_syncs_until_successful_activation(self):
        root, source = self.directory()
        self.catalog({'library': source}, {
            'alpha': {'source': 'library', 'path': 'skills/alpha'},
            'beta': {'source': 'library', 'path': 'skills/beta'}})
        self.document('shared', 'profiles.json', profiles={'coding': {'skills': ['alpha']}})
        self.document('private', 'machine.json', profiles=['coding'], overrides={})
        self.activate()
        previous = (self.paths.data / 'active.json').read_bytes()
        marker = root / 'skills/beta/SKILL.md'
        content = marker.read_text()
        marker.unlink()
        self.document('shared', 'profiles.json', profiles={'coding': {'skills': ['alpha', 'beta']}})

        for attempt in range(2):
            with self.subTest(attempt=attempt):
                self.assert_error(3, self.activate)
                result = inspect(Model(self.paths))
                self.assertEqual({'added': ['beta'], 'removed': []}, result['desired_diff'])
                self.assertEqual(['alpha', 'beta'], result['last_good']['selected'])
                self.assertEqual(previous, (self.paths.data / 'active.json').read_bytes())

        marker.write_text(content)
        result = self.activate()
        self.assertEqual({'added': ['beta'], 'removed': []}, result['desired_diff'])
        self.assertEqual(['alpha', 'beta'], [entry['id'] for entry in result['active']])
        self.assertEqual({'added': [], 'removed': []}, inspect(Model(self.paths))['desired_diff'])

    def test_first_failed_sync_publishes_no_active_set(self):
        self.catalog({'missing': {'type': 'directory', 'path': 'missing', 'provenance': 'authored'}},
                     {'alpha': {'source': 'missing', 'path': '.'}})
        self.select('alpha')
        self.assert_error(3, self.activate)
        self.assertFalse((self.paths.data / 'active.json').exists())
        self.assertEqual([], inspect(Model(self.paths))['active'])

    def test_exact_cache_sync_is_offline_and_never_fetches_unselected_sources(self):
        work, remote, revision = self.register_remote()
        self.activate()
        self.remote_change(work)
        remote.rename(self.root / 'unavailable-remote')
        catalog = read_json(self.paths.config / 'catalog.json', {})
        catalog['sources']['unselected'] = {'type': 'git', 'url': str(self.root / 'missing.git'),
                                             'ref': 'main', 'provenance': 'third-party'}
        catalog['skills']['unselected'] = {'source': 'unselected', 'path': '.'}
        atomic_write(self.paths.config / 'catalog.json', catalog)
        self.activate(offline=True)
        result = inspect(Model(self.paths))
        self.assertEqual(['alpha'], [entry['id'] for entry in result['active']])
        self.assertEqual(revision, result['selected'][0]['required_revision'])
        self.assertEqual('remote original\n', (Path(result['selected'][0]['installed_directory']) / 'SKILL.md').read_text())
        cache_metadata = list((self.paths.data / 'private/cache').rglob('metadata.json'))
        self.assertEqual({'upstream'}, {json.loads(path.read_text())['source'] for path in cache_metadata})

    def test_missing_exact_cache_cannot_fall_back_to_another_revision(self):
        work, _, _ = self.register_remote()
        self.activate()
        previous = (self.paths.data / 'active.json').read_bytes()
        newer = self.remote_change(work)
        self.document('private', 'lock.json', sources={'upstream': newer})
        self.assert_error(3, self.activate, offline=True)
        self.assertEqual(previous, (self.paths.data / 'active.json').read_bytes())
        selected = inspect(Model(self.paths))['selected'][0]
        self.assertEqual('unavailable', selected['availability'])
        self.assertIsNone(selected['required_fingerprint'])
        self.assertIsNone(selected['installed_directory'])

    def test_missing_lock_is_availability_not_invalid_selection(self):
        self.register_remote()
        (self.paths.config / 'lock.json').unlink()
        result = inspect(Model(self.paths))
        self.assertTrue(result['selection_valid'])
        self.assertFalse(result['stale'])
        self.assertIsNone(result['selected'][0]['required_revision'])
        self.assertEqual('unavailable', result['selected'][0]['availability'])
        self.assert_error(3, self.activate)

    def test_modified_generated_snapshot_conflicts_without_overwriting_local_edit(self):
        _, source = self.directory()
        self.catalog({'library': source}, {'alpha': {'source': 'library', 'path': 'skills/alpha'}})
        self.select('alpha')
        self.activate()
        active_before = (self.paths.data / 'active.json').read_bytes()
        installed = Path(self.active()['active'][0]['installed_directory'])
        self.write(installed / 'SKILL.md', 'unexpected installed edit\n')
        self.select()
        self.assert_error(4, self.activate)
        self.assertEqual(active_before, (self.paths.data / 'active.json').read_bytes())
        self.assertEqual('unexpected installed edit\n', (installed / 'SKILL.md').read_text())

    def test_modified_fetched_content_conflicts_and_is_not_reset(self):
        self.register_remote()
        self.activate()
        active_before = (self.paths.data / 'active.json').read_bytes()
        cached = next((self.paths.data / 'private/cache').rglob('tree/skills/alpha/SKILL.md'))
        cached.write_text('unexpected cache edit\n')
        self.assert_error(4, self.activate, offline=True)
        self.assertEqual(active_before, (self.paths.data / 'active.json').read_bytes())
        self.assertEqual('unexpected cache edit\n', cached.read_text())
        selected = inspect(Model(self.paths))['selected'][0]
        self.assertEqual('conflict', selected['availability'])
        self.assertIsNone(selected['installed_directory'])

    def test_escaping_sibling_symlink_rejects_source_before_activation(self):
        root, source = self.directory()
        external = self.write(self.root / 'external.txt', 'must not copy\n')
        (root / 'assets/escape').symlink_to(external)
        self.catalog({'library': source}, {'alpha': {'source': 'library', 'path': 'skills/alpha'}})
        self.select('alpha')
        self.assert_error(2, self.activate)
        self.assertFalse((self.paths.data / 'active.json').exists())
        self.assertEqual('must not copy\n', external.read_text())

    def test_update_changes_only_requested_lock_and_later_sync_activates_revision(self):
        work, _, old_revision = self.register_remote()
        self.activate()
        before_active = (self.paths.data / 'active.json').read_bytes()
        before_machine = (self.paths.config / 'machine.json').read_bytes()
        new_revision = self.remote_change(work)
        result = self.revise('upstream')
        self.assertEqual([{'source': 'upstream', 'visibility': 'private',
                           'old_revision': old_revision, 'new_revision': new_revision}], result['updates'])
        self.assertEqual(before_active, (self.paths.data / 'active.json').read_bytes())
        self.assertEqual(before_machine, (self.paths.config / 'machine.json').read_bytes())
        self.assertEqual(new_revision, read_json(self.paths.config / 'lock.json', {})['sources']['upstream'])
        self.activate()
        selected = inspect(Model(self.paths))['selected'][0]
        self.assertEqual(new_revision, selected['required_revision'])
        self.assertEqual('remote changed\n', (Path(selected['installed_directory']) / 'SKILL.md').read_text())

    def test_failed_multi_scope_update_preserves_both_lock_documents(self):
        shared_work, _, shared_old, shared_source = self.remote('portable', shared=True)
        _, _, private_old, private_source = self.remote('local')
        private_source['ref'] = 'missing-branch'
        self.catalog({'portable': shared_source}, {}, 'shared')
        self.catalog({'local': private_source}, {}, 'private')
        self.document('shared', 'lock.json', sources={'portable': shared_old})
        self.document('private', 'lock.json', sources={'local': private_old})
        self.remote_change(shared_work)
        before = {scope: (root / 'lock.json').read_bytes() for scope, root in
                  [('shared', self.paths.shared), ('private', self.paths.config)]}
        self.assert_error(3, self.revise, 'portable', 'local')
        self.assertEqual(before['shared'], (self.paths.shared / 'lock.json').read_bytes())
        self.assertEqual(before['private'], (self.paths.config / 'lock.json').read_bytes())
        self.assertFalse((self.paths.data / 'active.json').exists())

    def test_update_rejects_missing_and_ambiguous_tracking_refs_without_lock_changes(self):
        work, _, _ = self.register_remote()
        self.git(work, 'tag', 'main')
        self.git(work, 'push', '-q', 'origin', 'refs/tags/main')
        before = (self.paths.config / 'lock.json').read_bytes()
        self.assert_error(3, self.revise, 'upstream')
        self.assertEqual(before, (self.paths.config / 'lock.json').read_bytes())
        catalog = read_json(self.paths.config / 'catalog.json', {})
        catalog['sources']['upstream']['ref'] = 'not-found'
        atomic_write(self.paths.config / 'catalog.json', catalog)
        self.assert_error(3, self.revise, 'upstream')
        self.assertEqual(before, (self.paths.config / 'lock.json').read_bytes())

    def test_annotated_tag_update_creates_exact_commit_lock_without_installing(self):
        work, _, revision = self.register_remote()
        self.git(work, 'tag', '-a', 'release', '-m', 'Fixture annotated tag')
        self.git(work, 'push', '-q', 'origin', 'refs/tags/release')
        catalog = read_json(self.paths.config / 'catalog.json', {})
        catalog['sources']['upstream']['ref'] = 'refs/tags/release'
        atomic_write(self.paths.config / 'catalog.json', catalog)
        (self.paths.config / 'lock.json').unlink()
        result = self.revise('upstream')
        self.assertIsNone(result['updates'][0]['old_revision'])
        self.assertEqual(revision, result['updates'][0]['new_revision'])
        self.assertFalse((self.paths.data / 'active.json').exists())
        self.assertFalse((self.paths.data / 'private/snapshots').exists())

    def test_update_requires_explicit_remote_targets(self):
        _, source = self.directory()
        self.catalog({'directory': source}, {})
        self.assert_error(2, self.revise)
        self.assert_error(2, self.revise, 'directory')
        self.assert_error(2, self.revise, 'unknown')
        self.assert_error(2, self.revise, 'directory', all_sources=True)

    def test_update_all_includes_remote_sources_but_not_directory_sources(self):
        _, directory_source = self.directory()
        _, _, revision, git_source = self.remote()
        self.catalog({'directory': directory_source}, {})
        self.catalog({'remote': git_source}, {}, 'private')
        result = self.revise(all_sources=True)
        self.assertEqual(['remote'], [entry['source'] for entry in result['updates']])
        self.assertEqual(revision, read_json(self.paths.config / 'lock.json', {})['sources']['remote'])
        self.assertFalse((self.paths.shared / 'lock.json').exists())

    def test_private_and_shared_installations_and_cache_metadata_remain_separate(self):
        _, _, shared_revision, shared_source = self.remote('portable', shared=True)
        _, _, private_revision, private_source = self.remote('private-fixture')
        self.catalog({'portable': shared_source}, {'shared-skill': {'source': 'portable', 'path': 'skills/alpha'}})
        self.catalog({'private-fixture': private_source},
                     {'private-skill': {'source': 'private-fixture', 'path': 'skills/alpha'}}, 'private')
        self.document('shared', 'lock.json', sources={'portable': shared_revision})
        self.document('private', 'lock.json', sources={'private-fixture': private_revision})
        self.select('shared-skill', 'private-skill')
        self.activate()
        records = {entry['id']: entry for entry in inspect(Model(self.paths))['selected']}
        self.assertTrue(Path(records['shared-skill']['installed_directory']).is_relative_to(self.paths.data / 'shared'))
        self.assertTrue(Path(records['private-skill']['installed_directory']).is_relative_to(self.paths.data / 'private'))
        for path in [*self.paths.shared.rglob('*.json'), *(self.paths.data / 'shared').rglob('metadata.json')]:
            self.assertNotIn('private-fixture', path.read_text())
            self.assertNotIn('private-skill', path.read_text())
        self.assertEqual(0o700, (self.paths.data / 'private').stat().st_mode & 0o777)
        self.assertEqual(0o600, (self.paths.data / 'active.json').stat().st_mode & 0o777)

    def test_invalid_selection_retains_last_good_without_returning_current_paths(self):
        _, source = self.directory()
        self.catalog({'library': source}, {'alpha': {'source': 'library', 'path': 'skills/alpha'}})
        self.select('alpha')
        self.activate()
        self.select('unknown')
        before = self.inventory()
        result = inspect(Model(self.paths))
        self.assertFalse(result['selection_valid'])
        self.assertTrue(result['stale'])
        self.assertIsNone(result['desired'])
        self.assertEqual([], result['selected'])
        self.assertEqual(['alpha'], result['last_good']['selected'])
        self.assertEqual(['alpha'], [entry['id'] for entry in result['active']])
        self.assertEqual(before, self.inventory())
        self.assert_error(2, self.activate)
        self.assertEqual(['alpha'], read_json(self.paths.config / 'last-selection.json', {})['selection']['selected'])

    def test_read_only_inspection_neither_fetches_missing_remote_nor_rewrites_git_index(self):
        work, remote, _ = self.register_remote()
        remote.rename(self.root / 'unavailable-remote')
        before = self.inventory()
        result = inspect(Model(self.paths))
        self.assertEqual('unavailable', result['selected'][0]['availability'])
        self.assertIsNone(result['selected'][0]['required_fingerprint'])
        self.assertEqual(before, self.inventory())
        self.assertFalse(self.paths.data.exists())
        self.assertEqual('remote original\n', (work / 'skills/alpha/SKILL.md').read_text())

    def test_source_disappearance_is_not_stale_selection_and_retains_active_diagnostics(self):
        root, source = self.directory()
        self.catalog({'library': source}, {'alpha': {'source': 'library', 'path': 'skills/alpha'}})
        self.select('alpha')
        self.activate()
        root.rename(self.repo / 'moved-library')
        result = inspect(Model(self.paths))
        self.assertTrue(result['selection_valid'])
        self.assertFalse(result['stale'])
        self.assertEqual('unavailable', result['selected'][0]['availability'])
        self.assertIsNone(result['selected'][0]['installed_directory'])
        self.assertEqual(['alpha'], [entry['id'] for entry in result['active']])

    def test_unsupported_active_manifest_schema_stops_activation(self):
        self.select()
        atomic_write(self.paths.data / 'active.json', {'schema_version': 99, 'active': []})
        before = (self.paths.data / 'active.json').read_bytes()
        self.assert_error(2, self.activate)
        self.assertEqual(before, (self.paths.data / 'active.json').read_bytes())
        result = inspect(Model(self.paths))
        self.assertFalse(result['selection_valid'])
        self.assertTrue(result['errors'])

    def test_activation_publication_failure_keeps_previous_whole_set(self):
        _, source = self.directory()
        self.catalog({'library': source}, {'alpha': {'source': 'library', 'path': 'skills/alpha'},
                                          'beta': {'source': 'library', 'path': 'skills/beta'}})
        self.select('alpha')
        self.activate()
        before = (self.paths.data / 'active.json').read_bytes()
        self.select('alpha', 'beta')
        replace = os.replace
        failed = False

        def fail_active_publication(source_path, destination):
            nonlocal failed
            if Path(destination) == self.paths.data / 'active.json' and not failed:
                failed = True
                raise OSError('Fixture interruption at atomic activation boundary')
            return replace(source_path, destination)

        # Double: filesystem publication failure at the external atomic-replace boundary.
        with patch('os.replace', side_effect=fail_active_publication):
            self.assert_error(3, self.activate)
        self.assertEqual(before, (self.paths.data / 'active.json').read_bytes())
        self.assertEqual(['alpha'], [entry['id'] for entry in self.active()['active']])
        self.assertEqual(['alpha', 'beta'], inspect(Model(self.paths))['last_good']['selected'])

    def test_failed_later_download_retains_exact_earlier_download_for_offline_retry(self):
        _, _, revision, source = self.remote('available')
        self.catalog({'a-available': source,
                      'z-missing': {'type': 'git', 'url': str(self.root / 'missing.git'),
                                    'ref': 'main', 'provenance': 'third-party'}},
                     {'alpha': {'source': 'a-available', 'path': 'skills/alpha'},
                      'missing': {'source': 'z-missing', 'path': '.'}}, 'private')
        self.document('private', 'lock.json', sources={'a-available': revision, 'z-missing': 'a' * 40})
        self.select('alpha', 'missing')
        self.assert_error(3, self.activate)
        self.assertFalse((self.paths.data / 'active.json').exists())
        cached = list((self.paths.data / 'private/cache').rglob('metadata.json'))
        self.assertEqual({'a-available'}, {json.loads(path.read_text())['source'] for path in cached})
        self.select('alpha')
        self.activate(offline=True)
        self.assertEqual(['alpha'], [entry['id'] for entry in self.active()['active']])

    def test_cache_schema_error_does_not_replace_cache_or_active_installation(self):
        self.register_remote()
        self.activate()
        active_before = (self.paths.data / 'active.json').read_bytes()
        metadata = next((self.paths.data / 'private/cache').rglob('metadata.json'))
        atomic_write(metadata, {'schema_version': 99})
        self.assert_error(2, self.activate, offline=True)
        self.assertEqual(active_before, (self.paths.data / 'active.json').read_bytes())
        self.assertEqual({'schema_version': 99}, json.loads(metadata.read_text()))

    def test_changed_generated_link_is_a_conflict_not_a_new_source_dependency(self):
        root, source = self.directory()
        (root / 'skills/alpha/reference').symlink_to('../../assets/reference.txt')
        self.catalog({'library': source}, {'alpha': {'source': 'library', 'path': 'skills/alpha'}})
        self.select('alpha')
        self.activate()
        installed = Path(self.active()['active'][0]['installed_directory'])
        link = installed / 'reference'
        link.unlink()
        outside = self.write(self.root / 'outside.txt', 'outside\n')
        link.symlink_to(outside)
        self.assert_error(4, self.activate)
        self.assertEqual(str(outside), os.readlink(link))
        self.assertEqual('conflict', inspect(Model(self.paths))['selected'][0]['availability'])

    def test_scope_store_cannot_be_redirected_into_an_external_directory(self):
        self.register_remote()
        external = self.root / 'external-store'
        external.mkdir()
        self.paths.data.mkdir(parents=True)
        (self.paths.data / 'private').symlink_to(external, target_is_directory=True)
        self.assert_error(4, self.activate)
        self.assertEqual([], list(external.iterdir()))
        self.assertFalse((self.paths.data / 'active.json').exists())

    def test_missing_selected_subdirectory_preserves_the_previous_set(self):
        _, source = self.directory()
        self.catalog({'library': source}, {'alpha': {'source': 'library', 'path': 'skills/alpha'},
                                          'absent': {'source': 'library', 'path': 'skills/absent'}})
        self.select('alpha')
        self.activate()
        before = (self.paths.data / 'active.json').read_bytes()
        self.select('alpha', 'absent')
        self.assert_error(3, self.activate)
        self.assertEqual(before, (self.paths.data / 'active.json').read_bytes())
        records = {entry['id']: entry for entry in inspect(Model(self.paths))['selected']}
        self.assertEqual('unavailable', records['absent']['availability'])
        self.assertEqual('installed', records['alpha']['availability'])

    def test_unchanged_sources_reuse_snapshots_and_common_source_revision(self):
        self.register_remote()
        catalog = read_json(self.paths.config / 'catalog.json', {})
        catalog['skills']['beta'] = {'source': 'upstream', 'path': 'skills/beta'}
        atomic_write(self.paths.config / 'catalog.json', catalog)
        self.select('alpha', 'beta')
        self.activate()
        before = (self.paths.data / 'active.json').read_bytes()
        manifest = self.active()
        snapshots = manifest['snapshots']
        self.assertEqual(['upstream'], [entry['source'] for entry in snapshots])
        self.assertEqual({manifest['active'][0]['required_revision']},
                         {entry['required_revision'] for entry in manifest['active']})
        self.activate(offline=True)
        self.assertEqual(before, (self.paths.data / 'active.json').read_bytes())
        self.assertEqual(snapshots, self.active()['snapshots'])

    def test_lock_publication_failure_rolls_back_both_visibility_scopes(self):
        shared_work, _, shared_old, shared_source = self.remote('a-portable', shared=True)
        private_work, _, private_old, private_source = self.remote('z-local')
        self.catalog({'a-portable': shared_source}, {}, 'shared')
        self.catalog({'z-local': private_source}, {}, 'private')
        self.document('shared', 'lock.json', sources={'a-portable': shared_old})
        self.document('private', 'lock.json', sources={'z-local': private_old})
        shared_before = (self.paths.shared / 'lock.json').read_bytes()
        private_before = (self.paths.config / 'lock.json').read_bytes()
        self.remote_change(shared_work)
        self.remote_change(private_work)
        replace, failed = os.replace, False

        def fail_private_lock(source_path, destination):
            nonlocal failed
            if Path(destination) == self.paths.config / 'lock.json' and not failed:
                failed = True
                raise OSError('Fixture private lock publication failure')
            return replace(source_path, destination)

        # Double: a filesystem failure while publishing the second lock document.
        with patch('os.replace', side_effect=fail_private_lock):
            self.assert_error(3, self.revise, all_sources=True)
        self.assertEqual(shared_before, (self.paths.shared / 'lock.json').read_bytes())
        self.assertEqual(private_before, (self.paths.config / 'lock.json').read_bytes())
        self.assertFalse((self.paths.data / 'active.json').exists())

    def test_post_rename_activation_failure_restores_previous_active_manifest(self):
        _, source = self.directory()
        self.catalog({'library': source}, {'alpha': {'source': 'library', 'path': 'skills/alpha'},
                                          'beta': {'source': 'library', 'path': 'skills/beta'}})
        self.select('alpha')
        self.activate()
        manifest = self.paths.data / 'active.json'
        before = manifest.read_bytes()
        self.select('alpha', 'beta')
        fsync, failed = os.fsync, False

        def fail_active_directory_sync(fd):
            nonlocal failed
            if (not failed and os.fstat(fd).st_ino == self.paths.data.stat().st_ino and
                    manifest.read_bytes() != before):
                failed = True
                raise OSError('Fixture post-rename directory sync failure')
            return fsync(fd)

        # Double: directory durability failure after the external atomic rename.
        with patch('os.fsync', side_effect=fail_active_directory_sync):
            self.assert_error(3, self.activate)
        self.assertTrue(failed)
        self.assertEqual(before, manifest.read_bytes())
        self.assertEqual(['alpha'], [entry['id'] for entry in self.active()['active']])


    def test_working_source_inspection_does_not_refresh_the_git_index(self):
        root, source = self.directory()
        self.git(self.repo, 'init', '-q')
        self.git(self.repo, 'add', 'library')
        self.git(self.repo, 'commit', '-qm', 'Fixture tracked source')
        self.catalog({'library': source}, {'alpha': {'source': 'library', 'path': 'skills/alpha'}})
        self.select('alpha')
        self.write(root / 'assets/reference.txt', 'working companion change\n')
        before = self.inventory()
        result = inspect(Model(self.paths))
        self.assertTrue(result['selected'][0]['source_dirty'])
        self.assertEqual('not-installed', result['selected'][0]['availability'])
        self.assertEqual(before, self.inventory())
        self.assertFalse(self.paths.data.exists())

    def test_two_machine_homes_activate_independent_shared_selections(self):
        _, source = self.directory()
        self.catalog({'library': source}, {'alpha': {'source': 'library', 'path': 'skills/alpha'},
                                          'beta': {'source': 'library', 'path': 'skills/beta'}})
        self.select('alpha')
        self.activate(offline=True)
        first_before = (self.paths.data / 'active.json').read_bytes()
        second_home = self.root / 'second-home'
        second_home.mkdir()
        with patch.dict(os.environ, {'HOME': str(second_home),
                                   'XDG_CONFIG_HOME': str(second_home / '.config'),
                                   'XDG_DATA_HOME': str(second_home / '.local/share')}):
            second_paths = Paths(self.repo, second_home)
            self.assertEqual([], inspect(Model(second_paths))['selected'])
            atomic_write(second_paths.config / 'machine.json',
                         {'schema_version': 1, 'profiles': [], 'overrides': {'beta': 'enabled'}})
            with locked(second_paths):
                sync(Model(second_paths), offline=True)
            second = inspect(Model(second_paths))
            self.assertEqual(['beta'], [entry['id'] for entry in second['active']])
            self.assertTrue(Path(second['selected'][0]['installed_directory']).is_relative_to(second_paths.data))
        self.assertEqual(first_before, (self.paths.data / 'active.json').read_bytes())
        self.assertEqual(['alpha'], [entry['id'] for entry in inspect(Model(self.paths))['active']])

    def test_remote_escaping_symlink_fails_without_retaining_unsafe_content(self):
        work, _, _ = self.register_remote()
        outside = self.write(self.root / 'outside.txt', 'outside fixture\n')
        (work / 'assets/escape').symlink_to(outside)
        self.git(work, 'add', '.')
        self.git(work, 'commit', '-qm', 'Fixture escaping source link')
        self.git(work, 'push', '-q', 'origin', 'main')
        revision = self.git(work, 'rev-parse', 'HEAD')
        self.document('private', 'lock.json', sources={'upstream': revision})
        self.assert_error(2, self.activate)
        self.assertFalse((self.paths.data / 'active.json').exists())
        self.assertEqual([], list((self.paths.data / 'private/cache').rglob('metadata.json')))
        self.assertEqual('outside fixture\n', outside.read_text())

    def test_same_tree_but_changed_fetched_head_is_a_conflict(self):
        self.register_remote()
        self.activate()
        tree = next((self.paths.data / 'private/cache').rglob('tree/.git')).parent
        self.git(tree, 'commit', '-q', '--allow-empty', '-m', 'Fixture unexpected managed commit')
        unexpected = self.git(tree, 'rev-parse', 'HEAD')
        active_before = (self.paths.data / 'active.json').read_bytes()
        self.assert_error(4, self.activate, offline=True)
        self.assertEqual(unexpected, self.git(tree, 'rev-parse', 'HEAD'))
        self.assertEqual(active_before, (self.paths.data / 'active.json').read_bytes())

    def test_snapshot_metadata_schema_error_does_not_publish_a_new_set(self):
        _, source = self.directory()
        self.catalog({'library': source}, {'alpha': {'source': 'library', 'path': 'skills/alpha'}})
        self.select('alpha')
        self.activate()
        before = (self.paths.data / 'active.json').read_bytes()
        metadata = Path(self.active()['snapshots'][0]['directory']).parent / 'metadata.json'
        atomic_write(metadata, {'schema_version': 99})
        self.assert_error(2, self.activate)
        self.assertEqual(before, (self.paths.data / 'active.json').read_bytes())
        self.assertFalse(inspect(Model(self.paths))['selection_valid'])


    def test_existing_directory_without_skill_marker_is_unavailable_until_repaired(self):
        root, source = self.directory()
        (root / 'skills/empty').mkdir()
        self.catalog({'library': source}, {'empty': {'source': 'library', 'path': 'skills/empty'}})
        self.select('empty')
        result = inspect(Model(self.paths))
        self.assertTrue(result['selection_valid'])
        self.assertFalse(result['stale'])
        self.assertEqual('unavailable', result['selected'][0]['availability'])
        self.assertIsNone(result['selected'][0]['installed_directory'])
        self.assert_error(3, self.activate)
        self.assertFalse((self.paths.data / 'active.json').exists())
        self.write(root / 'skills/empty/SKILL.md', 'plain skill instructions\n')
        self.activate()
        self.assertEqual('installed', inspect(Model(self.paths))['selected'][0]['availability'])

    def test_redirected_snapshot_root_is_a_content_conflict_not_stale_selection(self):
        _, source = self.directory()
        self.catalog({'library': source}, {'alpha': {'source': 'library', 'path': 'skills/alpha'}})
        self.select('alpha')
        self.activate()
        tree = Path(self.active()['snapshots'][0]['directory'])
        tree.rename(tree.with_name('retained-original-tree'))
        outside = self.root / 'outside-directory'
        outside.mkdir()
        tree.symlink_to(outside, target_is_directory=True)
        self.assert_error(4, self.activate)
        result = inspect(Model(self.paths))
        self.assertTrue(result['selection_valid'])
        self.assertFalse(result['stale'])
        self.assertEqual('conflict', result['selected'][0]['availability'])
        self.assertIsNone(result['selected'][0]['installed_directory'])
        self.assertEqual(str(outside), os.readlink(tree))


if __name__ == '__main__':
    unittest.main()
