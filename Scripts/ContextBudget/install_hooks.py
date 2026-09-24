"""Install/remove a repository-local pre-commit chain without touching LFS hooks."""
import argparse
from pathlib import Path
import sys
from context_budget import atomic, digest, encode, git, read_json, report

WRAPPER = b'''#!/bin/sh
# ContextBudget02 preserving wrapper v1
set -eu
if [ -f "$0.context-budget-original" ]; then
    "$0.context-budget-original" "$@"
fi
root=$(git rev-parse --show-toplevel)
exec sh "$root/.githooks/pre-commit" "$@"
'''


def install(root, remove=False):
    hooks = Path(git(root, 'rev-parse', '--path-format=absolute', '--git-path', 'hooks').decode().strip()).resolve()
    common = Path(git(root, 'rev-parse', '--path-format=absolute', '--git-common-dir').decode().strip()).resolve()
    if not (hooks.is_relative_to(root) or hooks.is_relative_to(common)):
        raise ValueError('Refusing to modify a shared external hooks directory; configure repository-local hooks first')
    target = hooks / 'pre-commit'
    if target.resolve() == (root / '.githooks/pre-commit').resolve():
        raise ValueError('Refusing to wrap the versioned hook itself (core.hooksPath aliases .githooks)')
    original = hooks / 'pre-commit.context-budget-original'
    record = root / 'Saved/ContextBudget02/hook-install.json'
    if target.is_symlink() or original.is_symlink():
        raise ValueError('Refusing to replace symlink hooks')
    if remove:
        saved = read_json(record)
        if saved['hook'] != str(target) or target.read_bytes() != WRAPPER:
            raise ValueError('Installed hook changed; preserving it for manual reconciliation')
        if saved['original_sha256']:
            if digest(original.read_bytes()) != saved['original_sha256']:
                raise ValueError('Original hook changed; refusing automatic rollback')
            target.unlink()
            original.replace(target)
        else:
            target.unlink()
        record.unlink()
        return {'passed': True, 'status': 'removed', 'hook': str(target)}
    if target.exists() and target.read_bytes() == WRAPPER:
        saved = read_json(record)
        if saved['original_sha256'] and (not original.exists() or digest(original.read_bytes()) != saved['original_sha256']):
            raise ValueError('Preserved hook identity changed')
        return {'passed': True, 'status': 'already installed', 'hook': str(target)}
    if record.exists() or original.exists():
        raise ValueError('Previous install record/backup exists; refusing to overwrite')
    if not (root / '.githooks/pre-commit').is_file():
        raise ValueError('Versioned hook missing')
    hooks.mkdir(parents=True, exist_ok=True)
    saved = {'hook': str(target), 'original_sha256': digest(target.read_bytes()) if target.exists() else None}
    if target.exists():
        target.replace(original)
    try:
        atomic(target, WRAPPER)
        target.chmod(0o755)
        atomic(record, encode(saved))
    except Exception:
        if target.exists() and target.read_bytes() == WRAPPER:
            target.unlink()
        if original.exists():
            original.replace(target)
        raise
    return {'passed': True, 'status': 'installed', **saved}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    p.add_argument('--remove', action='store_true')
    args = p.parse_args()
    try:
        report(args.root.resolve(), install(args.root.resolve(), args.remove), name='hook-install')
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
