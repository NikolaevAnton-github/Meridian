"""MSQ-138: bounded repository/task context. Multica owns live task state."""
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
LIMITS = {'brief': 4096, 'checkpoint': 2048}
ACTIVE = {'backlog', 'todo', 'in_progress', 'in_review', 'blocked'}


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


def canonical(data, allow=False):
    if BEGIN not in data and END not in data:
        return data, 0
    if not allow:
        raise ValueError('Generated Multica runtime block must not be staged')
    if data.count(BEGIN) != 1 or data.count(END) != 1:
        raise ValueError('Malformed managed runtime markers')
    start, end = data.index(BEGIN), data.index(END) + len(END)
    if end <= start:
        raise ValueError('Malformed managed runtime ordering')
    if start >= 2 and data[start-2:start] == b'\n\n':
        start -= 2
    if data[end:end+2] == b'\r\n':
        end += 2
    elif data[end:end+1] == b'\n':
        end += 1
    return data[:start] + data[end:], end-start


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


def guard(root, mode='worktree', relevant=False, allow=False):
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
            body, _ = canonical(tree.read(path), allow and not tree.staged)
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
    try:
        role_data = tree.read('Tools/ContextBudgetRoles.json')
        if len(role_data) > 8192:
            raise ValueError('Role manifest exceeds 8192 bytes')
        role_spec = json.loads(role_data.decode('utf-8-sig'))
        if role_spec.get('schema_version') != 1 or set(role_spec['roles']) != {'code', 'unreal', 'art', 'review'}:
            raise ValueError('Invalid role manifest schema')
        for role in role_spec['roles'].values():
            if role['thinking_level'] != 'max' or role['service_tier'] != 'default' or not 1 <= role['tool_output_token_limit'] <= 8192:
                raise ValueError('Invalid role reasoning/tier/output budget')
            for key in ('mcp_allow', 'plugin_allow', 'skill_allow'):
                if not isinstance(role[key], list) or any(not isinstance(s, str) or not re.fullmatch(r'[\w*?@.-]+', s) for s in role[key]):
                    raise ValueError('Invalid role allowlist: ' + key)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        failures.append(str(exc))
    for path, maximum, layer in measured:
        try:
            if layer == 'map' and maximum > 5120:
                raise ValueError('Map budget exceeds 5120 bytes: ' + path)
            data, generated = canonical(tree.read(path), allow and not tree.staged)
            files.append({'path': path, 'bytes': len(data), 'max_bytes': maximum, 'generated_runtime_bytes': generated, 'layer': layer})
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


def live_issue(root, issue_id, controller_profile=None, *, allow_controller=True):
    uuid.UUID(issue_id)
    local_cli = root / '.tools/multica/bin' / ('multica.exe' if os.name == 'nt' else 'multica')
    command = os.environ.get('CONTEXT_BUDGET_MULTICA') or (str(local_cli) if local_cli.is_file() else 'multica')
    profile = (controller_profile if controller_profile is not None else os.environ.get('CONTEXT_BUDGET_MULTICA_PROFILE', '')).strip()
    argv, cwd = [command], root
    if profile:
        # Never clear task identity or borrow owner auth to make a worker read succeed.
        if not allow_controller or any(os.environ.get(key) for key in ('MULTICA_TOKEN', 'MULTICA_TASK_ID', 'MULTICA_TASK_CONFIG_ROOT')):
            raise ValueError('Controller profile is forbidden for daemon preparation or a task-scoped worker')
        argv += ['--profile', profile]
        cwd = root.parent
    argv += ['issue', 'get', issue_id, '--output', 'json']
    result = subprocess.run(argv, cwd=cwd, capture_output=True, timeout=25)
    if result.returncode:
        raise ValueError('Live Multica issue read failed; no cached status fallback')
    issue = json.loads(result.stdout.decode('utf-8-sig'))
    if issue.get('id') != issue_id:
        raise ValueError('Live issue identity mismatch')
    return issue


def scope_hash(issue):
    return digest(encode({'title': issue.get('title'), 'description': issue.get('description')}))


def identity(root, issue, candidate, authority):
    status = issue.get('status_category') or issue.get('status')
    if status not in ACTIVE:
        raise ValueError('Task is closed or has unknown live status: ' + str(status))
    if not isinstance(candidate, str) or not candidate or len(candidate) > 160:
        raise ValueError('Candidate must be a nonempty identifier up to 160 characters')
    authority_data = contained(root, authority).read_bytes()
    return {'task_id': issue['id'], 'scope_sha256': scope_hash(issue), 'candidate': candidate,
            'revision': git(root, 'rev-parse', 'HEAD').decode().strip(), 'owner_authority': authority, 'authority_sha256': digest(authority_data)}


def task_path(root, issue_id, kind):
    uuid.UUID(issue_id)
    return root / 'Saved/ContextBudget02/tasks' / issue_id / (kind + '.json')


