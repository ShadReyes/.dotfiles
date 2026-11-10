"""Behavioral migration tests; run: python3 -m unittest test_skillset_migration."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent / 'scripts'))
from skillset_lib.core import Error, Model, Paths
from skillset_lib.migration import apply, plan


class MigrationFixture:
    def __init__(self, base):
        self.repo = Path(base).resolve() / 'repo'
        self.home = Path(base).resolve() / 'home'
        self.repo.mkdir()
        self.home.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)
        self.paths = Paths(self.repo, self.home)

    def source(self, name='bundle', nested=False):
        root = self.repo / 'skills' / name
        skill = root / 'skills' / 'nested' if nested else root
        skill.mkdir(parents=True)
        (skill / 'SKILL.md').write_text('---\nname: original-name\n---\nLocally modified instructions.\n')
        (root / 'companion.txt').write_text('Preserved supporting asset.\n')
        return root

    def reviewed(self, classification='shared', source_id='bundle', private_approved=False):
        result = plan(Model(self.paths))
        path = Path(result['plan'])
        document = json.loads(path.read_text())
        for entry in document['entries']:
            entry.update(classification=classification, source_id=source_id,
                         provenance='third-party', private_approved=private_approved)
            for index, skill in enumerate(entry['skills']):
                skill['id'] = f'{source_id}-skill-{index}'
        path.write_text(json.dumps(document))
        return path, document

    def discovery(self, source):
        links = []
        for root in ('.claude/skills', '.agents/skills'):
            directory = self.home / root
            directory.mkdir(parents=True)
            link = directory / source.name
            link.symlink_to(str(source) + '/')
            links.append(link)
        return links

    def legacy_sync(self):
        shutil.copyfile(Path(__file__).parent / 'sync-skills.sh', self.repo / 'sync-skills.sh')
        (self.repo / 'agents').mkdir()
        (self.repo / 'commands').mkdir()
        (self.repo / 'agents/helper.toml').write_text(
            'name = "helper"\ndescription = "Generic helper"\n'
            'developer_instructions = """\nGeneric agent instructions.\n"""\n')
        (self.repo / 'commands/example.md').write_text('Generic command instructions.\n')


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.environment = patch.dict(os.environ, {'XDG_CONFIG_HOME': '', 'XDG_DATA_HOME': ''})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.fixture = MigrationFixture(self.temporary.name)

    def test_plan_is_local_unclassified_and_discovers_exact_nested_skills(self):
        root = self.fixture.source(nested=True)
        (root / 'examples').mkdir()
        (root / 'examples' / 'SKILL.md').write_text('Example skill')
        links = self.fixture.discovery(root)

        result = plan(Model(self.fixture.paths))
        document = json.loads(Path(result['plan']).read_text())

        self.assertEqual(result['unclassified'], 1)
        self.assertTrue(Path(result['plan']).is_relative_to(self.fixture.paths.data))
        self.assertFalse(self.fixture.paths.shared.exists())
        self.assertEqual(document['entries'][0]['classification'], 'unclassified')
        self.assertFalse(document['entries'][0]['private_approved'])
        self.assertEqual([skill['path'] for skill in document['entries'][0]['skills']],
                         ['examples', 'skills/nested'])
        self.assertEqual({reference['path'] for reference in document['references']},
                         {str(link) for link in links})

    def test_shared_import_preserves_modified_bundle_and_does_not_select(self):
        root = self.fixture.source(nested=True)
        before = (root / 'skills/nested/SKILL.md').read_bytes()
        path, _ = self.fixture.reviewed()

        apply(Model(self.fixture.paths), path)
        model = Model(self.fixture.paths)

        self.assertEqual(model.sources['bundle']['path'], 'skills/bundle')
        self.assertEqual(model.skills['bundle-skill-0']['path'], 'skills/nested')
        self.assertEqual(model.sources['bundle']['provenance'], 'third-party')
        self.assertEqual((root / 'skills/nested/SKILL.md').read_bytes(), before)
        self.assertEqual((root / 'companion.txt').read_text(), 'Preserved supporting asset.\n')
        self.assertEqual(model.selection()['selected'], [])
        self.assertFalse((self.fixture.paths.config / 'machine.json').exists())

    def test_unclassified_and_missing_private_approval_fail_without_writes(self):
        original = self.fixture.source()
        unreviewed = Path(plan(Model(self.fixture.paths))['plan'])
        with self.assertRaises(Error):
            apply(Model(self.fixture.paths), unreviewed)
        path, _ = self.fixture.reviewed('private')
        with self.assertRaises(Error):
            apply(Model(self.fixture.paths), path)
        self.assertTrue(original.is_dir())
        self.assertFalse(original.is_symlink())
        self.assertFalse(self.fixture.paths.shared.exists())
        self.assertFalse((self.fixture.paths.config / 'catalog.json').exists())

    def test_changed_source_inventory_configuration_and_discovery_reject_plan(self):
        for change in ('source', 'inventory', 'configuration', 'link', 'git-index'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as directory:
                fixture = MigrationFixture(directory)
                root = fixture.source()
                links = fixture.discovery(root)
                path, _ = fixture.reviewed()
                if change == 'source':
                    (root / 'companion.txt').write_text('Changed after review')
                elif change == 'inventory':
                    fixture.source('new-source')
                elif change == 'configuration':
                    fixture.paths.config.mkdir(parents=True)
                    (fixture.paths.config / 'machine.json').write_text(
                        '{"schema_version":1,"profiles":[],"overrides":{}}')
                elif change == 'link':
                    links[0].unlink()
                else:
                    subprocess.run(['git', '-C', str(fixture.repo), 'add', 'skills'], check=True)
                with self.assertRaises(Error) as error:
                    apply(Model(fixture.paths), path)
                self.assertEqual(error.exception.code, 4)
                self.assertFalse((fixture.paths.shared / 'catalog.json').exists())

    def test_review_cannot_omit_discovered_skills_or_register_dotfiles_root(self):
        self.fixture.source(nested=True)
        path, document = self.fixture.reviewed()
        document['entries'][0]['skills'] = []
        path.write_text(json.dumps(document))
        with self.assertRaises(Error):
            apply(Model(self.fixture.paths), path)
        path, document = self.fixture.reviewed()
        document['entries'][0]['path'] = '.'
        path.write_text(json.dumps(document))
        with self.assertRaises(Error):
            apply(Model(self.fixture.paths), path)
        self.assertFalse(self.fixture.paths.shared.exists())

    def test_private_relocation_keeps_verified_recovery_and_legacy_discovery(self):
        root = self.fixture.source('local-library', nested=True)
        links = self.fixture.discovery(root)
        self.fixture.legacy_sync()
        config = self.fixture.home / '.claude/settings.json'
        config.write_text(json.dumps({'skillDirectories': [str(root / 'skills/nested')]}))
        original_config = config.read_bytes()
        path, _ = self.fixture.reviewed('private', 'private-library', True)

        result = apply(Model(self.fixture.paths), path)
        model = Model(self.fixture.paths)
        relocated = Path(model.sources['private-library']['path'])

        self.assertTrue(root.is_symlink())
        self.assertTrue(relocated.is_relative_to(self.fixture.paths.data / 'private/originals'))
        self.assertFalse(relocated.is_relative_to(self.fixture.repo))
        self.assertEqual((relocated / 'companion.txt').read_text(), 'Preserved supporting asset.\n')
        self.assertTrue(result['recovery'])
        for recovery in result['recovery']:
            self.assertEqual((Path(recovery) / 'companion.txt').read_bytes(),
                             (relocated / 'companion.txt').read_bytes())
        for _ in range(2):
            environment = {**os.environ, 'HOME': str(self.fixture.home)}
            subprocess.run(['bash', str(self.fixture.repo / 'sync-skills.sh')],
                           env=environment, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for link in links:
                self.assertTrue((link / 'skills/nested/SKILL.md').is_file())
            self.assertTrue((self.fixture.home / '.codex/agents/helper.toml').is_symlink())
            self.assertIn('Generic agent instructions.',
                          (self.fixture.home / '.claude/agents/helper.md').read_text())
            self.assertTrue((self.fixture.home / '.claude/commands/example.md').is_symlink())
        self.assertEqual(config.read_bytes(), original_config)
        self.assertFalse((self.fixture.paths.shared / 'catalog.json').exists())
        excluded = subprocess.run(['git', '-C', str(self.fixture.repo), 'check-ignore', '-q', str(root)])
        self.assertEqual(excluded.returncode, 0)
        self.assertFalse((self.fixture.repo / '.gitignore').exists())

    def test_tracked_private_source_refuses_without_claiming_history_removal(self):
        root = self.fixture.source()
        subprocess.run(['git', '-C', str(self.fixture.repo), 'add', 'skills'], check=True)
        path, _ = self.fixture.reviewed('private', private_approved=True)

        with self.assertRaisesRegex(Error, 'tracked|history'):
            apply(Model(self.fixture.paths), path)

        self.assertFalse(root.is_symlink())
        self.assertFalse((self.fixture.paths.config / 'catalog.json').exists())

    def test_unknown_affected_config_format_fails_before_retiring_original(self):
        root = self.fixture.source()
        self.fixture.discovery(root)
        (self.fixture.home / '.claude/custom.conf').write_text('skills = ' + str(root))
        path, _ = self.fixture.reviewed('private', private_approved=True)

        with self.assertRaisesRegex(Error, 'configuration|format'):
            apply(Model(self.fixture.paths), path)

        self.assertFalse(root.is_symlink())
        self.assertTrue((root / 'SKILL.md').is_file())

    def test_private_id_never_appears_in_shared_catalog_when_importing_mixed_sources(self):
        self.fixture.source('portable')
        private = self.fixture.source('local-library')
        result = plan(Model(self.fixture.paths))
        path = Path(result['plan'])
        document = json.loads(path.read_text())
        for entry in document['entries']:
            local = entry['path'].endswith('/local-library')
            entry.update(classification='private' if local else 'shared',
                         source_id='private-only-identity' if local else 'portable',
                         provenance='authored', private_approved=local)
            entry['skills'][0]['id'] = entry['source_id'] + '-skill'
        path.write_text(json.dumps(document))

        apply(Model(self.fixture.paths), path)

        shared = (self.fixture.paths.shared / 'catalog.json').read_text()
        self.assertNotIn('private-only-identity', shared)
        self.assertNotIn(private.name, shared)
        self.assertNotIn(str(self.fixture.home), shared)

    def test_applied_plan_retry_is_idempotent_but_rejects_later_edits(self):
        root = self.fixture.source()
        path, _ = self.fixture.reviewed('private', private_approved=True)
        first = apply(Model(self.fixture.paths), path)
        second = apply(Model(self.fixture.paths), path)
        self.assertEqual(first, second)
        (root / 'companion.txt').write_text('New work after import')
        with self.assertRaises(Error) as error:
            apply(Model(self.fixture.paths), path)
        self.assertEqual(error.exception.code, 4)
        self.assertEqual((root / 'companion.txt').read_text(), 'New work after import')

    def test_directory_only_ignore_still_excludes_the_relocated_path_alias(self):
        root = self.fixture.source()
        (self.fixture.repo / '.gitignore').write_text('/skills/bundle/\n')
        path, _ = self.fixture.reviewed('private', private_approved=True)

        apply(Model(self.fixture.paths), path)

        self.assertTrue(root.is_symlink())
        result = subprocess.run(['git', '-C', str(self.fixture.repo), 'check-ignore', '-q', str(root)])
        self.assertEqual(result.returncode, 0)
        self.assertEqual((self.fixture.repo / '.gitignore').read_text(), '/skills/bundle/\n')

    def test_filesystem_failure_restores_original_discovery_and_allows_retry(self):
        root = self.fixture.source()
        links = self.fixture.discovery(root)
        path, _ = self.fixture.reviewed('private', private_approved=True)
        symlink = os.symlink

        def fail_original_alias(target, link, *args, **kwargs):
            if Path(link) == root:
                raise OSError('Injected filesystem publication failure')
            return symlink(target, link, *args, **kwargs)

        # Double: the OS filesystem boundary fails while publishing the new alias.
        with patch('os.symlink', side_effect=fail_original_alias):
            with self.assertRaises(OSError):
                apply(Model(self.fixture.paths), path)

        self.assertFalse(root.is_symlink())
        self.assertEqual((root / 'companion.txt').read_text(), 'Preserved supporting asset.\n')
        self.assertTrue(all((link / 'SKILL.md').is_file() for link in links))
        self.assertFalse((self.fixture.paths.config / 'catalog.json').exists())
        self.assertTrue(list((self.fixture.paths.data / 'private/recovery').glob('*/bundle/SKILL.md')))
        result = apply(Model(self.fixture.paths), path)
        self.assertEqual(result['sources'], 1)
        self.assertTrue(root.is_symlink())

    def test_catalog_publication_failure_restores_original_and_git_excludes(self):
        root = self.fixture.source()
        self.fixture.discovery(root)
        path, _ = self.fixture.reviewed('private', private_approved=True)
        exclude = self.fixture.repo / '.git/info/exclude'
        before_exclude = exclude.read_bytes()
        replace = os.replace

        def fail_catalog(source, destination, *args, **kwargs):
            if Path(destination) == self.fixture.paths.config / 'catalog.json':
                raise OSError('Injected catalog publication failure')
            return replace(source, destination, *args, **kwargs)

        # Double: the OS atomic file-replacement boundary rejects the catalog.
        with patch('os.replace', side_effect=fail_catalog):
            with self.assertRaises(OSError):
                apply(Model(self.fixture.paths), path)

        self.assertFalse(root.is_symlink())
        self.assertTrue((root / 'SKILL.md').is_file())
        self.assertEqual(exclude.read_bytes(), before_exclude)
        self.assertFalse((self.fixture.paths.config / 'catalog.json').exists())

    def test_relative_in_source_links_and_toml_paths_survive_private_relocation(self):
        root = self.fixture.source(nested=True)
        (root / 'skills/nested/asset.txt').symlink_to('../../companion.txt')
        self.fixture.discovery(root)
        config = self.fixture.home / '.claude/config.toml'
        config.write_text('skill_path = ' + json.dumps(str(root / 'skills/nested')) + '\n')
        path, _ = self.fixture.reviewed('private', private_approved=True)

        apply(Model(self.fixture.paths), path)

        self.assertEqual((root / 'skills/nested/asset.txt').read_text(), 'Preserved supporting asset.\n')
        self.assertTrue((root / 'skills/nested/asset.txt').is_symlink())

    def test_interrupted_alias_publication_is_recovered_by_the_next_apply(self):
        root = self.fixture.source()
        links = self.fixture.discovery(root)
        path, _ = self.fixture.reviewed('private', private_approved=True)
        script = '''
import os, sys
from pathlib import Path
from skillset_lib.core import Model, Paths
from skillset_lib.migration import apply
original_symlink = os.symlink
def interrupt(target, link, *args, **kwargs):
    original_symlink(target, link, *args, **kwargs)
    if Path(link) == Path(sys.argv[4]):
        os._exit(99)
os.symlink = interrupt
apply(Model(Paths(Path(sys.argv[1]), Path(sys.argv[2]))), Path(sys.argv[3]))
'''
        environment = {**os.environ, 'PYTHONPATH': str(Path(__file__).parent / 'scripts')}

        interrupted = subprocess.run([sys.executable, '-c', script, str(self.fixture.repo),
                                      str(self.fixture.home), str(path), str(root)], env=environment,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        self.assertEqual(interrupted.returncode, 99, interrupted.stderr.decode())
        self.assertTrue(all((link / 'SKILL.md').is_file() for link in links))
        result = apply(Model(self.fixture.paths), path)
        self.assertEqual(result['sources'], 1)
        self.assertTrue(root.is_symlink())
        self.assertTrue(all((link / 'SKILL.md').is_file() for link in links))
        self.assertFalse(list((self.fixture.paths.data / 'plans').glob('*.journal.json')))

    def test_duplicate_proposed_skill_identity_does_not_partially_register_sources(self):
        root = self.fixture.source(nested=True)
        (root / 'other').mkdir()
        (root / 'other/SKILL.md').write_text('Another skill')
        path, document = self.fixture.reviewed()
        for skill in document['entries'][0]['skills']:
            skill['id'] = 'colliding-identity'
        path.write_text(json.dumps(document))

        with self.assertRaisesRegex(Error, 'overwrite|identity'):
            apply(Model(self.fixture.paths), path)

        self.assertFalse((self.fixture.paths.shared / 'catalog.json').exists())

    def test_existing_configuration_paths_through_repository_alias_remain_usable(self):
        root = self.fixture.source()
        self.fixture.discovery(root)
        alias = self.fixture.home / 'repository-alias'
        alias.symlink_to(self.fixture.repo, target_is_directory=True)
        configured = alias / 'skills/bundle'
        config = self.fixture.home / '.claude/settings.json'
        config.write_text(json.dumps({'skillDirectories': [str(configured)]}))
        before = config.read_bytes()
        path, document = self.fixture.reviewed('private', private_approved=True)

        self.assertEqual(next(reference for reference in document['references']
                              if reference['path'] == str(config))['format'], 'json')
        apply(Model(self.fixture.paths), path)

        self.assertEqual(config.read_bytes(), before)
        self.assertTrue(root.is_symlink())
        self.assertEqual((configured / 'companion.txt').read_text(), 'Preserved supporting asset.\n')

    def test_malformed_review_fields_are_rejected_without_writes(self):
        self.fixture.source()
        for field in ('path', 'source_id'):
            with self.subTest(field=field):
                path, document = self.fixture.reviewed()
                document['entries'][0][field] = []
                path.write_text(json.dumps(document))
                with self.assertRaises(Error):
                    apply(Model(self.fixture.paths), path)
        self.assertFalse(self.fixture.paths.shared.exists())

    def test_escaping_source_link_is_rejected_without_shared_or_private_changes(self):
        root = self.fixture.source()
        outside = self.fixture.home / 'secret.txt'
        outside.write_text('Not a source asset')
        (root / 'escape').symlink_to(outside)
        with self.assertRaises(Error):
            plan(Model(self.fixture.paths))
        self.assertFalse(self.fixture.paths.shared.exists())


if __name__ == '__main__':
    unittest.main()
