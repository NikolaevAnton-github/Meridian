"""Bounded project footprint audit, including Git, services and generated files."""
import json
import os
import argparse
from pathlib import Path
ROOT=Path('D:/devgames/MeridianSquad')
parser=argparse.ArgumentParser()
parser.add_argument('--evidence-root',default='Saved/ReinforcedColumn01/Candidate01')
options=parser.parse_args()
OUT=ROOT/options.evidence_root
pending=[ROOT]
size=count=0
errors=[]
while pending:
    folder=pending.pop()
    try:
        with os.scandir(folder) as entries:
            for entry in entries:
                if entry.is_dir(follow_symlinks=False):
                    pending.append(entry.path)
                elif entry.is_file(follow_symlinks=False):
                    try:
                        size+=entry.stat(follow_symlinks=False).st_size
                        count+=1
                    except OSError as error:
                        errors.append(str(error))
    except OSError as error:
        errors.append(str(error))
record=dict(root=str(ROOT),bytes=size,files=count,limit_bytes=250000000000,errors=errors)
path=OUT/'storage.json'
assert not path.exists()
path.write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record))
assert not errors and size < record['limit_bytes']
