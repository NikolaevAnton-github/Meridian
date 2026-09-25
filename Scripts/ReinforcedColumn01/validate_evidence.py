"""Validate the final candidate's bounded runtime and preservation evidence."""
import hashlib
import json
import math
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/ReinforcedColumn01/Candidate01'

def read(name): return json.loads((OUT/name).read_text(encoding='utf-8'))
def stable(value): return re.sub(r'0x[0-9A-Fa-f]+','PTR',value)
def moved(a,b,start=0,end=288,tolerance=.01):
    return [i for i in range(start,end) if math.dist(a['pieces'][i]['location'],b['pieces'][i]['location'])>tolerance]

impact=read('review-impact.json')
burst=read('review-burst.json')
layers=read('review-layers.json')
reset=read('review-reset.json')
next_shot=read('review-after-reset-shot.json')
for run in [impact,burst,layers,reset,next_shot]:
    assert 'error' not in run
    for row in [run['before']]+run['samples']+[run['after']]:
        assert row['global_dilation']==1 and row['player_dilation']==1
        assert stable(row['core_transform'])==stable(impact['before']['core_transform'])
        assert stable(row['core_bounds'])==stable(impact['before']['core_bounds'])
        assert not moved(run['before'],row,288,576)
assert impact['after']['rifle']['shots']-impact['before']['rifle']['shots']==1
assert impact['after']['prop']['delivered_hits']==1
assert len(moved(impact['before'],impact['after']))==1
assert burst['after']['rifle']['shots']-burst['before']['rifle']['shots']>=8
assert not moved(burst['before'],burst['after'])
assert layers['after']['rifle']['shots']-layers['before']['rifle']['shots']==3
removed=moved(impact['before'],layers['after'])
assert len(removed)==4
design=json.loads((ROOT/'Assets/Source/ReinforcedColumn01/design.json').read_text())
assert any(design['piece_meta'][i]['shallow'] for i in removed)
assert any(not design['piece_meta'][i]['shallow'] for i in removed)
assert reset['after']['prop']['reset_generation']==1 and not reset['after']['prop']['root_broken']
assert reset['after']['prop']['materials']==impact['before']['prop']['materials']
assert not moved(impact['before'],reset['after'])
assert next_shot['after']['prop']['delivered_hits']==1 and next_shot['after']['prop']['reset_generation']==1
assert next_shot['after']['rifle']['shots']-next_shot['before']['rifle']['shots']==1
assert len(moved(next_shot['before'],next_shot['after']))==1
collision=read('review-cavity-collision.json')
assert all(t['result']['impact'][1]<-124 for t in collision)
scene=read('review-reopened.json')
assert not scene['removed'] and scene['changed']==['StaticMeshActor_35'] and len(scene['added'])==1
assert not scene['protected_changes'] and not scene['dirty']
assert read('Build08.json')['exit_code']==0
assert read('Build09.json')['exit_code']==0
assert read('inspector-only-diff.json')['passed']
assert read('core-seams01.json')['passed']
managed=read('managed-collection-comparison.json')
assert managed['candidate']['anchored_count']==288
assert managed['candidate']['level_counts']=={'0':1,'1':576}
assert read('source-check02.json')['source_sha256']==hashlib.sha256((ROOT/'Assets/Source/ReinforcedColumn01/column.json').read_bytes()).hexdigest()
assert read('storage.json')['bytes']<250000000000
settings=read('native-settings.json')
assert settings['configured']['model_reasoning_effort']=='max' and settings['configured']['service_tier']=='default'
assert all(c['model']=='gpt-6-astra' and c['effort']=='max' for c in settings['actual_contexts'])
assert all(c['fast_disabled'] and c['tier']=='default' for c in settings['native_arguments'])
views=['review-intact.png','review-damaged-layers.png','review-detail.png','review-reset.png']
assert all((OUT/n).stat().st_size>50000 for n in views)
result=dict(passed=True,normal_speed=True,single_shot_delta=1,sustained_shots=burst['after']['rifle']['shots']-burst['before']['rifle']['shots'],
    local_layer_shots=3,removed_body_indices=removed,fixed_bond_anchor_movement=0,continuous_core_unchanged=True,
    reset_generation=1,next_shot_works=True,collision_depth_cm=[round(-120-t['result']['impact'][1],3) for t in collision],
    preserved_files=scene['protected_file_count'],unrelated_actors_preserved=len(scene['actors'])-2,views=views,
    engine_build='Build09',runtime_evidence_build='Build08',asset_build='asset-build07.json',
    inspector_only_change_verified=True,geometric_core_closure_verified=True,managed_vendor_comparison_recorded=True)
path=OUT/(sys.argv[1] if len(sys.argv)>1 else 'verification.json')
assert not path.exists()
path.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
