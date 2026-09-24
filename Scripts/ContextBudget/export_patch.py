"""Export only ContextBudget02 changes using a temporary Git index."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
from context_budget import atomic, digest, encode

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / '.tools/multica/source'
OWNED = ['server/internal/daemon/' + name for name in ('daemon.go', 'types.go', 'prompt.go', 'context_budget.go', 'context_budget_test.go', 'context_budget_layers.go', 'context_budget_prompt.go', 'context_budget_prompt_test.go', 'execenv/execenv.go', 'execenv/runtime_config_sections.go')]
OWNED += ['server/pkg/agent/' + name for name in ('agent.go', 'codex.go', 'context_budget_test.go')]
OWNED += ['server/internal/daemon/context_budget_identity.go', 'server/internal/daemon/context_budget_identity_test.go']
PIN = '2ae2dbbb8f9ed9ffe1739ecf5abfe31a940ee50c'


def run(*args, env=None):
    result = subprocess.run(['git', '-C', str(SOURCE), *args], env=env, capture_output=True, timeout=30)
    if result.returncode:
        raise ValueError('Patch export Git operation failed: ' + args[0])
    return result.stdout


def main():
    work = ROOT / 'Saved/ContextBudget02/Worker'
    work.mkdir(parents=True, exist_ok=True)
    if run('rev-parse', 'HEAD').decode().strip() != PIN:
        raise ValueError('Multica source revision differs from pinned patch base')
    before = json.loads((work / 'preservation-before.json').read_text(encoding='utf-8-sig'))
    for path, sha in before.items():
        if digest((SOURCE / path).read_bytes()) != sha:
            raise ValueError('Existing owner Multica source changed: ' + path)
    fd, index = tempfile.mkstemp(prefix='patch-index-', dir=work)
    os.close(fd)
    os.unlink(index)
    env = {**os.environ, 'GIT_INDEX_FILE': index}
    try:
        run('read-tree', 'HEAD', env=env)
        run('add', '--', *OWNED, env=env)
        data = run('diff', '--cached', '--binary', '--', *OWNED, env=env)
        dest = ROOT / 'Tools/ContextBudget02-Multica.patch'
        atomic(dest, data)
        value = {'base_commit': PIN, 'patch': dest.relative_to(ROOT).as_posix(), 'patch_sha256': digest(data),
                 'prior_patch_sha256': digest((ROOT / 'Tools/Patches/multica-0.4.43-local.patch').read_bytes()),
                 'source_files': {p: digest((SOURCE / p).read_bytes()) for p in OWNED}, 'owner_sources_preserved': True}
        atomic(work / 'patch-manifest.json', encode(value))
        print(json.dumps({'patch': value['patch'], 'sha256': value['patch_sha256'], 'source_files': len(OWNED), 'owner_sources_preserved': True}))
    finally:
        for path in (Path(index), Path(index + '.lock')):
            if path.exists(): path.unlink()


if __name__ == '__main__':
    main()
