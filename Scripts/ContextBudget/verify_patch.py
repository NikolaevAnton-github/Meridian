"""Replay the additive patch on only its pinned base files; no full worktree."""
from pathlib import Path
import subprocess
import tempfile
from context_budget import atomic, digest, encode, git, read_json, report

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / '.tools/multica/source'


def main():
    manifest = read_json(ROOT / 'Saved/ContextBudget02/Worker/patch-manifest.json')
    patch = ROOT / manifest['patch']
    if digest(patch.read_bytes()) != manifest['patch_sha256']:
        raise ValueError('Patch identity changed')
    replay = Path(tempfile.mkdtemp(prefix='patch-replay-', dir=ROOT / 'Saved/ContextBudget02/Worker'))
    for relative in manifest['source_files']:
        result = subprocess.run(['git', '-C', str(SOURCE), 'show', manifest['base_commit']+':'+relative], capture_output=True, timeout=20)
        if result.returncode == 0:
            atomic(replay / relative, result.stdout)
    git(replay, 'init', '-q')
    git(replay, 'config', 'core.autocrlf', 'false')
    git(replay, 'apply', '--check', str(patch))
    git(replay, 'apply', str(patch))
    for relative, expected in manifest['source_files'].items():
        if digest((replay / relative).read_bytes()) != expected:
            raise ValueError('Replayed source differs: ' + relative)
    report(ROOT, {'passed': True, 'source_files': len(manifest['source_files']), 'patch_sha256': manifest['patch_sha256'], 'replay': str(replay)},
           str(ROOT / 'Saved/ContextBudget02/Worker/patch-replay.json'))


if __name__ == '__main__':
    main()
