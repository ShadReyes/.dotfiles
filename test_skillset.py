"""Consumer-visible selection and configuration boundaries, using isolated homes."""

from contextlib import contextmanager
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent / 'scripts'))
from skillset_lib.core import Error, Model, Paths, atomic_write, contained, fingerprint, locked, write_many

CLI = Path(__file__).parent / 'scripts/skillset'


def document(**fields):
    return {'schema_version': 1, **fields}


@contextmanager
def world():
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        repo, home = root / 'repo', root / 'home'
        (repo / 'skills/bundle/alpha').mkdir(parents=True)
        (repo / 'skills/bundle/beta').mkdir()
        for name in ('alpha', 'beta'):
            (repo / f'skills/bundle/{name}/SKILL.md').write_text(f'---\nname: {name}\n---\n{name}\n')
        home.mkdir()
        # Environment is an external boundary; each fixture owns its machine roots.
        with patch.dict(os.environ, {'HOME': str(home), 'XDG_CONFIG_HOME': str(home / '.config'), 'XDG_DATA_HOME': str(home / '.local/share')}, clear=False):
            paths = Paths(repo)
            atomic_write(paths.shared / 'catalog.json', document(
                sources={'bundle': {'type': 'directory', 'path': 'skills/bundle', 'provenance': 'third-party'}},
                skills={'alpha': {'source': 'bundle', 'path': 'alpha'}, 'beta': {'source': 'bundle', 'path': 'beta'}}))
            atomic_write(paths.shared / 'profiles.json', document(profiles={'coding': {'name': 'Coding', 'skills': ['alpha']}, 'review': {'skills': ['alpha', 'beta']}}))
            yield paths


def run_cli(paths, *arguments, code=0):
    result = subprocess.run([str(CLI), '--repo', str(paths.repo), *arguments], capture_output=True, text=True, env=os.environ.copy())
    if result.returncode != code:
        raise AssertionError(f'{arguments}: expected {code}, got {result.returncode}\n{result.stdout}\n{result.stderr}')
    return json.loads(result.stdout) if result.stdout else None


class SelectionContract(unittest.TestCase):
    def test_explicit_overrides_replace_each_other_and_reset_inherits_union(self):
        with world() as paths:
            run_cli(paths, 'profile', 'select', 'coding', 'review')
            disabled = run_cli(paths, 'disable', 'alpha')['selection']
            self.assertEqual(disabled['selected'], ['beta'])
            enabled = run_cli(paths, 'enable', 'alpha')['selection']
            self.assertEqual(enabled['selected'], ['alpha', 'beta'])
            self.assertEqual(enabled['overrides'], {'alpha': 'enabled'})
            inherited = run_cli(paths, 'reset', 'alpha')['selection']
            self.assertEqual(inherited['reasons']['alpha'], ['profile:coding', 'profile:review'])
            run_cli(paths, 'profile', 'deselect', 'review')
            self.assertEqual(Model(paths).selection()['selected'], ['alpha'])

    def test_two_machine_selections_are_independent_after_shared_profile_changes(self):
        with world() as paths:
            run_cli(paths, 'profile', 'select', 'coding')
            run_cli(paths, 'disable', 'beta')
            another_home = paths.home.parent / 'another-home'
            with patch.dict(os.environ, {'HOME': str(another_home), 'XDG_CONFIG_HOME': str(another_home / '.config'), 'XDG_DATA_HOME': str(another_home / '.local/share')}):
                another = Paths(paths.repo)
                self.assertEqual(Model(another).selection()['selected'], [])
                run_cli(another, 'enable', 'beta')
                self.assertEqual(Model(another).selection()['selected'], ['beta'])
            run_cli(paths, 'profile', 'add', 'coding', 'beta')
            self.assertEqual(Model(paths).selection()['selected'], ['alpha'])
            self.assertEqual(Model(another).selection()['selected'], ['beta'])

    def test_stale_overrides_can_be_removed_without_silently_discarding_other_choices(self):
        with world() as paths:
            run_cli(paths, 'enable', 'alpha')
            machine = document(profiles=[], overrides={'alpha': 'enabled', 'removed': 'disabled'})
            atomic_write(paths.config / 'machine.json', machine)
            with self.assertRaises(Error):
                Model(paths).validate()
            repaired = run_cli(paths, 'reset', 'removed')['selection']
            self.assertEqual(repaired['selected'], ['alpha'])
            self.assertEqual(repaired['overrides'], {'alpha': 'enabled'})

    def test_display_name_changes_preserve_profile_identity(self):
        with world() as paths:
            run_cli(paths, 'profile', 'select', 'coding')
            run_cli(paths, 'profile', 'rename', 'coding', '--name', 'Build')
            model = Model(paths)
            self.assertEqual(model.selection()['profiles'], ['coding'])
            self.assertEqual(model.selection()['selected'], ['alpha'])
            self.assertEqual(model.profiles['coding']['name'], 'Build')


