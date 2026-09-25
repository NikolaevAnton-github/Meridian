"""Focused evidence checks; never mutates or rebaselines earlier evidence."""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT/'Saved/LobbyPlaytestFix01/Candidate01'
checks = []
def read(name):
    return json.loads((OUT/name).read_text(encoding='utf-8'))
def check(name, passed, detail=None):
    checks.append(dict(name=name,passed=bool(passed),detail=detail))
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical(value):
    return re.sub(r'0x[0-9A-Fa-f]+', '<address>', json.dumps(value,sort_keys=True))

def placement():
    before = {a['name']:a for a in read('editor-before.json')['actors']}
    after = {a['name']:a for a in read('editor-final-placement.json')['actors']}
    changed = [key for key,row in before.items() if key not in after or canonical(row)!=canonical(after[key])]
    check('Original 132 actor records preserved', not changed, changed)
    check('Exactly 11 new actors',len(after)==len(before)+11)
    demo = read('demo-inventory.json')
    props = read('placement-final.json')
    signature = lambda p: canonical([p[k] for k in ['config','collection','materials','scale','gc_collision','gc_damage']])
    source = {signature(p) for p in demo['instances']}
    placed = {signature(p) for p in props}
    check('All 14 distinct configurations from 21 default-demo actors',len(props)==14 and len(source)==14 and placed==source,dict(demo=len(source),placed=len(placed)))
    used = {p['config']['DataAsset'].split('.')[0] for p in props}
    excluded = sorted(set(demo['catalog'])-used)
    check('Catalog reconciliation excludes only two performance examples', [p.split('/')[-1] for p in excluded]==['DA_Pillar_Small_Concrete_Simplified','DA_Pillar_Small_NOFXEXAMPLE'],excluded)
    check('No conservative bounds overlap',not read('spatial-final.json')['conservative_overlaps'])
    check('Central and side route sweeps clear',all(not r['result']['blocked'] for r in read('route-clearance.json')['routes']))

def preservation():
    hashes=read('before-hashes.json')
    changed=[p for p,h in hashes.items() if p!='Content/Maps/L_OpeningLobby_PainterStone01.umap' and digest(ROOT/p)!=h]
    check('Vendor packages and protected owner files byte-identical',not changed,dict(files=len(hashes)-1,changed=changed))
    build=read('Build02.json')
    check('Build02 passed and exact binary/source hashes match',build['exit_code']==0 and all(digest(ROOT/p)==h for p,h in build['files'].items()))

def trace(name):
    p=read(name+'.json')
    check(name+' completed', 'error' not in p and 'after' in p)
    return p

