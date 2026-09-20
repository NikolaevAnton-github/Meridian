"""Read-only preservation/storage audit for the controller handoff."""
import hashlib
import json
import os
import subprocess
import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlStepping01/Worker'
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()
def write(name,value):
    p=OUT/name
    assert not p.exists(),p
    p.write_text(json.dumps(value,indent=2),encoding='utf-8')

rows=[]
for entry in json.loads((OUT.parent/'Controller/preservation-before.json').read_text(encoding='utf-8-sig')):
    path=Path(entry['Path']); current=digest(path)
    rows.append(dict(path=path.relative_to(ROOT).as_posix(),expected=entry['Hash'].lower(),actual=current,match=current==entry['Hash'].lower()))
baseline=ROOT/'Saved/CombatSlice01/PhysicsControlRecovery01/Worker/Candidate04/manifest.json'
for entry in json.loads(baseline.read_text()):
    name=entry['path']
    if name.startswith('Content/') or name.startswith('Source/MeridianSquad/DummyRecovery') or name.endswith('MeridianSquad.Build.cs'):
        current=digest(ROOT/name)
        rows.append(dict(path=name,expected=entry['sha256'],actual=current,match=current==entry['sha256']))
content_diff=subprocess.check_output(['git','diff','--name-only','--','Content','Assets'],cwd=ROOT,text=True).strip()
if not (OUT/'preservation-after01.json').exists():
    write('preservation-after01.json',dict(checks=rows,all_match=all(x['match'] for x in rows),content_source_diff=content_diff))
assert all(x['match'] for x in rows) and not content_diff

total=count=0
reparse=[]
for directory,dirs,files in os.walk(ROOT,followlinks=False):
    # Windows Multica task roots include junctions back to the project. Python
    # 3.11 followlinks=False does not exclude junctions, so exclude all reparse
    # directories explicitly instead of traversing a cycle or an external tree.
    kept=[]
    for name in dirs:
        p=Path(directory)/name
        if p.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            reparse.append(p.relative_to(ROOT).as_posix())
        else:
            kept.append(name)
    dirs[:]=kept
    for name in files:
        p=Path(directory)/name
        if not p.is_symlink():
            try:
                total+=p.stat().st_size; count+=1
            except FileNotFoundError:
                pass # Live local service temporary files may disappear during the read.
storage=dict(bytes=total,GB=total/1e9,GiB=total/1024**3,files=count,limit_GB=250,within_limit=total<250e9,
             excluded_reparse_directories=reparse,method='Physical project tree, excluding junction/symlink directories; hardlink aliases are conservatively counted separately.')
write('storage-after01.json',storage)
print(json.dumps(dict(preserved=len(rows),bytes=total,GB=total/1e9,files=count,
                      excluded_reparse_directories=len(reparse),within_limit=storage['within_limit'])))