class PrivacyAndValidation(unittest.TestCase):
    def test_shared_only_validation_does_not_read_malformed_private_documents(self):
        with world() as paths:
            paths.config.mkdir(parents=True)
            (paths.config / 'catalog.json').write_text('not JSON')
            result = run_cli(paths, 'validate', '--shared-only', '--json')
            self.assertTrue(result['valid'])
            run_cli(paths, 'validate', '--json', code=2)

    def test_private_registration_never_enters_shared_files_and_mixed_profiles_fail(self):
        with world() as paths:
            original = (paths.shared / 'catalog.json').read_bytes()
            private = paths.home / 'authored'
            private.mkdir()
            (private / 'SKILL.md').write_text('Private fixture')
            run_cli(paths, 'source', 'add', 'local-source', '--directory', str(private), '--private', '--provenance', 'authored')
            run_cli(paths, 'add', 'local-skill', '--source', 'local-source', '--path', '.', '--private')
            run_cli(paths, 'profile', 'create', 'local-profile', '--private')
            run_cli(paths, 'profile', 'add', 'local-profile', 'local-skill')
            run_cli(paths, 'profile', 'select', 'coding', 'local-profile')
            self.assertEqual(Model(paths).selection()['selected'], ['alpha', 'local-skill'])
            run_cli(paths, 'profile', 'add', 'coding', 'local-skill', code=2)
            self.assertEqual((paths.shared / 'catalog.json').read_bytes(), original)
            shared = Model(paths, shared_only=True)
            shared.validate()
            self.assertNotIn('local-skill', shared.skills)

    def test_duplicate_identity_and_referenced_deletion_preserve_configuration(self):
        with world() as paths:
            before = (paths.shared / 'catalog.json').read_bytes()
            run_cli(paths, 'add', 'alpha', '--source', 'bundle', '--path', 'beta', code=2)
            run_cli(paths, 'remove', 'alpha', code=2)
            run_cli(paths, 'source', 'remove', 'bundle', code=2)
            self.assertEqual((paths.shared / 'catalog.json').read_bytes(), before)

    def test_traversal_and_escaping_symlinks_are_rejected(self):
        with world() as paths:
            for relative in ('../outside', '/absolute', ''):
                with self.subTest(relative=relative), self.assertRaises(Error):
                    contained(paths.repo, relative)
            (paths.repo / 'skills/bundle/escape').symlink_to(paths.home, target_is_directory=True)
            with self.assertRaises(Error):
                fingerprint(paths.repo / 'skills/bundle')
            run_cli(paths, 'add', 'escape', '--source', 'bundle', '--path', 'escape', code=2)

    def test_local_roots_cannot_be_inside_dotfiles_or_harness_discovery(self):
        with world() as paths:
            for base in (paths.repo / 'local', paths.home / '.agents/skills'):
                with patch.dict(os.environ, {'XDG_DATA_HOME': str(base)}), self.assertRaises(Error):
                    Paths(paths.repo)

    def test_duplicate_json_keys_and_unsupported_schema_are_invalid_configuration(self):
        with world() as paths:
            catalog = paths.shared / 'catalog.json'
            for text in ('{"schema_version":1,"sources":{},"skills":{},"skills":{}}', '{"schema_version":2,"sources":{},"skills":{}}'):
                with self.subTest(text=text):
                    catalog.write_text(text)
                    result = run_cli(paths, 'validate', '--json', code=2)
                    self.assertFalse(result['valid'])

    def test_malformed_skill_source_references_are_configuration_errors(self):
        with world() as paths:
            catalog = json.loads((paths.shared / 'catalog.json').read_text())
            for bad in ([], {}, 1, None):
                with self.subTest(source=bad):
                    catalog['skills']['alpha']['source'] = bad
                    atomic_write(paths.shared / 'catalog.json', catalog)
                    with self.assertRaises(Error) as caught:
                        Model(paths).validate()
                    self.assertEqual(caught.exception.code, 2)

    def test_malformed_machine_shapes_fail_before_mutation(self):
        with world() as paths:
            for machine, command in ((document(profiles='other', overrides={}), ['profile', 'select', 'coding']), (document(profiles=[], overrides=[]), ['enable', 'alpha'])):
                with self.subTest(machine=machine):
                    atomic_write(paths.config / 'machine.json', machine)
                    before = (paths.config / 'machine.json').read_bytes()
                    run_cli(paths, *command, code=2)
                    self.assertEqual((paths.config / 'machine.json').read_bytes(), before)

    def test_failed_publication_restores_every_document_even_after_rename(self):
        with world() as paths:
            first, second = paths.config / 'first.json', paths.config / 'second.json'
            atomic_write(first, document(value='old-first'))
            atomic_write(second, document(value='old-second'))
            fsync = os.fsync
            calls = 0

            def failing_fsync(fd):
                nonlocal calls
                calls += 1
                if calls == 4:
                    raise OSError('simulated durability failure after second rename')
                return fsync(fd)

            # fsync is the external filesystem durability boundary.
            with patch('os.fsync', side_effect=failing_fsync), self.assertRaises(OSError):
                write_many({first: document(value='new-first'), second: document(value='new-second')})
            self.assertEqual(json.loads(first.read_text())['value'], 'old-first')
            self.assertEqual(json.loads(second.read_text())['value'], 'old-second')

    def test_concurrent_mutations_do_not_change_machine_intent(self):
        with world() as paths:
            with locked(paths):
                run_cli(paths, 'enable', 'alpha', code=4)
            self.assertEqual(Model(paths).selection()['selected'], [])


    def test_broken_catalog_retains_stale_selection_in_human_and_json_status(self):
        with world() as paths:
            run_cli(paths, 'enable', 'alpha')
            run_cli(paths, 'sync')
            (paths.shared / 'catalog.json').write_text('broken JSON')
            before = {path: path.read_bytes() for root in (paths.config, paths.data, paths.shared) for path in root.rglob('*') if path.is_file()}
            result = run_cli(paths, 'resolve', '--json', code=2)
            self.assertTrue(result['stale'])
            self.assertEqual(result['last_good']['selected'], ['alpha'])
            self.assertEqual([entry['id'] for entry in result['active']], ['alpha'])
            human = subprocess.run([str(CLI), '--repo', str(paths.repo), 'status'], capture_output=True, text=True)
            self.assertEqual(human.returncode, 2)
            self.assertIn('stale', human.stdout)
            after = {path: path.read_bytes() for root in (paths.config, paths.data, paths.shared) for path in root.rglob('*') if path.is_file()}
            self.assertEqual(after, before)


if __name__ == '__main__':
    unittest.main()
