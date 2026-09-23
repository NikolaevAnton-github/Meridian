"""Summarize the existing focused recordings; this does not execute gameplay."""
import json
from collections import Counter
from pathlib import Path

OUT=Path(__file__).resolve().parents[2]/'Saved/CombatSlice01/GASPALSEnemy01'

def read(name):
    result=json.loads((OUT/(name+'.json')).read_text())
    assert not result['error'], name
    return result['rows']

def aim_window(rows,start,end):
    values=[r['enemy_rifles'][0] for r in rows if start<=r['t']<=end]
    assert values
    return dict(interval=[start,end],samples=len(values),
        max_aim_error_degrees=max(v['aim_error_degrees'] for v in values),
        max_left_grip_gap_cm=max(v['left_grip_gap_cm'] for v in values),
        root_yaw_range=[min(v['root_relative_aim'][0] for v in values),max(v['root_relative_aim'][0] for v in values)])

poses=read('Pilot02-RiflePoses')
recovery=read('Fix04-CrouchHitAim')
movement=read('Fix03-AimedStop')
death=read('Rollout02-DeathResetSlow')
three=read('Final02-ThreeRendered')
result=dict(
    poses=dict(samples=len(poses),stances=sorted({r['dummy']['gasp']['rifle_stance'] for r in poses}),
        capsule_half_heights=sorted({r['dummy']['gasp']['capsule_half_height'] for r in poses})),
    crouch_hit=dict(samples=len(recovery),authorities=dict(Counter(r['dummy']['gasp']['authority'] for r in recovery)),
        final_health=recovery[-1]['dummy']['health'],hits=recovery[-1]['dummy']['physical_hits'],
        pre_hit=aim_window(recovery,1.4,1.98),post_getup_standing=aim_window(recovery,8.5,10)),
    stopped_aim=[aim_window(movement,*window) for window in [(3.25,3.48),(4.85,5.15),(6.5,6.9),(8,8.48),(12,13)]],
    death_reset_slow=dict(samples=len(death),authorities=dict(Counter(r['dummy']['gasp']['authority'] for r in death)),
        epochs=sorted({r['dummy']['epoch'] for r in death}),global_scales=sorted({r['global_dilation'] for r in death}),
        final_counts=death[-1]['counts']),
    three=dict(samples=len(three),final_counts=three[-1]['counts'],
        profiles=[v['profile'] for v in three[-1]['enemy_rifles']],
        final_aim_error_degrees=[v['aim_error_degrees'] for v in three[-1]['enemy_rifles']]))
with (OUT/'verification-summary.json').open('x',encoding='utf-8') as stream: json.dump(result,stream,indent=2)
print(json.dumps(result,indent=2))