def input_checks():
    a=trace('after-auto-hit')
    check('Auto sustains all 30 rounds through real NGD fracture',a['after']['rifle']['shots']-a['before']['rifle']['shots']==30 and a['after']['rifle']['magazine']==0 and any(p['break_events']>0 for p in a['after']['props']))
    b=trace('before-auto-hit')
    check('Before trace proves canceled held trigger with ammunition',any(s['key_down'] and not s['rifle']['fire_held'] and s['rifle']['magazine']>0 for s in b['samples']))
    b=trace('before-semi-active-debris');a=trace('after-semi-active-debris')
    check('Same four semi presses: two before, four after',b['after']['rifle']['shots']-b['before']['rifle']['shots']==2 and a['after']['rifle']['shots']-a['before']['rifle']['shots']==4)
    for name in ['after-empty-reload-held','after-slow-empty-reload-held-valid']:
        a=trace(name);r=a['after']['rifle'];before=a['before']['rifle']
        check(name+' finite 2+4 rounds and one transfer',r['shots']-before['shots']==6 and r['magazine']==0 and r['reserve']==0 and r['transfers']-before['transfers']==1)
    a=trace('after-auto-hitch-recovery');r=a['after']['rifle']
    check('Auto resumes a single held input after two overloads',a['after']['combat']['overload_frames']-a['before']['combat']['overload_frames']>=2 and r['shots']-a['before']['rifle']['shots']==16 and r['input_presses']-a['before']['rifle']['input_presses']==1)
    a=trace('after-semi-hitch-held')
    check('Held semi press produces exactly one current shot after hitch',a['after']['rifle']['shots']-a['before']['rifle']['shots']==1)
    a=trace('after-semi-hitch-released')
    check('Released deferred press never fires after recovery',a['after']['rifle']['shots']==a['before']['rifle']['shots'])
    a=trace('after-slowdown-transitions-valid')
    slow=[s for s in a['samples'] if s['global_dilation']==.25]
    check('World and rifle quarter clock, player movement 0.65',len(slow)>10 and all(abs(s['player_dilation']*s['global_dilation']-.65)<1e-6 and s['combat']['player_action_rate']==.25 and s['combat']['scale']==.25 for s in slow))
    check('Held auto survives entry and exit from slowdown',a['after']['rifle']['shots']-a['before']['rifle']['shots']==30 and a['after']['global_dilation']==1)
    for name in ['after-auto-hit','after-auto-hitch-recovery','after-slowdown-transitions-valid']:
        a=read(name+'.json');shots=[s for s in a['after']['rifle']['recent_shots'] if s['id']>a['before']['rifle']['last_shot_id']]
        gaps=[y['action_time']-x['action_time'] for x,y in zip(shots,shots[1:])]
        check(name+' never shortens 85 ms rifle spacing',all(g>=.085-1e-6 for g in gaps),dict(min_gap=min(gaps),max_gap=max(gaps)))
    a=trace('after-mode-semi-slow')
    held=[s for s in a['samples'] if .65<s['elapsed']<.8]
    switched=[s for s in a['samples'] if 1.5<s['elapsed']<1.8]
    check('Held mode switch is ignored, released switch takes effect',held and switched and all(s['rifle']['automatic'] for s in held) and all(not s['rifle']['automatic'] for s in switched))
    check('Repeated semi presses across slowdown, with finite ammunition',a['after']['rifle']['shots']-a['before']['rifle']['shots']==12 and a['after']['rifle']['magazine']==4 and a['after']['rifle']['input_presses']-a['before']['rifle']['input_presses']==6)

def destruction_checks():
    a=trace('after-glass-near-cover')
    glass=next(p for p in a['after']['props'] if p['id']=='LPF01_LargeGlass')
    shots=[s for s in a['after']['rifle']['recent_shots'] if s['id']>a['before']['rifle']['last_shot_id']]
    check('Near-cover rifle fractures glass and next shot crosses opening',len(shots)==2 and glass['delivered_hits']==1 and glass['break_events']>0)
    view=next(s['view'] for s in a['samples'] if 1.35<s['elapsed']<1.4)
    check('Blocked muzzle launches from safe view origin',max(abs(x-y) for x,y in zip(view,shots[0]['position']))<.01)
    a=trace('after-mug-variant-reset')
    damaged=[p for s in a['samples'] for p in s['props'] if p['id']=='LPF01_MarbleMug']
    check('Dynamic marble mug receives actual rifle hit and fractures',max(p['delivered_hits'] for p in damaged)==1 and max(p['break_events'] for p in damaged)>0)
    final=a['after']['props']
    check('F6 restores all 14 intact props',len(final)==14 and all(p['ready'] and not p['root_broken'] and p['break_events']==0 and p['delivered_hits']==0 and p['live_fields']==0 for p in final))
    sources={p['config']['DataAsset']:p for p in read('placement-final.json')}
    mismatches=[p['id'] for p in final if p['materials']!=sources[p['data_asset']]['materials'] or p['material_overrides']!=sources[p['data_asset']]['config']['Material Overrides']]
    check('F6 retains all source materials, including marble overrides and glass break switch',not mismatches,mismatches)
    contracts=read('native-contracts.json')
    failed=[k for k,v in contracts.items() if isinstance(v,bool) and not v]
    check('Native collision/reset/timing contracts pass',not failed and contracts.get('held_trigger_recovers_without_geometry_backlog') is True,dict(checks=sum(isinstance(v,bool) for v in contracts.values()),failed=failed))

if __name__ == '__main__':
    name=sys.argv[1]
    placement()
    preservation()
    if '--input' in sys.argv:
        input_checks()
        destruction_checks()
    path=OUT/(name+'.json')
    assert not path.exists()
    path.write_text(json.dumps(dict(checks=checks),indent=2),encoding='utf-8')
    print(json.dumps(checks))
    sys.exit(0 if all(c['passed'] for c in checks) else 1)
