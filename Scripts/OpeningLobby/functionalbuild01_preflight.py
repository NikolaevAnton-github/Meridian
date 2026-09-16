"""Read-only protected fingerprints and no-junction storage accounting."""
import hashlib
import json
import os
import stat
from pathlib import Path
from functionalbuild01_data import ROOT,OUT

def walk(root):
    for base,dirs,files in os.walk(root,followlinks=False):
        dirs[:]=[d for d in dirs if not ((Path(base)/d).lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)]
        for name in files:
            p=Path(base)/name
            if not p.is_symlink():yield p

def digest(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()

def scan():
    OUT.mkdir(parents=True,exist_ok=True)
    target=OUT/'protected-before.json';assert not target.exists()
    entries=[]
    for folder in ['Assets','Content','Config','Scripts','Docs','.agents']:
        for p in walk(ROOT/folder):
            rel=p.relative_to(ROOT).as_posix()
            if 'FunctionalBuild01' in rel or 'functionalbuild01_' in rel or '__pycache__' in rel:continue
            entries.append({'path':rel,'bytes':p.stat().st_size,'sha256':digest(p)})
    total=sum(p.stat().st_size for p in walk(ROOT))
    assert total<250*10**9,total
    target.write_text(json.dumps({'project_bytes':total,'entries':entries},indent=2))
    print(json.dumps({'protected':len(entries),'project_GB':total/1e9}))

if __name__=='__main__':scan()
