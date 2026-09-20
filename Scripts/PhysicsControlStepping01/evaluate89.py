"""Focused acceptance measurements from the retained runtime and CPU skin audits.

This checks behavior in recorded episodes, not a mirror of the stepping solver.
Visual weight/feel remains an owner gate; inspect the continuous MP4s separately.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlStepping01/Worker'
NAMES = ['Frontal', 'BodyLateralTurned', 'WeakRifleFall', 'Rehit', 'Blocked', 'LegLoss',
         'Death', 'SlowReset', 'ResetDuring', 'SixRendered']
checks, measurements, data = [], {}, {}
PREFIX = sys.argv[1] if len(sys.argv) > 1 else 'Candidate04'
def record_name(suffix):
    return ('Candidate03' if suffix == 'SixRendered' else PREFIX) + '-' + suffix

def check(name, passed, observed=None):
    checks.append(dict(name=name, passed=bool(passed), observed=observed))

def dist(a, b, dimensions=2):
    return math.sqrt(sum((x-y)**2 for x, y in zip(a[:dimensions], b[:dimensions])))

def dot(a, b):
    return sum(x*y for x, y in zip(a, b))

def unit(v):
    length = math.sqrt(dot(v, v))
    return [x / length for x in v] if length else [0, 0, 0]

def at(rows, t):
    return min(rows, key=lambda row: abs(row['t']-t))

for suffix in NAMES:
    name = record_name(suffix)
    d = json.loads((OUT / (name + '.json')).read_text())
    rows = d['rows']
    data[suffix] = d
    active = [r for r in rows if r['dummy']]
    steps = [r for r in active if r['dummy']['balance']['state'] == 'STEPPING']
    standing = [r for r in active if r['dummy']['balance']['state'] == 'STANDING']
    stable = [r for r in standing if r['dummy']['balance']['instability'] <= .001]
    gaps = [r['dummy']['balance'][key] - r['dummy']['balance']['ground_z']
            for r in stable for key in ['sole_left_z','sole_right_z']]
    label_gaps = [r['dummy']['balance'][key] - r['dummy']['balance']['ground_z']
                  for r in standing for key in ['sole_left_z','sole_right_z']]
    check(name+': recorder completed', d['error'] is None and rows[-1]['t'] >= d['config']['duration'])
    check(name+': other five fixtures unchanged', all(x['health'] == 100 and x['hits'] == 0 and x['deaths'] == 0
          for r in rows for x in r['fixtures'] if x['profile'] != 1))
    check(name+': maximum two steps per episode', all(r['dummy']['step']['episode_steps'] <= 2 for r in active))
    check(name+': all fall/down/death drives released', all(r['dummy']['balance']['enabled_drives'] == 0 for r in active
          if r['dummy']['balance']['state'] in ['FALLING','DOWN','CORPSE']))
    check(name+': no healing within an epoch', all(b['dummy']['health'] <= a['dummy']['health'] for a,b in zip(active,active[1:])
          if a['dummy']['name'] == b['dummy']['name'] and a['dummy']['epoch'] == b['dummy']['epoch']))
    check(name+': stable standing visible sole tolerance (instability zero)', bool(gaps) and min(gaps) >= 0 and max(gaps) <= 1, [min(gaps),max(gaps)])
    after_step = [r['dummy']['balance'][key] - r['dummy']['balance']['ground_z'] for r in standing
                  if r['dummy']['step']['completed'] > 0 for key in ['sole_left_z','sole_right_z']]
    if after_step:
        check(name+': every post-step standing sample keeps sole tolerance',min(after_step)>=0 and max(after_step)<=1,[min(after_step),max(after_step)])
    m = dict(samples=len(rows), standing_sole_gap_cm=[min(gaps),max(gaps)],
             all_standing_label_sole_gap_cm=[min(label_gaps),max(label_gaps)],
             steps_completed=max(r['dummy']['step']['completed'] for r in active),
             max_joint_gap_cm=max(r['dummy']['max_locked_joint_anchor_gap_cm'] for r in active),
             final_health=active[-1]['dummy']['health'],
             magazine=[rows[0]['rifle']['magazine'],rows[-1]['rifle']['magazine']], steps=[])
    if steps:
        check(name+': complete pose supplied while stepping', all(r['dummy']['step']['full_pose_bones'] == 89 for r in steps))
        drift = max(r['dummy']['step']['support_drift_cm'] for r in steps)
        check(name+': support ankle drift <= 2 cm', drift <= 2, drift)
        for number in sorted({r['dummy']['step']['started'] for r in steps}):
            part = [r for r in steps if r['dummy']['step']['started'] == number]
            first = part[0]['dummy']['step']
            transfer = [r for r in part if r['dummy']['step']['phase'] == 'TRANSFER']
            swing = [r for r in part if r['dummy']['step']['phase'] == 'SWING']
            weight_direction = unit(first['weight_transfer'])
            start_pelvis = part[0]['dummy']['bodies']['pelvis']['position']
            weight_motion = max([dot([a-b for a,b in zip(r['dummy']['bodies']['pelvis']['position'],start_pelvis)],weight_direction)
                                for r in transfer] or [0])
            sole_key = 'sole_left_z' if first['swing_foot'] == 'foot_l' else 'sole_right_z'
            swing_gap = max([r['dummy']['balance'][sole_key]-r['dummy']['balance']['ground_z'] for r in swing] or [0])
            m['steps'].append(dict(number=number,swing_foot=first['swing_foot'],support_foot=first['support_foot'],
                start_t=part[0]['t'],end_t=part[-1]['t'],peak_support_drift_cm=max(r['dummy']['step']['support_drift_cm'] for r in part),
                actual_transfer_cm=weight_motion,peak_swing_sole_gap_cm=swing_gap,direction=first['direction'],
                impulse=first['impulse'],facing=first['facing'],body_direction=first['body_direction'],
                direction_impulse_dot=dot(first['direction'],unit(first['impulse'])),
                direction_facing_dot=dot(first['direction'],first['facing'])))
    capture = json.loads((OUT/'Video'/(name+'.capture.json')).read_text())
    frames = capture['frames']
    m['video'] = dict(frames=len(frames),duration=frames[-1]['t'],
        max_gap=max(b['t']-a['t'] for a,b in zip(frames,frames[1:])),
        average_fps=(len(frames)-1)/(frames[-1]['t']-frames[0]['t']))
    check(name+': continuous WGC recording present', len(frames)>30 and frames[-1]['t'] >= d['config']['duration'])
    measurements[suffix] = m

for suffix in ['Frontal','BodyLateralTurned','WeakRifleFall','Rehit','SlowReset']:
    expected = 2 if suffix == 'Rehit' else 1
    check(suffix+': requested recovery steps complete', measurements[suffix]['steps_completed'] == expected)
    for step in measurements[suffix]['steps']:
        check(suffix+f': step {step["number"]} visible swing clearance > 5 cm',step['peak_swing_sole_gap_cm']>5,step['peak_swing_sole_gap_cm'])
        check(suffix+f': step {step["number"]} actual transfer toward support > 2 cm',step['actual_transfer_cm']>2,step['actual_transfer_cm'])
        check(suffix+f': step {step["number"]} follows impulse/body direction',step['direction_impulse_dot']>.85,step['direction_impulse_dot'])
    if suffix in ['Frontal','BodyLateralTurned','Rehit']:
        rows=data[suffix]['rows']
        moved=dist(rows[0]['dummy']['step']['stance_pelvis'],rows[-1]['dummy']['step']['stance_pelvis'])
        check(suffix+': retains displaced standing stance', moved>10 and rows[-1]['dummy']['balance']['state']=='STANDING',moved)
        measurements[suffix]['stance_displacement_cm']=moved

check('front disturbance produces retreat',measurements['Frontal']['steps'][0]['direction_facing_dot']<-.9)
check('turned lateral disturbance remains lateral to the body',abs(measurements['BodyLateralTurned']['steps'][0]['direction_facing_dot'])<.3,
      measurements['BodyLateralTurned']['steps'][0]['direction_facing_dot'])
check('turned body heading differs from baseline',abs(dot(measurements['Frontal']['steps'][0]['facing'],measurements['BodyLateralTurned']['steps'][0]['facing']))<.25)

rows = data['WeakRifleFall']['rows']
check('weak disturbance recovers in place',all(r['dummy']['step']['started']==0 for r in rows if r['t']<3) and at(rows,2.5)['dummy']['balance']['state']=='STANDING')
check('actual rifle contact and health loss',at(rows,4.5)['dummy']['physical_hits']==1 and at(rows,4.5)['dummy']['health']==75 and rows[-1]['rifle']['magazine']==29)
for suffix in ['WeakRifleFall','LegLoss']:
    rows=data[suffix]['rows']
    rec=[r for r in rows if r['dummy']['balance']['state']=='GETTING UP']
    check(suffix+': physical collapse and complete snapshot get-up',bool(rec) and all(r['dummy']['balance']['snapshot_bones']==89 for r in rec)
          and rows[-1]['dummy']['balance']['get_ups']==1 and rows[-1]['dummy']['balance']['state']=='STANDING')
    moved=dist(rows[0]['dummy']['step']['stance_pelvis'],rows[-1]['dummy']['step']['stance_pelvis'])
    check(suffix+': get-up retains a non-home stance',moved>3,moved)
    measurements[suffix]['getup_stance_displacement_cm']=moved

rows=data['Blocked']['rows']
check('blocked destination rejected before swing',rows[-1]['dummy']['step']['rejected']==1 and measurements['Blocked']['steps_completed']==0
      and all(r['dummy']['step']['started']==0 for r in rows) and any(r['dummy']['balance']['state']=='FALLING' for r in rows))
blocked_height=max(r['dummy']['bodies']['pelvis']['position'][2]-r['dummy']['balance']['ground_z'] for r in rows if r['t']>3)
check('blocked recovery remains down with released fall drives; retained get-up may retry',blocked_height<60,blocked_height)
measurements['Blocked']['max_pelvis_height_after_fall_cm']=blocked_height
rows=data['LegLoss']['rows']
check('one unusable support leg releases step',any(r['dummy']['balance']['state']=='FALLING' and
      max(r['dummy']['balance']['left_leg_disabled'],r['dummy']['balance']['right_leg_disabled'])>0 for r in rows))
rows=data['Death']['rows']
dead=[r for r in rows if r['dummy']['deaths']]
check('lethal real rifle contact during swing is terminal',bool(dead) and rows[-1]['rifle']['magazine']==29 and
      all(r['dummy']['step']['phase']=='IDLE' and r['dummy']['health']==0 and r['dummy']['balance']['get_ups']==0 for r in dead)
      and any(e['key']=='during_step_kill' for e in data['Death']['events']))

rows=data['SlowReset']['rows']
slow=[r for r in rows if r['dummy'] and r['dummy']['balance']['state']=='STEPPING' and r['global_dilation']==.25]
check('step uses retained world/player slowdown',len(slow)>50 and all(abs(r['global_dilation']*r['player_dilation']-.65)<.001 for r in slow))
a,b=slow[5],slow[-5]
ratio=(b['dummy']['step']['seconds']-a['dummy']['step']['seconds'])/(b['t']-a['t'])
check('step phase clock advances at quarter rate',abs(ratio-.25)<.01,ratio)
check('Ctrl+F7 and Ctrl+F8 preserved',at(rows,5)['combat']['immortal_dummies'] and at(rows,5)['rifle']['infinite_reserve'])
check('F10 destroys and recreates fresh instance-local state',at(rows,8.25)['counts']['dummy']==0 and at(rows,9)['counts']['dummy']==6
      and at(rows,9)['dummy']['step']['started']==0 and at(rows,9)['dummy']['step']['phase']=='IDLE')
for suffix,t in [('SlowReset',6.4),('ResetDuring',2)]:
    rows=data[suffix]['rows']; after=at(rows,t); before=rows[0]
    check(suffix+': F6 clears state and returns home without ammunition refill', after['dummy']['step']['started']==0 and after['dummy']['step']['completed']==0
          and after['dummy']['step']['seconds']==0 and after['dummy']['step']['cooldown']==0 and not after['dummy']['step']['requested']
          and after['dummy']['epoch']>before['dummy']['epoch'] and after['rifle']['magazine']==29
          and dist(after['dummy']['step']['stance_pelvis'],before['dummy']['step']['stance_pelvis'],3)<.001)

skin=[]
for suffix in NAMES:
    for path in OUT.glob(record_name(suffix)+'-skin-*.json'):
        item=json.loads(path.read_text())
        floor=item['runtime']['balance']['ground_z']
        gaps=[min(v['world'][2] for v in item['foot_vertices'] if v['bone'].endswith(side))-floor for side in ['_l','_r']]
        check(path.stem+': CPU-skinned soles agree with grounding tolerance',min(gaps)>=0 and max(gaps)<=1,gaps)
        skin.append(dict(path=path.name,bones=item['skeleton_bones'],vertices=len(item['foot_vertices']),sole_gaps_cm=gaps))

result=dict(candidate_native=PREFIX,checks=checks,measurements=measurements,skin_audits=skin,
            passed=sum(c['passed'] for c in checks),total=len(checks),
            limits='Runtime measurements and inspected frames do not establish owner motion/play acceptance.')
dest=OUT/(PREFIX+'-focused-results02.json')
assert not dest.exists(),dest
dest.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(dict(passed=result['passed'],total=result['total'],failed=[c for c in checks if not c['passed']],measurements=measurements),indent=2))
