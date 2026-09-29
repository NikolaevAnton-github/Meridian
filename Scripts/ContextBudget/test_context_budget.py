"""Focused standalone context-guard and output-capture regression tests."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import context_budget as cb

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
        cb.git(self.root, 'init', '-q')
        cb.git(self.root, 'add', '.')
        cb.git(self.root, '-c', 'user.name=Context Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'Fixture')

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


    def test_retired_runtime_instructions_rejected_in_worktree_and_index(self):
        original = (self.root / 'AGENTS.md').read_bytes()
        self.write('AGENTS.md', original + cb.BEGIN + b'Generated' + cb.END)
        self.assertFalse(cb.guard(self.root)['passed'])
        cb.git(self.root, 'add', 'AGENTS.md')
        self.assertFalse(cb.guard(self.root, 'staged')['passed'])

    def test_capture_bounded_output_complete_artifact_and_exit(self):
        result = subprocess.run([sys.executable, str(ROOT / 'Scripts/ContextBudget/context_budget.py'), '--root', str(self.root),
                                 'run', '--label', 'capture-test', '--', sys.executable, '-c', 'import sys; print("x"*10000); sys.exit(7)'], capture_output=True)
        self.assertEqual(result.returncode, 7)
        self.assertLess(len(result.stdout), 1024)
        manifest = cb.read_json(json.loads(result.stdout)['artifact'])
        self.assertGreater(Path(manifest['stdout']).stat().st_size, 10000)


if __name__ == '__main__':
    unittest.main()
