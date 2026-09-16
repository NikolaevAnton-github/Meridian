"""Bounded disk accounting and preservation of pre-existing project inputs."""
import hashlib
import json
import os
import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'Saved/OpeningLobby/Stage2/Architecture01'

def files(base):
    for parent, dirs, names in os.walk(base, followlinks=False):
        dirs[:] = [n for n in dirs if not ((Path(parent)/n).lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)]
        for name in names:
            p = Path(parent)/name
            if not p.is_symlink():
                yield p

def digest(p):
    with p.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def storage():
    total = 0
    groups = {}
    for p in files(ROOT):
        try:
            size = p.stat().st_size
        except OSError:
            continue
        total += size
        key = p.relative_to(ROOT).parts[0]
        groups[key] = groups.get(key, 0)+size
    return dict(bytes=total, gib=total/1024**3, groups=groups, junctions_followed=False)

def preserve():
    assert not (OUT/'protected-inputs.json').exists()
    entries = {}
    for base in ['Assets/Concepts','Content/Maps','Content/OpeningLobby','Config','Source','Docs','Scripts/OpeningLobby']:
        for p in files(ROOT/base):
            if 'architecture01' not in str(p).lower() and '__pycache__' not in str(p):
                entries[str(p.relative_to(ROOT))] = digest(p)
    for p in [ROOT/'AGENTS.md',ROOT/'.codex/config.toml']:
        entries[str(p.relative_to(ROOT))] = digest(p)
    (OUT/'protected-inputs.json').write_text(json.dumps(entries,indent=2))
    report = storage()
    (OUT/'storage-before.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(dict(protected=len(entries),storage_gib=report['gib'])))

def finish():
    old = json.loads((OUT/'protected-inputs.json').read_text())
    changed = [name for name, sha in old.items() if not (ROOT/name).exists() or digest(ROOT/name)!=sha]
    result = dict(protected=len(old),changed=changed,passed=not changed)
    (OUT/'preservation.json').write_text(json.dumps(result,indent=2))
    inventory = {}
    for base in ['Assets/Source/OpeningLobby/Architecture01','Content/OpeningLobby/Architecture01','Saved/OpeningLobby/Stage2/Architecture01']:
        for p in files(ROOT/base):
            if p.name not in ('inventory.json','storage-after.json') and not p.name.endswith('.painter_lock'):
                inventory[str(p.relative_to(ROOT))] = dict(bytes=p.stat().st_size,sha256=digest(p))
    source_files=list((ROOT/'Scripts/OpeningLobby').glob('*architecture01*.py'))
    document=ROOT/'Docs/OpeningLobbyArchitecture01.md'
    if document.exists():source_files.append(document)
    for p in source_files:
        inventory[str(p.relative_to(ROOT))] = dict(bytes=p.stat().st_size,sha256=digest(p))
    p=ROOT/'Content/Maps/L_OpeningLobby_Architecture01.umap'
    if p.exists():
        inventory[str(p.relative_to(ROOT))] = dict(bytes=p.stat().st_size,sha256=digest(p))
    (OUT/'inventory.json').write_text(json.dumps(inventory,indent=2))
    report=storage()
    report['new_deliverable_bytes']=sum(row['bytes'] for row in inventory.values())
    report['growth_bytes']=report['bytes']-json.loads((OUT/'storage-before.json').read_text())['bytes']
    (OUT/'storage-after.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(dict(preservation=result,storage=report)))

if __name__=='__main__':
    import sys
    preserve() if sys.argv[-1]=='before' else finish()
