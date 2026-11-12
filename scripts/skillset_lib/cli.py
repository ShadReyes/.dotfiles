"""Command parsing and configuration edits; installation and migration are separate."""

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

from .core import Error, Model, Paths, read_json, valid_id, locked, write_many


def parser():
    root = argparse.ArgumentParser(description='Install skills, manage selections, and explicitly prepare isolated harness exposure.')
    root.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[2], help='Dotfiles checkout (defaults to this CLI checkout)')
    commands = root.add_subparsers(dest='command', required=True)
    source = commands.add_parser('source').add_subparsers(dest='action', required=True)
    add = source.add_parser('add')
    add.add_argument('id')
    kind = add.add_mutually_exclusive_group(required=True)
    kind.add_argument('--directory')
    kind.add_argument('--git', dest='url')
    add.add_argument('--ref')
    add.add_argument('--provenance', choices=['authored', 'third-party'], default='third-party')
    add.add_argument('--upstream')
    add.add_argument('--private', action='store_true')
    source.add_parser('remove').add_argument('id')
    add = commands.add_parser('add')
    add.add_argument('id')
    add.add_argument('--source', required=True)
    add.add_argument('--path', required=True)
    add.add_argument('--upstream-name')
    add.add_argument('--private', action='store_true')
    commands.add_parser('remove').add_argument('id')
    profile = commands.add_parser('profile').add_subparsers(dest='action', required=True)
    create = profile.add_parser('create')
    create.add_argument('id')
    create.add_argument('--name')
    create.add_argument('--private', action='store_true')
    for action in ('add', 'remove'):
        command = profile.add_parser(action)
        command.add_argument('id')
        command.add_argument('skills', nargs='+')
    rename = profile.add_parser('rename')
    rename.add_argument('id')
    rename.add_argument('--name', required=True)
    profile.add_parser('delete').add_argument('id')
    for action in ('select', 'deselect'):
        profile.add_parser(action).add_argument('ids', nargs='+')
    for action in ('enable', 'disable', 'reset'):
        command = commands.add_parser(action)
        command.add_argument('ids', nargs='+')
        if action == 'reset':
            command.add_argument('--deselect-profile', action='append', default=[], metavar='PROFILE',
                                 help='Deselect an explicit profile in the same reset transaction')
    for action in ('list', 'status', 'validate', 'resolve'):
        command = commands.add_parser(action)
        command.add_argument('--json', action='store_true', required=action == 'resolve')
        if action == 'validate':
            command.add_argument('--shared-only', action='store_true')
    update = commands.add_parser('update')
    update.add_argument('sources', nargs='*')
    update.add_argument('--all', action='store_true')
    commands.add_parser('sync').add_argument('--offline', action='store_true')
    expose = commands.add_parser('expose', help='Prepare isolated managed launches; default discovery is unchanged')
    expose.add_argument('action', choices=('apply', 'status', 'rollback'))
    expose.add_argument('--target', action='append', required=True)
    migration = commands.add_parser('import')
    mode = migration.add_mutually_exclusive_group(required=True)
    mode.add_argument('--plan', action='store_true')
    mode.add_argument('--apply', type=Path)
    return root


def _refresh(model):
    model.sources = model._merge(model.catalogs, 'sources')
    model.skills = model._merge(model.catalogs, 'skills')
    model.profiles = model._merge(model.profile_docs, 'profiles')


def _root(model, scope):
    return model.paths.shared if scope == 'shared' else model.paths.config


def _existing(mapping, identity, label):
    if identity not in mapping:
        raise Error(f'Unknown {label}: {identity}')
    return mapping[identity]


def _new(mapping, identity):
    valid_id(identity)
    if identity in mapping:
        raise Error(f'Identity already registered: {identity}')


