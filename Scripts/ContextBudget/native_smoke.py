"""Bounded subscription-only app-server smoke; no gameplay or issue dispatch.

Generated role homes come from TestContextBudgetExportNativeProfiles. Only
sanitized native config/skill metadata and usage reports are retained as evidence.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import queue
import subprocess
import threading
import time
import tomllib
from context_budget import atomic, digest, encode, git, read_json, report
from usage import automatic_baseline, collect, compare


class Native:
    def __init__(self, executable, home, cwd, extra):
        env = os.environ.copy()
        for name in list(env):
            if name.endswith('API_KEY') or name in ('MULTICA_TOKEN', 'MULTICA_LLM_BASE_URL', 'OPENAI_BASE_URL'):
                env.pop(name, None)
        env['CODEX_HOME'] = str(home)
        self.log = (home / 'native-stderr.log').open('wb')
        self.process = subprocess.Popen([str(executable), 'app-server', *extra, '-c', 'forced_login_method="chatgpt"'],
                                        cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.log)
        self.messages, self.counter = queue.Queue(), 0
        threading.Thread(target=self.read, daemon=True).start()
        try:
            self.request('initialize', {'clientInfo': {'name': 'context-budget-smoke', 'version': '1'}, 'capabilities': {'experimentalApi': True}})
            self.send({'method': 'initialized'})
        except Exception:
            self.close()
            raise

    def read(self):
        for line in self.process.stdout:
            try: self.messages.put(json.loads(line))
            except ValueError: pass
        self.messages.put({'closed': True})

    def send(self, data):
        self.process.stdin.write(encode(data).replace(b'\n', b'') + b'\n')
        self.process.stdin.flush()

    def next(self, timeout=60):
        value = self.messages.get(timeout=timeout)
        if value.get('closed'): raise RuntimeError('Native process closed unexpectedly')
        if 'method' in value and 'id' in value:
            self.send({'id': value['id'], 'error': {'code': -32601, 'message': 'Smoke does not authorize tools or approvals'}})
        return value

    def request(self, method, params):
        self.counter += 1
        self.send({'id': self.counter, 'method': method, 'params': params})
        deadline = time.monotonic()+70
        while time.monotonic() < deadline:
            value = self.next(max(1, deadline-time.monotonic()))
            if value.get('id') == self.counter:
                if 'error' in value: raise RuntimeError(method + ': ' + str(value['error'])[:500])
                return value['result']
        raise TimeoutError(method)

    def turn(self, thread):
        self.request('turn/start', {'threadId': thread, 'effort': 'max', 'serviceTier': 'default',
                     'input': [{'type': 'text', 'text': 'Reply with exactly CONTEXT_BUDGET_SMOKE_OK. Do not use tools, read files, or perform any other work.'}]})
        deadline = time.monotonic()+90
        while time.monotonic() < deadline:
            row = self.next(max(1, deadline-time.monotonic()))
            if row.get('method') == 'turn/completed':
                turn = row.get('params', {}).get('turn', {})
                if turn.get('status') != 'completed': raise RuntimeError('Native smoke turn failed')
                return
        raise TimeoutError('Native smoke turn')

    def close(self):
        self.process.stdin.close()
        try: self.process.wait(timeout=12)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)
        self.log.close()


def config_summary(result):
    config = result.get('config', result)
    return {'model': config.get('model'), 'model_reasoning_effort': config.get('model_reasoning_effort'),
            'tool_output_token_limit': config.get('tool_output_token_limit'),
            'service_tier': config.get('service_tier'), 'features': {k: v for k, v in config.get('features', {}).items() if k in ('apps', 'memories', 'multi_agent')},
            'mcp_servers': sorted(config.get('mcp_servers', {})),
            'mcp_enabled': {k: v.get('enabled', True) for k, v in config.get('mcp_servers', {}).items()},
            'plugins': {k: v.get('enabled') for k, v in config.get('plugins', {}).items() if isinstance(v, dict)},
            'skill_override_count': len(config.get('skills', {}).get('config', []))}


def smoke(root, executable, profiles, auth_source, generate=False, config_cwd=None):
    cwd = profiles / 'workdir'
    cwd.mkdir(parents=True, exist_ok=True)
    git(cwd, 'init', '-q')
    atomic(cwd / 'AGENTS.md', b'Native context validation fixture. Reply only to the explicit smoke prompt.\n')
    roles = read_json(root / 'Tools/ContextBudgetRoles.json')['roles']
    summaries = {}
    for role, profile in roles.items():
        home = profiles / role
        extra = read_json(home / 'overrides.json') + ['-c', 'model="gpt-6-astra"']
        client = Native(executable, home, config_cwd or cwd, extra)
        try:
            summaries[role] = config_summary(client.request('config/read', {'includeLayers': False, 'cwd': str(config_cwd or cwd)}))
            summary = summaries[role]
            if summary['model_reasoning_effort'] != 'max' or summary['service_tier'] != 'default':
                raise ValueError('Native role settings differ: ' + role)
            if summary['tool_output_token_limit'] != profile['tool_output_token_limit']:
                raise ValueError('Native output budget differs: ' + role)
            from fnmatch import fnmatch
            for name, enabled in summary['mcp_enabled'].items():
                if enabled and not any(fnmatch(name, pattern) for pattern in profile['mcp_allow']):
                    raise ValueError('Native role enabled excluded MCP: ' + role + '/' + name)
        finally:
            client.close()
    atomic(profiles / 'effective-native-config.json', encode(summaries))
    if generate:
        home = profiles / 'code'
        auth = home / 'auth.json'
        if auth.exists(): raise ValueError('Smoke auth destination already exists; preserve and inspect it')
        os.link(auth_source, auth)
        extra = read_json(home / 'overrides.json') + ['-c', 'model="gpt-6-astra"']
        binding = {'model': 'gpt-6-astra', 'service_tier': 'default', 'profile_sha256': digest(encode(roles['code'])),
                   'workload': 'context-budget-native-smoke-v1', 'resume_expected': False, 'prior_session_id': '', 'completed': True,
                   'effective_config_sha256': read_json(home / 'native-config.json')['comparison_config_sha256'],
                   'mcp_sha256': digest(encode(summaries['code']['mcp_enabled'])),
                   'brief_sha256': digest((cwd / 'AGENTS.md').read_bytes()), 'checkpoint_sha256': 'none',
                   'launch_args_sha256': digest(encode(['app-server', *extra, '-c', 'forced_login_method="chatgpt"']))}
        try:
            extra = read_json(home / 'overrides.json') + ['-c', 'model="gpt-6-astra"']
            started = datetime.now(timezone.utc).isoformat()
            client = Native(executable, home, cwd, extra)
            try:
                result = client.request('thread/start', {'model': 'gpt-6-astra', 'cwd': str(cwd), 'approvalPolicy': 'never',
                                        'config': {'model_reasoning_effort': 'max', 'service_tier': 'default'}, 'persistExtendedHistory': True})
                thread = result['thread']['id']
                client.turn(thread)
                client.turn(thread)
            finally: client.close()
            first = collect(home, thread, started, {**binding, 'ended_at': datetime.now(timezone.utc).isoformat()})
            first['baseline_comparison'] = automatic_baseline(root, first)
            atomic(profiles / 'fresh-usage.json', encode(first))
            # A second process resumes the exact native thread; no inherited raw
            # transcript enters this tool's stdout or any report.
            started = datetime.now(timezone.utc).isoformat()
            client = Native(executable, home, cwd, extra)
            try:
                client.request('thread/resume', {'threadId': thread, 'cwd': str(cwd), 'model': 'gpt-6-astra',
                               'config': {'model_reasoning_effort': 'max', 'service_tier': 'default'}})
                client.turn(thread)
            finally: client.close()
            resumed = collect(home, thread, started, {**binding, 'resume_expected': True, 'prior_session_id': thread, 'ended_at': datetime.now(timezone.utc).isoformat()})
            atomic(profiles / 'resumed-usage.json', encode(resumed))
            atomic(profiles / 'fresh-vs-resumed.json', encode(compare(first, resumed)))
            # The compatible regression example needs a second fresh session
            # with identical native profile and workload, not a reused counter.
            started = datetime.now(timezone.utc).isoformat()
            client = Native(executable, home, cwd, extra)
            try:
                result = client.request('thread/start', {'model': 'gpt-6-astra', 'cwd': str(cwd), 'approvalPolicy': 'never',
                                        'config': {'model_reasoning_effort': 'max', 'service_tier': 'default'}, 'persistExtendedHistory': True})
                second_thread = result['thread']['id']
                client.turn(second_thread)
                client.turn(second_thread)
            finally: client.close()
            second = collect(home, second_thread, started, {**binding, 'ended_at': datetime.now(timezone.utc).isoformat()})
            second['baseline_comparison'] = automatic_baseline(root, second)
            atomic(profiles / 'fresh-repeat-usage.json', encode(second))
            atomic(profiles / 'compatible-comparison.json', encode(compare(first, second)))
        finally:
            auth.unlink()
    return {'passed': True, 'roles_verified': list(summaries), 'native_generations': 5 if generate else 0,
            'limits': 'Effective native config proves configured tier; raw turn metadata may omit actual service tier. Installed daemon deployment remains a controller check.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    p.add_argument('--executable', type=Path, required=True)
    p.add_argument('--profiles', type=Path, required=True)
    p.add_argument('--auth-source', type=Path)
    p.add_argument('--generate', action='store_true', help='Five bounded native subscription responses (fresh, resumed, fresh repeat)')
    p.add_argument('--config-cwd', type=Path, help='Inspect config at the actual trusted project cwd; generation still uses the isolated fixture')
    args = p.parse_args()
    if not args.profiles.resolve().is_relative_to((args.root / 'Saved').resolve()):
        raise ValueError('Smoke profiles must stay under Saved')
    value = smoke(args.root.resolve(), args.executable, args.profiles.resolve(), args.auth_source, args.generate, args.config_cwd)
    report(args.root.resolve(), value, str(args.profiles / 'smoke-result.json'), 'native-smoke')
