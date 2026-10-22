#!/usr/bin/env python3
"""Copy the canonical production contract into a portable bundle, or check it."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', required=True, type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    source = Path(__file__).resolve().parent.parent / 'references/decalflow-production-contract.md'
    root = Path(subprocess.check_output(
        ['git', '-C', str(source.parent), 'rev-parse', '--show-toplevel'], text=True
    ).strip())
    relative = source.relative_to(root).as_posix()
    revision = subprocess.check_output(
        ['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True
    ).strip()
    committed = subprocess.run(
        ['git', '-C', str(root), 'show', f'{revision}:{relative}'],
        capture_output=True, check=False,
    )
    content = source.read_bytes()
    metadata = {
        'source': relative,
        'sourceRevision': revision,
        'sourceDirty': committed.returncode != 0 or committed.stdout != content,
        'sha256': hashlib.sha256(content).hexdigest(),
    }
    destination = args.destination.resolve()
    copy = destination / source.name
    provenance = destination / 'decalflow-production-contract.source.json'
    if copy == source:
        parser.error('destination must differ from the canonical source directory')
    encoded = (json.dumps(metadata, indent=2, sort_keys=True) + '\n').encode()
    if args.check:
        if not copy.is_file() or not provenance.is_file():
            sys.exit('Missing bundled contract or provenance; regenerate before packaging.')
        if copy.read_bytes() != content or provenance.read_bytes() != encoded:
            sys.exit('Stale bundled contract or provenance; regenerate before packaging.')
        print('Contract bytes and source provenance verified.')
    else:
        destination.mkdir(parents=True, exist_ok=True)
        copy.write_bytes(content)
        provenance.write_bytes(encoded)
        print('Generated contract copy and source provenance.')


if __name__ == '__main__':
    main()
