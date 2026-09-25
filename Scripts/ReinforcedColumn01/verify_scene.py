"""Compare saved/reopened actors and protected source bytes with the task snapshot."""
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import unreal as u
ROOT=Path('D:/devgames/MeridianSquad')
OUT=ROOT/'Saved/ReinforcedColumn01/Candidate01'

def capture(name):
    spec=importlib.util.spec_from_file_location('ngd_inspect',ROOT/'Scripts/NextGenDestructionIntegration01/inspect_scene.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows=module.actors()
    before=json.loads((OUT/'editor-before.json').read_text())['actors']
    def stable(row):
        return re.sub(r'0x[0-9A-Fa-f]+','PTR',json.dumps(row,sort_keys=True))
    old={r['name']:r for r in before}
    now={r['name']:r for r in rows}
    removed=sorted(set(old)-set(now))
    added=sorted(set(now)-set(old))
    changed=[n for n in old if n in now and stable(old[n])!=stable(now[n])]
    hashes=json.loads((OUT/'before-hashes.json').read_text())
    protected_changes=[p for p,h in hashes.items() if p!='Content/Maps/L_OpeningLobby_PainterStone01.umap' and hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    dirty=[x.get_path_name() for x in list(u.EditorLoadingAndSavingUtils.get_dirty_map_packages())+list(u.EditorLoadingAndSavingUtils.get_dirty_content_packages())]
    report=dict(actors=rows,removed=removed,added=added,changed=changed,protected_changes=protected_changes,protected_file_count=len(hashes)-1,dirty=dirty)
    path=OUT/(name+'.json')
    assert not path.exists()
    path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    assert removed==[] and len(added)==1 and changed==['StaticMeshActor_35'], report.keys()
    assert not protected_changes and not dirty
    print(json.dumps({k:v for k,v in report.items() if k!='actors'}))
