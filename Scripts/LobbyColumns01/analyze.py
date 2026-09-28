"""Verify the two representative live-rifle probes and all reset instances."""
import json
from pathlib import Path

OUT=Path(__file__).resolve().parents[2]/'Saved/LobbyColumns01'
reports={}
for name,count in [('low03',10),('tall01',15)]:
    data=json.loads((OUT/(name+'.json')).read_text())
    assert not data.get('error'),data.get('error')
    assert data['after']['rifle']['shots']-data['before']['rifle']['shots']==count
    assert data['after']['rifle']['dry_fire']==data['before']['rifle']['dry_fire']
    marked={row['label']:row for row in data['marked']}
    for z in (22,810):
        a,b=marked[f'before-{z}'],marked[f'after-{z}']
        assert b['cladding']['concrete_impacts']>a['cladding']['concrete_impacts']
        assert b['cladding']['released_concrete']>a['cladding']['released_concrete']
        assert b['cladding']['attached']<a['cladding']['attached']
    if name=='tall01':
        a,b=marked['before-890'],marked['after-890']
        assert b['rifle']['shots']-a['rifle']['shots']==5
        for key in ['concrete_impacts','released_concrete','attached']:
            assert b['cladding'][key]==a['cladding'][key]
    fresh=marked['reset']
    assert fresh['cladding']['attached']==768 and fresh['cladding']['concrete_impacts']==0
    assert fresh['prop']['reset_generation']==data['before']['prop']['reset_generation']+1
    for row in data['samples']:
        for key in ['protected_core_moved','unsupported_wall_tiles','debris_inside_core','retained_tile_simulating','retained_concrete_nonkinematic']:
            assert row['cladding'][key]==0,(name,key,row['elapsed'])
        assert row['cladding']['retention_slots']<=80
    reports[name]=dict(shots=count,base_and_top_destructible=True,reset_complete=True,core_stable=True)
rows=json.loads((OUT/'runtime-final.json').read_text())
columns=[r for r in rows if '/LobbyColumns01/' in r['prop']['data_asset']]
assert len(columns)==16
for row in columns:
    assert row['prop']['ready'] and row['prop']['reset_generation']==3
    assert row['cladding']['attached']==768
    assert abs(row['rebar_z'][0]+30)<.01 and abs(row['rebar_z'][1]-840)<.01
traces=json.loads((OUT/'traces.json').read_text())
assert traces['lower']['blocked'] and traces['lower']['actor'].startswith('BP_BreakableObject_')
assert traces['upper']['blocked'] and traces['upper']['actor']=='StaticMeshActor_38'
reports.update(reset_instances=16,rebar_z_cm=[-30,840],tall_upper_static=True)
(OUT/'analysis.json').write_text(json.dumps(reports,indent=2))
print(json.dumps(reports))