def validate_document(root, kind, data, issue, brief=None):
    if len(encode(data)) > LIMITS[kind]:
        raise ValueError(kind + ' exceeds ' + str(LIMITS[kind]) + ' bytes')
    required = {'schema_version', 'task_id', 'scope_sha256', 'candidate', 'revision', 'owner_authority', 'authority_sha256', 'pending', 'evidence'}
    required |= {'role', 'objective', 'allowed_writes', 'acceptance'} if kind == 'brief' else {'brief_sha256', 'next_step'}
    if set(data) != required or data['schema_version'] != 1:
        raise ValueError('Invalid ' + kind + ' schema (exact fields required)')
    expected = identity(root, issue, data['candidate'], data['owner_authority'])
    for key, value in expected.items():
        if data[key] != value:
            raise ValueError('Stale ' + kind + ': ' + key)
    for key in ('pending', 'evidence'):
        if not isinstance(data[key], list) or any(not isinstance(x, str) or not x for x in data[key]):
            raise ValueError(key + ' must be a list of nonempty strings')
    for path in data['evidence']:
        if not contained(root, path).exists():
            raise ValueError('Missing evidence: ' + path)
    if kind == 'brief':
        roles = read_json(root / 'Tools/ContextBudgetRoles.json')['roles']
        if data['role'] not in roles or not isinstance(data['objective'], str) or not data['objective']:
            raise ValueError('Invalid role/objective')
        for key in ('allowed_writes', 'acceptance'):
            if not isinstance(data[key], list) or not data[key] or any(not isinstance(x, str) or not x for x in data[key]):
                raise ValueError(key + ' requires nonempty strings')
        for path in data['allowed_writes']:
            contained(root, path)
    else:
        if brief is None or data['brief_sha256'] != digest(encode(brief)):
            raise ValueError('Checkpoint belongs to a replaced brief')
        if any(data[key] != brief[key] for key in expected):
            raise ValueError('Checkpoint candidate/scope differs from brief')
        if not isinstance(data['next_step'], str) or not data['next_step']:
            raise ValueError('Missing checkpoint next_step')
    return data


def load_document(root, kind, issue, brief=None):
    path = task_path(root, issue['id'], kind)
    if path.stat().st_size > LIMITS[kind]:
        raise ValueError(kind + ' raw file exceeds byte budget')
    return validate_document(root, kind, read_json(path), issue, brief)


def prepare(root, request):
    result = guard(root, allow=True)
    if not result['passed']:
        raise ValueError('Context guard failed: ' + '; '.join(result['failures'][:3]))
    issue = live_issue(root, request['issue_id'], allow_controller=False)
    brief = load_document(root, 'brief', issue)
    cp_path = task_path(root, issue['id'], 'checkpoint')
    checkpoint = load_document(root, 'checkpoint', issue, brief) if cp_path.exists() else None
    if request.get('resume_expected') and checkpoint is None:
        raise ValueError('Resume/cold resume requires an active checkpoint')
    role = read_json(root / 'Tools/ContextBudgetRoles.json')['roles'][brief['role']]
    if role['thinking_level'] != 'max' or role['service_tier'] != 'default':
        raise ValueError('Role must retain max reasoning and default speed')
    return {'passed': True, 'role': brief['role'], 'profile': role, 'brief_sha256': digest(encode(brief)),
            'candidate': brief['candidate'], 'revision': brief['revision'], 'scope_sha256': brief['scope_sha256'],
            'checkpoint_sha256': digest(encode(checkpoint)) if checkpoint else None,
            'profile_sha256': digest(encode(role)), 'startup_bytes': result['startup_bytes'],
            'brief_path': str(task_path(root, issue['id'], 'brief')), 'checkpoint_path': str(cp_path) if checkpoint else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('guard')
    p.add_argument('--mode', choices=['worktree', 'staged'], default='worktree')
    p.add_argument('--relevant-only', action='store_true')
    p.add_argument('--allow-managed-runtime', action='store_true')
    p.add_argument('--output')
    p = sub.add_parser('write')
    p.add_argument('kind', choices=list(LIMITS))
    p.add_argument('--issue', required=True)
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--candidate')
    p.add_argument('--authority')
    p.add_argument('--controller-profile')
    p = sub.add_parser('validate')
    p.add_argument('--issue', required=True)
    p.add_argument('--controller-profile')
    p = sub.add_parser('state')
    p.add_argument('--issue', required=True)
    p.add_argument('--controller-profile')
    p = sub.add_parser('prepare')
    p.add_argument('--request', type=Path, required=True)
    p.add_argument('--output', required=True)
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
            result = guard(root, args.mode, args.relevant_only, args.allow_managed_runtime)
            report(root, result, args.output, 'guard')
            return 0 if result['passed'] else 1
        if args.command == 'state':
            issue = live_issue(root, args.issue, args.controller_profile)
            print(json.dumps({k: issue.get(k) for k in ('id', 'identifier', 'status', 'status_category', 'revision')}, ensure_ascii=True))
        elif args.command in ('write', 'validate'):
            issue = live_issue(root, args.issue, args.controller_profile)
            if args.command == 'validate':
                brief = load_document(root, 'brief', issue)
                cp = task_path(root, args.issue, 'checkpoint')
                if cp.exists():
                    load_document(root, 'checkpoint', issue, brief)
                print(json.dumps({'passed': True, 'task_id': args.issue, 'checkpoint': cp.exists()}))
            else:
                data = read_json(args.input)
                brief = load_document(root, 'brief', issue) if args.kind == 'checkpoint' else None
                bound = identity(root, issue, args.candidate or (brief or {}).get('candidate'), args.authority or (brief or {}).get('owner_authority', ''))
                if set(data) & set(bound):
                    raise ValueError('Input must not supply generated identity fields')
                data.update(bound, schema_version=1)
                if brief:
                    data['brief_sha256'] = digest(encode(brief))
                validate_document(root, args.kind, data, issue, brief)
                dest = task_path(root, args.issue, args.kind)
                atomic(dest, encode(data))
                print(json.dumps({'passed': True, 'path': str(dest), 'bytes': dest.stat().st_size}))
        elif args.command == 'prepare':
            report(root, prepare(root, read_json(args.request)), args.output, 'prepare')
        elif args.command == 'preview':
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
