"""Standalone repository context validation and optional bounded output helpers."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit
import uuid

BEGIN = b'<!-- BEGIN MULTICA-RUNTIME (auto-managed; do not edit) -->'
END = b'<!-- END MULTICA-RUNTIME -->'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def contained(root, relative):
    relative = str(relative)
    if not relative or '\\' in relative or ':' in relative or Path(relative).is_absolute():
        raise ValueError('Expected repository-relative path')
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Path escapes repository: ' + relative)
    return path


def lexical(relative):
    if not relative or '\\' in relative or ':' in relative or relative.startswith('/'):
        raise ValueError('Expected repository-relative path')
    normalized = posixpath.normpath(relative)
    if normalized == '..' or normalized.startswith('../'):
        raise ValueError('Path escapes repository: ' + relative)
    return normalized


def artifact(root, value=None, name='report'):
    path = Path(value).resolve() if value else root / 'Saved/ContextBudget02/artifacts' / (name + '-' + uuid.uuid4().hex + '.json')
    if not path.is_relative_to((root / 'Saved').resolve()):
        raise ValueError('Generated evidence must stay under repository Saved/')
    return path


def report(root, value, output=None, name='report'):
    path = artifact(root, output, name)
    atomic(path, encode(value))
    summary = {k: value[k] for k in ('passed', 'skipped', 'startup_bytes', 'status', 'exit_code', 'compatible', 'observed_increases', 'coverage', 'role') if k in value}
    if 'baseline_comparison' in value:
        comparison = value['baseline_comparison']
        summary['baseline_status'] = comparison['status']
        summary['observed_increases'] = comparison.get('observed_increases', [])
    summary.update(artifact=str(path), sha256=digest(path.read_bytes()))
    if value.get('failures'):
        summary.update(failure_count=len(value['failures']), failures_preview=[s[:180] for s in value['failures'][:3]])
    print(json.dumps(summary, ensure_ascii=True))
    return path


def git(root, *args, check=True):
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, timeout=30)
    if check and result.returncode:
        raise ValueError('Git operation failed: ' + args[0])
    return result.stdout


def canonical(data):
    if BEGIN in data or END in data:
        raise ValueError('Retired Multica runtime block found; direct workflow requires plain repository instructions')
    return data


class Tree:
    def __init__(self, root, staged):
        self.root, self.staged, self.index = root, staged, {}
        if staged:
            for row in git(root, 'ls-files', '--stage', '-z').split(b'\0'):
                if not row:
                    continue
                info, path = row.split(b'\t', 1)
                mode, oid, stage = info.decode().split()
                if stage != '0':
                    raise ValueError('Unmerged index entries')
                self.index[path.decode('utf-8')] = (mode, oid)

    def read(self, path):
        path = lexical(path)
        if self.staged:
            if path not in self.index or self.index[path][0] not in ('100644', '100755'):
                raise ValueError('Missing or non-regular staged input: ' + path)
            return git(self.root, 'cat-file', 'blob', self.index[path][1])
        full = contained(self.root, path)
        if not full.is_file() or full.is_symlink():
            raise ValueError('Missing or non-regular input: ' + path)
        return full.read_bytes()

    def exists(self, path):
        path = lexical(path)
        return path in self.index and self.index[path][0] in ('100644', '100755') if self.staged else contained(self.root, path).is_file()


def guard(root, mode='worktree', relevant=False):
    tree = Tree(root, mode == 'staged')
    spec = json.loads(tree.read('Tools/ContextBudget.json').decode('utf-8-sig'))
    navigation = list(spec['navigation'])
    measured = [(v['path'], v['max_bytes'], 'startup') for v in spec['startup']]
    policy_dir = spec['policy_directory']
    policies = sorted(p for p in tree.index if p.startswith(policy_dir + '/') and p.endswith('.md')) if tree.staged else sorted(p.relative_to(root).as_posix() for p in contained(root, policy_dir).glob('*.md'))
    if not policies:
        raise ValueError('Missing policy inputs')
    measured += [(p, spec['policy_max_bytes'], 'policy') for p in policies]
    measured += [(v['path'], v.get('max_bytes', 5120), 'map') for v in spec.get('maps', [])]
    navigation += [p for p, _, _ in measured]
    relevant_paths = set(navigation) | {v['path'] for v in spec['snapshots']}
    failures, files, targets = [], [], set()
    for path in navigation:
        try:
            body = canonical(tree.read(path))
            for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', body.decode('utf-8-sig')):
                target = link.strip().split(' "', 1)[0].strip('<>')
                if urlsplit(target).scheme or target.startswith('#'):
                    continue
                relative = lexical(str(PurePosixPath(path).parent / unquote(target.split('#', 1)[0])))
                targets.add(relative)
                if not tree.exists(relative):
                    failures.append('Broken link in ' + path + ': ' + target)
        except (ValueError, OSError) as exc:
            failures.append(str(exc))
    head_spec = git(root, 'show', 'HEAD:Tools/ContextBudget.json', check=False)
    old = json.loads(head_spec.decode('utf-8-sig')) if head_spec else None
    if relevant:
        changed = set(git(root, 'diff', '--cached', '--no-renames', '--name-only', '-z').decode().split('\0')) - {''}
        prefixes = ('Tools/ContextBudget', 'Scripts/ContextBudget/', 'Scripts/check_context_budget.ps1', '.githooks/', policy_dir + '/', 'Docs/Archive/')
        if old:
            relevant_paths.update(v['path'] for v in old.get('maps', []) + old['startup'] + old['snapshots'])
            relevant_paths.update(old['navigation'])
        if not any(p in relevant_paths or p in targets or p.startswith(prefixes) for p in changed):
            return {'passed': True, 'skipped': True, 'reason': 'No staged context inputs or direct targets changed'}
    startup = 0
    for path, maximum, layer in measured:
        try:
            if layer == 'map' and maximum > 5120:
                raise ValueError('Map budget exceeds 5120 bytes: ' + path)
            data = canonical(tree.read(path))
            files.append({'path': path, 'bytes': len(data), 'max_bytes': maximum, 'layer': layer})
            if len(data) > maximum:
                failures.append('Budget exceeded: ' + path + ' (' + str(len(data)) + ' > ' + str(maximum) + ')')
            if layer == 'startup':
                startup += len(data)
        except (ValueError, OSError) as exc:
            failures.append(str(exc))
    if startup > spec['startup_max_bytes']:
        failures.append('Combined startup budget exceeded')
    if old:
        for key in ('snapshots', 'startup', 'startup_max_bytes', 'policy_directory', 'policy_max_bytes'):
            if old[key] != spec[key]:
                failures.append('Protected context manifest changed: ' + key)
    for snapshot in spec['snapshots']:
        try:
            data = tree.read(snapshot['path'])
            if len(data) != snapshot['bytes'] or digest(data) != snapshot['sha256']:
                failures.append('Changed immutable snapshot: ' + snapshot['path'])
        except (ValueError, OSError) as exc:
            failures.append(str(exc))
    return {'passed': not failures, 'mode': mode, 'measurement': 'UTF-8 repository bytes, not native tokens', 'startup_bytes': startup,
            'startup_max_bytes': spec['startup_max_bytes'], 'files': files, 'link_targets': sorted(targets), 'failures': failures}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('guard')
    p.add_argument('--mode', choices=['worktree', 'staged'], default='worktree')
    p.add_argument('--relevant-only', action='store_true')
    p.add_argument('--output')
    p = sub.add_parser('preview')
    p.add_argument('path')
    p.add_argument('--start', type=int, default=1)
    p.add_argument('--lines', type=int, default=30)
    p.add_argument('--bytes', type=int, default=4096)
    p = sub.add_parser('run')
    p.add_argument('--label', default='command')
    p.add_argument('--timeout', type=int, default=120)
    p.add_argument('argv', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.command == 'guard':
            result = guard(root, args.mode, args.relevant_only)
            report(root, result, args.output, 'guard')
            return 0 if result['passed'] else 1
        if args.command == 'preview':
            if not 1 <= args.start or not 1 <= args.lines <= 80 or not 1 <= args.bytes <= 8192:
                raise ValueError('Preview supports start>=1, lines<=80, bytes<=8192')
            path, selected = contained(root, args.path), bytearray()
            with path.open('rb') as stream:
                for number, line in enumerate(stream, 1):
                    if number >= args.start + args.lines or len(selected) >= args.bytes:
                        break
                    if number >= args.start:
                        selected.extend(line[:args.bytes - len(selected)])
            print(json.dumps({'path': args.path, 'start_line': args.start, 'preview_bytes': len(selected), 'total_bytes': path.stat().st_size}))
            print(selected.decode('utf-8', errors='replace'))
        elif args.command == 'run':
            argv = args.argv[1:] if args.argv[:1] == ['--'] else args.argv
            if not argv or not 1 <= args.timeout <= 3600 or not re.fullmatch('[a-zA-Z0-9_-]{1,60}', args.label):
                raise ValueError('Specify command, bounded timeout and simple label')
            out = artifact(root, name=args.label)
            stdout, stderr = out.with_suffix('.stdout.log'), out.with_suffix('.stderr.log')
            out.parent.mkdir(parents=True, exist_ok=True)
            with stdout.open('wb') as so, stderr.open('wb') as se:
                try:
                    code = subprocess.run(argv, cwd=root, stdout=so, stderr=se, timeout=args.timeout).returncode
                except subprocess.TimeoutExpired:
                    code = 124
            report(root, {'exit_code': code, 'stdout': str(stdout), 'stderr': str(stderr), 'stdout_bytes': stdout.stat().st_size, 'stderr_bytes': stderr.stat().st_size}, str(out))
            return code
        return 0
    except (ValueError, OSError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        report(root, {'passed': False, 'failures': [str(exc)]}, getattr(args, 'output', None), 'failure')
        return 1


if __name__ == '__main__':
    sys.exit(main())
