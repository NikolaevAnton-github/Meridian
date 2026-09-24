"""Focused staged-tree, lifecycle, preserving-hook and native-accounting tests."""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import context_budget as cb
import install_hooks
import usage

ROOT = Path(__file__).resolve().parents[2]


class ContextBudgetTests(unittest.TestCase):
    def setUp(self):
        self.base = ROOT / 'Saved/ContextBudget02/tests'
        self.base.mkdir(parents=True, exist_ok=True)
        self.root = Path(tempfile.mkdtemp(prefix='fixture-', dir=self.base))
        self.write('AGENTS.md', '[State](Docs/ProjectState.md)\n')
        self.write('Docs/ProjectState.md', '[Target](target.md)\n')
        self.write('Docs/target.md', 'source')
        self.write('Docs/AgentPolicies/Policy.md', 'small policy')
        self.write('Docs/snapshot.md', 'immutable source')
        self.write('Docs/authority.json', '{}')
        self.write('.githooks/pre-commit', '#!/bin/sh\nexit 0\n')
        spec = {'startup': [{'path': 'AGENTS.md', 'max_bytes': 4096}, {'path': 'Docs/ProjectState.md', 'max_bytes': 4096}],
                'startup_max_bytes': 8192, 'policy_directory': 'Docs/AgentPolicies', 'policy_max_bytes': 5120,
                'navigation': [], 'snapshots': [{'path': 'Docs/snapshot.md', 'bytes': 16, 'sha256': cb.digest(b'immutable source')}]}
        self.write('Tools/ContextBudget.json', cb.encode(spec))
        self.write('Tools/ContextBudgetRoles.json', (ROOT / 'Tools/ContextBudgetRoles.json').read_bytes())
        cb.git(self.root, 'init', '-q')
        cb.git(self.root, 'add', '.')
        cb.git(self.root, '-c', 'user.name=Context Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'Fixture')
        self.issue = {'id': '01a0d43a-d711-7ad9-8931-d42f59ae7eff', 'title': 'task', 'description': 'scope', 'status': 'in_progress'}

    def tearDown(self):
        if not self.root.resolve().is_relative_to(self.base.resolve()):
            raise AssertionError('Unsafe test cleanup path')
        def writable_retry(function, path, error):
            if not Path(path).resolve().is_relative_to(self.root.resolve()):
                raise ValueError('Unsafe cleanup retry')
            os.chmod(path, 0o700)
            function(path)
        shutil.rmtree(self.root, onexc=writable_retry)

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode() if isinstance(content, str) else content)
        return path

    def brief(self):
        return {'schema_version': 1, **cb.identity(self.root, self.issue, 'candidate-1', 'Docs/authority.json'),
                'role': 'code', 'objective': 'Test lifecycle', 'allowed_writes': ['Scripts'],
                'acceptance': ['Checks pass'], 'pending': ['Implement'], 'evidence': ['Docs/target.md']}

    def test_staged_good_worktree_bad(self):
        self.write('AGENTS.md', 'x' * 5000)
        self.assertTrue(cb.guard(self.root, 'staged')['passed'])
        self.assertFalse(cb.guard(self.root)['passed'])

    def test_staged_bad_worktree_good(self):
        self.write('AGENTS.md', 'x' * 5000)
        cb.git(self.root, 'add', 'AGENTS.md')
        self.write('AGENTS.md', 'small')
        self.assertFalse(cb.guard(self.root, 'staged', True)['passed'])

    def test_missing_staged_target_despite_worktree_file(self):
        cb.git(self.root, 'rm', '--cached', 'Docs/target.md')
        self.assertFalse(cb.guard(self.root, 'staged', True)['passed'])

    def test_rename_of_direct_target_is_relevant(self):
        cb.git(self.root, 'mv', 'Docs/target.md', 'Docs/renamed.md')
        self.assertFalse(cb.guard(self.root, 'staged', True)['passed'])

    def test_installer_rejects_versioned_hook_alias_without_mutation(self):
        cb.git(self.root, 'config', 'core.hooksPath', '.githooks')
        original = (self.root / '.githooks/pre-commit').read_bytes()
        with self.assertRaises(ValueError): install_hooks.install(self.root)
        self.assertEqual((self.root / '.githooks/pre-commit').read_bytes(), original)
        self.assertFalse((self.root / '.githooks/pre-commit.context-budget-original').exists())

    def test_worktree_missing_does_not_change_staged_navigation(self):
        (self.root / 'Docs/target.md').unlink()
        self.assertTrue(cb.guard(self.root, 'staged')['passed'])

    def test_unrelated_commit_skips_and_context_change_checks(self):
        self.write('AGENTS.md', 'too large' * 1000)
        self.write('unrelated.txt', 'small')
        cb.git(self.root, 'add', 'unrelated.txt')
        self.assertTrue(cb.guard(self.root, 'staged', True)['skipped'])
        cb.git(self.root, 'add', 'AGENTS.md')
        self.assertFalse(cb.guard(self.root, 'staged', True)['passed'])

    def test_staged_manifest_and_immutable_snapshot_protected(self):
        self.write('Docs/snapshot.md', 'new bytes')
        spec = cb.read_json(self.root / 'Tools/ContextBudget.json')
        spec['snapshots'][0].update(bytes=9, sha256=cb.digest(b'new bytes'))
        self.write('Tools/ContextBudget.json', cb.encode(spec))
        cb.git(self.root, 'add', '.')
        self.assertFalse(cb.guard(self.root, 'staged')['passed'])
        cb.git(self.root, 'rm', '--cached', 'Tools/ContextBudget.json')
        with self.assertRaises(ValueError):
            cb.guard(self.root, 'staged', True)

    def test_generated_runtime_measured_separately_and_never_staged(self):
        original = (self.root / 'AGENTS.md').read_bytes()
        self.write('AGENTS.md', original + b'\n\n' + cb.BEGIN + b'\nGenerated\n' + cb.END + b'\n')
        self.assertEqual(cb.canonical((self.root / 'AGENTS.md').read_bytes(), True)[0], original)
        self.assertTrue(cb.guard(self.root, allow=True)['passed'])
        cb.git(self.root, 'add', 'AGENTS.md')
        self.assertFalse(cb.guard(self.root, 'staged')['passed'])

    def test_hook_preserves_custom_path_lfs_existing_and_rollback(self):
        cb.git(self.root, 'config', 'core.hooksPath', '.local-hooks')
        old = b'#!/bin/sh\nprintf old-hook\\n >> hook-observed.txt\n'
        self.write('.local-hooks/pre-commit', old).chmod(0o755)
        lfs = self.write('.local-hooks/pre-push', b'LFS sentinel')
        self.assertEqual(install_hooks.install(self.root)['status'], 'installed')
        self.assertEqual(install_hooks.install(self.root)['status'], 'already installed')
        self.assertEqual(cb.git(self.root, 'hook', 'run', 'pre-commit'), b'')
        self.assertTrue((self.root / 'hook-observed.txt').exists())
        self.write('.githooks/pre-commit', '#!/bin/sh\nexit 7\n')
        result = subprocess.run(['git', '-C', str(self.root), 'hook', 'run', 'pre-commit'], capture_output=True)
        self.assertEqual(result.returncode, 7)
        install_hooks.install(self.root, remove=True)
        self.assertEqual((self.root / '.local-hooks/pre-commit').read_bytes(), old)
        self.assertEqual(lfs.read_bytes(), b'LFS sentinel')

    def test_hook_existing_failure_propagates(self):
        self.write('.git/hooks/pre-commit', '#!/bin/sh\nexit 9\n').chmod(0o755)
        install_hooks.install(self.root)
        result = subprocess.run(['git', '-C', str(self.root), 'hook', 'run', 'pre-commit'], capture_output=True)
        self.assertEqual(result.returncode, 9)

    def test_installed_real_hook_accepts_and_rejects_index(self):
        for relative in ('Scripts/check_context_budget.ps1', 'Scripts/ContextBudget/python.ps1', 'Scripts/ContextBudget/context_budget.py', '.githooks/pre-commit'):
            self.write(relative, (ROOT / relative).read_bytes())
        install_hooks.install(self.root)
        env = {**os.environ, 'CONTEXT_BUDGET_PYTHON': sys.executable}
        self.write('AGENTS.md', 'small changed instructions')
        cb.git(self.root, 'add', 'AGENTS.md')
        result = subprocess.run(['git', '-C', str(self.root), 'hook', 'run', 'pre-commit'], env=env, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertLess(len(result.stdout), 1400)
        self.write('AGENTS.md', 'x'*5000)
        cb.git(self.root, 'add', 'AGENTS.md')
        self.write('AGENTS.md', 'valid working tree')
        result = subprocess.run(['git', '-C', str(self.root), 'hook', 'run', 'pre-commit'], env=env, capture_output=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_automatic_baseline_config_compatibility_and_direction(self):
        record = {'coverage': 'recorded', 'settings_match': True, 'output_includes_reasoning_check': True,
                  'binding': {'completed': True, 'ended_at': '2026-09-24T12:00:03Z'}, 'comparison_key': {k: 'same' for k in usage.COMPATIBLE},
                  'first_input_tokens': 100, 'native_usage': {k: 10 for k in usage.benchmark.FIELDS}}
        created = usage.automatic_baseline(self.root, record)
        self.assertEqual(created['status'], 'baseline_recorded')
        original = Path(created['path']).read_bytes()
        increased = {**record, 'first_input_tokens': 120}
        result = usage.automatic_baseline(self.root, increased)
        self.assertEqual(result['observed_increases'], ['first_input_tokens'])
        self.assertEqual(Path(created['path']).read_bytes(), original)
        rotated = copy.deepcopy(record)
        rotated['binding'].update(run_id='new-run', ended_at='2026-09-25T12:00:03Z', mcp_raw_sha256='rotated-token', config_raw_sha256='new-home')
        self.assertEqual(usage.automatic_baseline(self.root, rotated)['status'], 'compared')
        unknown = copy.deepcopy(rotated)
        unknown['binding']['comparison_unavailable'] = 'Enabled broker has no stable identity'
        self.assertEqual(usage.automatic_baseline(self.root, unknown)['status'], 'incomparable')
        self.assertFalse(usage.compare(record, unknown)['compatible'])
        changed = copy.deepcopy(increased)
        changed['comparison_key']['model'] = 'different'
        self.assertFalse(usage.compare(record, changed)['compatible'])
        for key in ('brief_sha256', 'checkpoint_sha256'):
            changed_work = copy.deepcopy(increased)
            changed_work['comparison_key'][key] = 'replaced'
            self.assertFalse(usage.compare(record, changed_work)['compatible'])
        self.assertEqual(usage.automatic_baseline(self.root, changed)['status'], 'baseline_recorded')

    def test_live_issue_controller_profile_uses_local_cli_and_neutral_cwd(self):
        local_cli = self.write('.tools/multica/bin/' + ('multica.exe' if os.name == 'nt' else 'multica'), b'fixture')
        completed = subprocess.CompletedProcess([], 0, cb.encode(self.issue), b'')
        with patch.dict(os.environ, {}, clear=True), patch.object(cb.subprocess, 'run', return_value=completed) as run:
            self.assertEqual(cb.live_issue(self.root, self.issue['id'], 'meridiansquad'), self.issue)
            run.assert_called_once_with([str(local_cli), '--profile', 'meridiansquad', 'issue', 'get', self.issue['id'], '--output', 'json'],
                                        cwd=self.root.parent, capture_output=True, timeout=25)
        with patch.dict(os.environ, {'CONTEXT_BUDGET_MULTICA': 'explicit-cli', 'CONTEXT_BUDGET_MULTICA_PROFILE': 'meridiansquad'}, clear=True), patch.object(cb.subprocess, 'run', return_value=completed) as run:
            cb.live_issue(self.root, self.issue['id'])
            self.assertEqual(run.call_args.args[0][:3], ['explicit-cli', '--profile', 'meridiansquad'])
            self.assertEqual(run.call_args.kwargs['cwd'], self.root.parent)
            run.reset_mock()
            with self.assertRaisesRegex(ValueError, 'Controller profile is forbidden'):
                cb.live_issue(self.root, self.issue['id'], allow_controller=False)
            run.assert_not_called()

    def test_live_issue_worker_keeps_scoped_auth_and_rejects_owner_profile(self):
        scoped = {'MULTICA_TOKEN': 'fixture-scoped-token', 'MULTICA_TASK_ID': self.issue['id'], 'MULTICA_TASK_CONFIG_ROOT': 'fixture-scoped-config'}
        completed = subprocess.CompletedProcess([], 0, cb.encode(self.issue), b'')
        with patch.dict(os.environ, scoped, clear=True), patch.object(cb.subprocess, 'run', return_value=completed) as run:
            cb.live_issue(self.root, self.issue['id'])
            self.assertEqual(run.call_args.args[0], ['multica', 'issue', 'get', self.issue['id'], '--output', 'json'])
            self.assertEqual(run.call_args.kwargs, {'cwd': self.root, 'capture_output': True, 'timeout': 25})
            self.assertEqual(dict(os.environ), scoped)
            run.reset_mock()
            with self.assertRaisesRegex(ValueError, 'Controller profile is forbidden'):
                cb.live_issue(self.root, self.issue['id'], 'meridiansquad')
            os.environ['CONTEXT_BUDGET_MULTICA_PROFILE'] = 'meridiansquad'
            with self.assertRaisesRegex(ValueError, 'Controller profile is forbidden'):
                cb.live_issue(self.root, self.issue['id'])
            run.assert_not_called()

    def test_brief_checkpoint_staleness_budget_and_live_closed_state(self):
        brief = self.brief()
        cp = {'schema_version': 1, **cb.identity(self.root, self.issue, 'candidate-1', 'Docs/authority.json'),
              'brief_sha256': cb.digest(cb.encode(brief)), 'next_step': 'Run focused checks', 'pending': [], 'evidence': []}
        cb.validate_document(self.root, 'brief', brief, self.issue)
        cb.validate_document(self.root, 'checkpoint', cp, self.issue, brief)
        for field, value in [('candidate', 'candidate-2'), ('scope_sha256', 'old'), ('revision', 'old')]:
            bad = copy.deepcopy(cp); bad[field] = value
            with self.assertRaises(ValueError): cb.validate_document(self.root, 'checkpoint', bad, self.issue, brief)
        with self.assertRaises(ValueError): cb.validate_document(self.root, 'brief', brief, {**self.issue, 'status': 'done'})
        with self.assertRaises(ValueError): cb.validate_document(self.root, 'brief', {**brief, 'objective': 'x'*4096}, self.issue)
        with self.assertRaises(ValueError): cb.validate_document(self.root, 'brief', brief, {**self.issue, 'description': 'new scope'})
        cb.atomic(cb.task_path(self.root, self.issue['id'], 'brief'), cb.encode(brief))
        with patch.object(cb, 'live_issue', return_value=self.issue):
            self.assertTrue(cb.prepare(self.root, {'issue_id': self.issue['id']})['passed'])
            with self.assertRaises(ValueError): cb.prepare(self.root, {'issue_id': self.issue['id'], 'resume_expected': True})
            cb.atomic(cb.task_path(self.root, self.issue['id'], 'checkpoint'), cb.encode(cp))
            self.assertTrue(cb.prepare(self.root, {'issue_id': self.issue['id'], 'resume_expected': True})['passed'])

    def test_usage_deduplicates_native_responses_and_resumed_boundary(self):
        thread = self.issue['id']
        path = self.root / 'sessions/rollout-test.jsonl'
        rows = [{'type': 'session_meta', 'payload': {'id': thread, 'cli_version': '0.153.4'}}]
        for n in range(1, 4):
            rows.append({'type': 'turn_context', 'timestamp': f'2026-09-24T12:00:0{n}Z', 'payload': {'model': 'gpt-6-astra', 'effort': 'max'}})
            row = {'type': 'token_usage_record', 'timestamp': f'2026-09-24T12:00:0{n}Z',
                   'payload': {'thread_id': thread, 'response_id': str(n), 'usage': {'input_tokens': n*100, 'cached_input_tokens': 50,
                               'output_tokens': 10, 'reasoning_output_tokens': 5, 'total_tokens': n*100+10}}}
            rows.extend([row, row])
        self.write('sessions/rollout-test.jsonl', '\n'.join(json.dumps(r) for r in rows))
        result = usage.benchmark.collect_native_usage(path, '2026-09-24T12:00:02Z', thread)
        self.assertEqual(result['unique_response_count'], 2)
        self.assertEqual(result['first_input_tokens'], 200)
        self.assertEqual(result['native_usage']['output_tokens'], 20)
        self.assertEqual(result['native_usage']['input_tokens'], 500)
        self.assertEqual(result['native_usage']['cached_input_tokens'], 100)
        self.assertTrue(result['output_includes_reasoning_check'])
        first = usage.benchmark.collect_native_usage(path, '2026-09-24T12:00:01Z', thread, '2026-09-24T12:00:02Z')
        self.assertEqual(first['unique_response_count'], 2)
        self.assertEqual(first['native_usage']['input_tokens'], 300)

    def test_capture_bounded_output_complete_artifact_and_exit(self):
        result = subprocess.run([sys.executable, str(ROOT / 'Scripts/ContextBudget/context_budget.py'), '--root', str(self.root),
                                 'run', '--label', 'capture-test', '--', sys.executable, '-c', 'import sys; print("x"*10000); sys.exit(7)'], capture_output=True)
        self.assertEqual(result.returncode, 7)
        self.assertLess(len(result.stdout), 1024)
        manifest = cb.read_json(json.loads(result.stdout)['artifact'])
        self.assertGreater(Path(manifest['stdout']).stat().st_size, 10000)


if __name__ == '__main__':
    unittest.main()