def configure(model, args):
    """Change one configuration intent, validating the resulting document graph first."""
    command, action = args.command, getattr(args, 'action', None)
    if command in ('enable', 'disable', 'reset') or command == 'profile' and action in ('select', 'deselect'):
        machine = deepcopy(model.machine)
        model.validate(selection=False)
        if command == 'profile':
            for identity in args.ids:
                valid_id(identity)
                if action == 'select':
                    _existing(model.profiles, identity, 'profile')
                    if identity not in machine['profiles']:
                        machine['profiles'].append(identity)
                elif identity in machine['profiles']:
                    machine['profiles'].remove(identity)
        else:
            for identity in args.ids:
                valid_id(identity)
                if command == 'reset':
                    machine['overrides'].pop(identity, None)
                else:
                    _existing(model.skills, identity, 'skill')
                    machine['overrides'][identity] = 'enabled' if command == 'enable' else 'disabled'
            if command == 'reset':
                for identity in args.deselect_profile:
                    valid_id(identity)
                    if identity in machine['profiles']:
                        machine['profiles'].remove(identity)
        old = read_json(model.paths.config / 'last-selection.json', {'schema_version': 1, 'selection': None})['selection']
        selection = model.save_machine(machine)
        previous = set(old['selected']) if old else set()
        return {'schema_version': 1, 'selection': selection,
                'desired_diff': {'added': sorted(set(selection['selected']) - previous),
                                 'removed': sorted(previous - set(selection['selected']))}}

    model.validate()
    writes = {}
    scope = 'private' if getattr(args, 'private', False) else 'shared'
    if command == 'source':
        if action == 'add':
            _new(model.sources, args.id)
            if args.url:
                if not args.ref:
                    raise Error('--git requires an explicit --ref branch or tag')
                record = {'type': 'git', 'url': args.url, 'ref': args.ref, 'provenance': args.provenance}
            else:
                if args.ref:
                    raise Error('--ref applies only to Git sources')
                path = Path(args.directory).expanduser()
                if scope == 'shared':
                    path = path.resolve() if path.is_absolute() else (model.paths.repo / path).resolve()
                    if not path.is_relative_to(model.paths.repo):
                        raise Error('Shared directory source must be within dotfiles')
                    path = path.relative_to(model.paths.repo)
                else:
                    path = path.resolve()
                record = {'type': 'directory', 'path': str(path), 'provenance': args.provenance}
            if args.upstream is not None:
                record['upstream'] = args.upstream
            model.catalogs[scope]['sources'][args.id] = record
        else:
            record = _existing(model.sources, args.id, 'source')
            scope = record['visibility']
            references = [key for key, skill in model.skills.items() if skill['source'] == args.id]
            if references:
                raise Error(f'Source is referenced by skills: {", ".join(references)}')
            del model.catalogs[scope]['sources'][args.id]
            model.locks[scope]['sources'].pop(args.id, None)
            writes[_root(model, scope) / 'lock.json'] = model.locks[scope]
        writes[_root(model, scope) / 'catalog.json'] = model.catalogs[scope]
    elif command == 'add':
        _new(model.skills, args.id)
        source = _existing(model.sources, args.source, 'source')
        if source['visibility'] != scope:
            raise Error('Skill visibility must match source visibility; use --private for private entries')
        record = {'source': args.source, 'path': args.path}
        if args.upstream_name is not None:
            record['upstream_name'] = args.upstream_name
        model.catalogs[scope]['skills'][args.id] = record
        writes[_root(model, scope) / 'catalog.json'] = model.catalogs[scope]
    elif command == 'remove':
        record = _existing(model.skills, args.id, 'skill')
        scope = record['visibility']
        references = [key for key, profile in model.profiles.items() if args.id in profile['skills']]
        if args.id in model.machine['overrides']:
            references.append('machine override')
        if references:
            raise Error(f'Skill is referenced by: {", ".join(references)}')
        del model.catalogs[scope]['skills'][args.id]
        writes[_root(model, scope) / 'catalog.json'] = model.catalogs[scope]
    elif command == 'profile':
        if action == 'create':
            _new(model.profiles, args.id)
            record = {'skills': []}
            if args.name is not None:
                record['name'] = args.name
            model.profile_docs[scope]['profiles'][args.id] = record
        else:
            profile = _existing(model.profiles, args.id, 'profile')
            scope = profile['visibility']
            record = model.profile_docs[scope]['profiles'][args.id]
            if action == 'delete':
                if args.id in model.machine['profiles']:
                    raise Error('Profile is referenced by machine selection; deselect it first')
                del model.profile_docs[scope]['profiles'][args.id]
            elif action == 'rename':
                record['name'] = args.name
            else:
                for identity in args.skills:
                    skill = _existing(model.skills, identity, 'skill')
                    if skill['visibility'] != scope:
                        raise Error('Profile and skill visibility must match')
                    if action == 'add' and identity not in record['skills']:
                        record['skills'].append(identity)
                    elif action == 'remove' and identity in record['skills']:
                        record['skills'].remove(identity)
        writes[_root(model, scope) / 'profiles.json'] = model.profile_docs[scope]
    else:
        raise Error('Unknown configuration command')
    _refresh(model)
    model.validate()
    write_many(writes)
    return {'schema_version': 1, 'command': command, 'action': action, 'id': args.id, 'visibility': scope}


def _catalog_output(model):
    model.validate()
    names = {}
    skills = []
    for identity, skill in sorted(model.skills.items()):
        source = model.sources[skill['source']]
        upstream_name = skill.get('upstream_name') or Path(skill['path']).name or identity
        names.setdefault(upstream_name, []).append(identity)
        skills.append({'id': identity, **skill, 'provenance': source['provenance'], 'upstream_name': upstream_name})
    return {'schema_version': 1, 'skills': skills,
            'profiles': [{'id': key, **value} for key, value in sorted(model.profiles.items())],
            'upstream_name_collisions': {key: ids for key, ids in names.items() if len(ids) > 1},
            'exposure': 'unmanaged'}


