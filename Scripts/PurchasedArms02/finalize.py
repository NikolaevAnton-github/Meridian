"""Bounded staging cleanup and exact active-source provenance for MSQ-62."""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/PurchasedArms02/Worker'

def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

def prune():
    plan=json.loads((OUT/'dependency-closure.json').read_text())
    assert not plan['missing'] and not plan['forbidden']
    name='unused-staging02.json' if (OUT/'unused-staging.json').exists() else 'unused-staging.json'
    assert not (OUT/name).exists()
    rows=[]
    for r in json.loads((OUT/'staging-manifest.json').read_text())['files']:
        if r['existed'] or r['package'] in plan['keep']: continue
        src=(ROOT/r['destination']).resolve()
        if not src.exists(): continue
        dst=(OUT/'UnusedStaging'/r['destination']).resolve()
        assert src.is_relative_to((ROOT/'Content').resolve())
        assert dst.is_relative_to(OUT.resolve()) and not dst.exists()
        assert sha(src)==r['sha256'],src
        rows.append({'source':str(src),'preserved':str(dst),'sha256':r['sha256']})
    (OUT/name).write_text(json.dumps(rows,indent=2))
    for r in rows:
        src,dst=Path(r['source']),Path(r['preserved'])
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.move(str(src),str(dst))
    print(json.dumps({'preserved_outside_content':len(rows)}))

def manifest():
    rows=[]
    for r in json.loads((OUT/'staging-manifest.json').read_text())['files']:
        p=ROOT/r['destination']
        if not p.exists(): continue
        row=dict(r)
        row['active_sha256']=sha(p)
        row['active_bytes']=p.stat().st_size
        row['modified_copy']=row['active_sha256']!=r['sha256']
        rows.append(row)
    source=ROOT/'Assets/Source/PurchasedArms02/source-manifest.json'
    source.parent.mkdir(parents=True,exist_ok=True)
    source.write_text(json.dumps({'task':'MSQ-62','files':rows,'historical_manifest':'Assets/Archive/PurchasedArms01/manifest.json',
        'note':'New active-copy locations and adaptations. Source and archived hashes remain immutable; this records no art acceptance.'},indent=2))
    fields=subprocess.check_output(['git','check-attr','-z','filter','--stdin'],cwd=ROOT,
        input=('\0'.join(r['destination'] for r in rows)+'\0').encode('utf-8')).decode('utf-8').split('\0')
    lfs='\n'.join(f'{fields[i]}: {fields[i+1]}: {fields[i+2]}' for i in range(0,len(fields)-1,3))
    (OUT/'lfs-policy-final.txt').write_text(lfs)
    assert all(line.endswith(': lfs') for line in lfs.splitlines())
    print(json.dumps({'active':len(rows),'new':sum(not r['existed'] for r in rows),'modified':sum(r['modified_copy'] for r in rows),'bytes':sum(r['active_bytes'] for r in rows)}))

if __name__=='__main__': {'prune':prune,'manifest':manifest}[sys.argv[1]]()
