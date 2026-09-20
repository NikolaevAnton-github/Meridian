"""Verify protected fingerprints, execution identity and physical storage use."""
import hashlib
import json
import os
import stat
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/CombatSlice01/PhysicsControlLegPose01/Worker'
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def write(name,value):
    p=OUT/name;assert not p.exists(),p;p.write_text(json.dumps(value,indent=2),encoding='utf-8')

rows=[]
for e in json.loads((OUT.parent/'Controller/preservation-before.json').read_text(encoding='utf-8-sig')):
    p=Path(e['Path']);actual=digest(p)
    rows.append(dict(path=p.relative_to(ROOT).as_posix(),expected=e['Hash'].lower(),actual=actual,match=actual==e['Hash'].lower()))
for e in json.loads((ROOT/'Saved/CombatSlice01/PhysicsControlStepping01/Worker/Candidate05/manifest.json').read_text()):
    p=e['path']
    if p.startswith('Content/') or p.startswith('Source/MeridianSquad/DummyRecovery'):
        actual=digest(ROOT/p);rows.append(dict(path=p,expected=e['sha256'],actual=actual,match=actual==e['sha256']))
diff=subprocess.check_output(['git','diff','--name-only','--','Content','Assets'],cwd=ROOT,text=True).strip()
write('preservation-after01.json',dict(checks=rows,all_match=all(x['match'] for x in rows),content_source_diff=diff))
assert all(x['match'] for x in rows) and not diff

context=json.loads((OUT.parent/'Controller/native-context01.json').read_text(encoding='utf-8-sig'))
native=None
for line in Path(context['session_file']).read_text(encoding='utf-8').splitlines():
    entry=json.loads(line)
    if entry.get('type')=='turn_context':
        p=entry['payload'];native={k:p.get(k) for k in ['model','effort','service_tier','collaboration_mode']};break
process=json.loads((OUT.parent/'Controller/native-process01.json').read_text(encoding='utf-8-sig'))
assert native and native['model']=='gpt-6-astra' and native['effort']=='max' and native['service_tier'] in [None,'default','standard']
assert '--disable fast_mode' in process['CommandLine'] and 'service_tier=' in process['CommandLine']
write('native-execution01.json',dict(context=native,process_id=process['ProcessId'],native_arguments=process['CommandLine'],profile_administration=False))

total=count=aliases=0
for directory,dirs,files in os.walk(ROOT,followlinks=False):
    kept=[]
    for n in dirs:
        if (Path(directory)/n).lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:aliases+=1
        else:kept.append(n)
    dirs[:]=kept
    for n in files:
        p=Path(directory)/n
        if not p.is_symlink():
            try:total+=p.stat().st_size;count+=1
            except FileNotFoundError:pass
write('storage-after01.json',dict(bytes=total,GB=total/1e9,files=count,excluded_reparse_directories=aliases,
    within_250GB=total<250e9,method='Physical tree without junction/symlink directory aliases; hardlink files conservatively counted separately.'))
assert total<250e9
print(json.dumps(dict(preserved=len(rows),native=native,GB=total/1e9,excluded_directory_aliases=aliases)))