def _broken_resolution(paths, error):
    last, active = None, []
    errors = [str(error)]
    if paths is not None:
        try:
            last = read_json(paths.config / 'last-selection.json', {'schema_version': 1, 'selection': None}).get('selection')
            if not isinstance(last, dict) or not isinstance(last.get('selected'), list):
                last = None
        except Error as exc:
            errors.append(str(exc))
        try:
            records = read_json(paths.data / 'active.json', {'schema_version': 1, 'active': []}).get('active')
            if isinstance(records, list):
                active = records
        except Error as exc:
            errors.append(str(exc))
    return {'schema_version': 1, 'selection_valid': False, 'stale': last is not None,
            'desired': None, 'last_good': last, 'selected': [], 'active': active,
            'errors': errors, 'exposure': 'unmanaged',
            'data_directory': str(paths.data) if paths else None}


def _emit(result, args):
    if getattr(args, 'json', False) or args.command not in ('status', 'list', 'validate'):
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    if args.command == 'list':
        for kind in ('skills', 'profiles'):
            print(kind.capitalize() + ':')
            for entry in result[kind]:
                detail = entry.get('name') or entry.get('provenance') or ''
                print(f'  {entry["id"]} [{entry["visibility"]}] {detail}')
        for name, ids in result.get('upstream_name_collisions', {}).items():
            print(f'Upstream name collision: {name}: {", ".join(ids)}')
    elif args.command == 'validate':
        print('Configuration valid.')
    else:
        print('Selection: ' + ('valid' if result.get('selection_valid') else 'INVALID; retained result is stale' if result.get('stale') else 'INVALID; no last-good result'))
        if result.get('stale') and result.get('last_good'):
            print('  Last-good selection (stale): ' + ', '.join(result['last_good']['selected']))
        for record in result.get('selected', []):
            print(f'  {record["id"]} [{record["visibility"]}] {record.get("availability", "unknown")}')
            print('    Reasons: ' + ', '.join(record.get('reasons', [])))
            print(f'    Required revision: {record.get("required_revision")} fingerprint: {record.get("required_fingerprint")}')
            print(f'    Source state: {record.get("source_working_state", "unavailable")}')
        for label in ('desired_diff', 'installed_diff'):
            print(f'{label}: {json.dumps(result.get(label, {}), sort_keys=True)}')
        print(f'Retained data: {result.get("data_directory", "unavailable")}')
        for error in result.get('errors', []):
            print('Error: ' + str(error), file=sys.stderr)
    print('Installation commands do not change discovery. Inspect managed launches with: skillset expose status --target omp')


def main(argv=None):
    args = parser().parse_args(argv)
    paths = None
    try:
        paths = Paths(args.repo)
        read_only = args.command in ('list', 'status', 'validate', 'resolve') or (args.command == 'expose' and args.action == 'status')
        if read_only:
            model = Model(paths, shared_only=getattr(args, 'shared_only', False))
            if args.command == 'expose':
                from .exposure import run
                result = run(model, args.action, args.target)
            elif args.command == 'list':
                result = _catalog_output(model)
            elif args.command == 'validate':
                model.validate()
                result = {'schema_version': 1, 'valid': True, 'shared_only': args.shared_only}
            else:
                from .install import inspect
                result = inspect(model)
            _emit(result, args)
            return result.get('exit_code', 2 if result.get('selection_valid') is False else 0)
        with locked(paths):
            model = Model(paths)
            if args.command == 'sync':
                from .install import sync
                result = sync(model, offline=args.offline)
            elif args.command == 'expose':
                from .exposure import run
                result = run(model, args.action, args.target)
            elif args.command == 'update':
                from .install import update
                result = update(model, args.sources, all_sources=args.all)
            elif args.command == 'import':
                from . import migration
                result = migration.plan(model) if args.plan else migration.apply(model, args.apply)
            else:
                result = configure(model, args)
        _emit(result, args)
        return result.get('exit_code', 0)
    except Error as exc:
        if args.command in ('status', 'resolve'):
            _emit(_broken_resolution(paths, exc), args)
        elif getattr(args, 'json', False):
            _emit({'schema_version': 1, 'valid': False, 'errors': [str(exc)]}, args)
        print(f'skillset: {exc}', file=sys.stderr)
        return exc.code
    except (OSError, ValueError, TypeError, KeyError) as exc:
        if getattr(args, 'json', False):
            _emit({'schema_version': 1, 'errors': [str(exc)]}, args)
        print(f'skillset: {exc}', file=sys.stderr)
        return 1
