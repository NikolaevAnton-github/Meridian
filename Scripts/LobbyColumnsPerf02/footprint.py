"""Count project-owned bytes without recursively following Windows junctions."""
import json
import os
import stat
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/LobbyColumnsPerf02/footprint03.json'
totals={}; links=[]; errors=[]; files=0
for top in os.scandir(ROOT):
    total=0; pending=[top.path]
    while pending:
        path=pending.pop()
        try:
            info=os.stat(path,follow_symlinks=False)
            if info.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                links.append(path);continue
            if stat.S_ISDIR(info.st_mode):
                with os.scandir(path) as entries:pending.extend(e.path for e in entries)
            else:total+=info.st_size;files+=1
        except OSError:errors.append(path)
    totals[top.name]=total
    OUT.write_text(json.dumps(dict(complete=False,by_top_level_bytes=totals,files=files),indent=2))
report=dict(complete=True,total_bytes=sum(totals.values()),total_gib=sum(totals.values())/1024**3,
            by_top_level_bytes=totals,files=files,excluded_reparse_points=links,errors=errors)
OUT.write_text(json.dumps(report,indent=2))
print(json.dumps({k:report[k] for k in ['complete','total_bytes','total_gib','files']}))
