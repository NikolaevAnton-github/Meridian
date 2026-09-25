"""Verify final handoff state and fingerprint the exact candidate and evidence."""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT=Path('D:/devgames/MeridianSquad')
OUT=ROOT/'Saved/LobbyPlaytestFix01/Candidate01'
def read(name):
    return json.loads((OUT/name).read_text(encoding='utf-8'))
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical(row):
    return re.sub(r'0x[0-9a-fA-F]+','<address>',json.dumps(row,sort_keys=True))

checks=read('focused-checks.json')['checks']
assert len(checks)==42 and all(c['passed'] for c in checks)
handoff=read('editor-handoff.json')
assert not handoff['pie'] and not handoff['dirty_maps'] and not handoff['dirty_content']
assert handoff['world']=='/Game/Maps/L_OpeningLobby_PainterStone01.L_OpeningLobby_PainterStone01'
assert handoff['performance']==read('performance-before.json')
before={a['name']:a for a in read('editor-before.json')['actors']}
after={a['name']:a for a in handoff['actors']}
assert len(after)==len(before)+11
assert all(canonical(a)==canonical(after[name]) for name,a in before.items())
assert canonical(handoff['props'])==canonical(read('editor-reopened.json')['props'])
protected=read('before-hashes.json')
assert all(digest(ROOT/p)==h for p,h in protected.items() if not p.startswith('Content/Maps/'))
build=read('Build02.json')
assert all(digest(ROOT/p)==h for p,h in build['files'].items())
map_path=ROOT/'Content/Maps/L_OpeningLobby_PainterStone01.umap'
assert digest(map_path)=='94dbedbe2e516fc8cdde2d394f2b4c8c0a4d9573288e94772a6ebefafd54bc57'
reset=read('pie-visual-reset.json')
assert len(reset['after']['props'])==14 and all(p['ready'] and not p['root_broken'] and p['delivered_hits']==0 and p['break_events']==0 for p in reset['after']['props'])
assert reset['before']['rifle']['magazine']==reset['after']['rifle']['magazine']
for name in ['pie-concrete-broken.png','pie-concrete-reset.png']:
    assert (OUT/name).stat().st_size>100000
files=[ROOT/p for p in build['files']]+[map_path,ROOT/'Docs/LobbyPlaytestFix01.md',ROOT/'Docs/Tasks/LobbyPlaytestFix01.md']
files+=sorted((ROOT/'Scripts/LobbyPlaytestFix01').glob('*.py'))
evidence=sorted(p for p in OUT.rglob('*') if p.is_file())
manifest=dict(candidate='MSQ-152-Candidate01',build='Build02',checks_passed=len(checks),native_contract_checks=14,
    preserved_actor_count=len(before),new_actor_count=11,specimen_count=14,
    protected_file_count=len(protected)-1,
    files={p.relative_to(ROOT).as_posix():digest(p) for p in files},
    evidence={p.relative_to(OUT).as_posix():dict(sha256=digest(p),bytes=p.stat().st_size) for p in evidence},
    warning='One recovered editor GeometryCollectionSceneProxy assertion during initial move/save; final save/reload/PIE passed.',
    pending='Independent technical review and owner play/layout acceptance; controller owns status and commit.')
name=sys.argv[1] if len(sys.argv)>1 else 'delivery-final-manifest'
assert name.replace('-','').isalnum()
path=OUT/(name+'.json')
assert not path.exists()
path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in manifest.items() if k not in ['files','evidence']}))
