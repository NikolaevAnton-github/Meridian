"""Focused assertions over retained native records; does not drive or rerun Unreal."""
import collections
import itertools
import json
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlRecoverability01/Worker'
sys.path.insert(0, str(ROOT / 'Scripts/PhysicsControlLegPose01'))
from inspect91 import geometry, norm, sub

NAMES = ['Baseline-OneLeg01', 'Candidate07-OneLeg', 'Candidate06-OneLegComparable',
         'Candidate07-TorsoBurstResume', 'Candidate06-TorsoRearFast', 'Candidate06-TorsoRearOrdinary',
         'Candidate06-BothWeak', 'Candidate06-NoSupportAssist', 'Candidate06-LegContactWeak',
         'Candidate06-DeathDuring', 'Candidate07-Controls', 'Candidate06-SlowEpisode',
         'Candidate07-ThreeRendered']
DATA = {name: json.loads((OUT / (name + '.json')).read_text()) for name in NAMES}
CHECKS, METRICS = [], {}


def check(name, condition, detail=None):
    CHECKS.append(dict(name=name, passed=bool(condition), detail=detail))


def rows(name):
    return [r for r in DATA[name]['rows'] if r.get('dummy')]


def hits(name):
    found = {}
    for r in rows(name):
        c = r['combat']
        if c['last_hit_shot'] and c['last_hit'].startswith('PHYSICS HIT'):
            found[c['last_hit_shot']] = c['last_hit'].split('|')[1].strip()
    return collections.Counter(found.values())


def changes(name):
    result, previous = [], None
    for r in rows(name):
        d = r['dummy']
        key = (d['balance']['state'], d['step']['phase'], d['step']['completed'], d['epoch'])
        if key != previous:
            result.append(dict(t=r['t'], state=key[0], phase=key[1], completed=key[2],
                               reason=d['balance']['reason'], held=r['rifle']['fire_held']))
            previous = key
    return result


for name, data in DATA.items():
    xs = rows(name)
    final = xs[-1]['dummy']
    check(name + ': recorder completed', data['error'] is None and xs[-1]['t'] >= data['config']['duration'])
    video = json.loads((OUT / 'Video' / (name + '.capture.json')).read_text())
    times = [f['t'] for f in video['frames']]
    METRICS[name] = dict(samples=len(xs), hits=dict(hits(name)), transitions=changes(name),
        final_state=final['balance']['state'], steps=final['step']['completed'], falls=final['balance']['falls'],
        get_ups=final['balance']['get_ups'], video=dict(frames=len(times), duration=times[-1],
        average_fps=(len(times)-1)/times[-1], largest_gap=max(b-a for a,b in zip(times,times[1:]))))
    check(name + ': ordinary continuous WGC capture', video['backend'] == 'WGC' and
          times[-1] >= data['config']['duration'] and all(b > a for a,b in zip(times,times[1:])))
    if name.startswith('Baseline'):
        continue
    check(name + ': all existing drives have finite nonzero effort limits', all(
        math.isfinite(c[k]) and c[k] > 0 for r in xs for c in r['dummy']['controls'] for k in ['max_force','max_torque']))
    check(name + ': no powered standing/step without usable contact', all(
        d['balance']['enabled_drives'] == 0 or d['balance']['usable_feet'] > 0
        for r in xs if (d := r['dummy'])['balance']['state'] in ['STANDING','UNSTEADY','STEPPING']))
    check(name + ': fall/down/death release every drive', all(
        r['dummy']['balance']['enabled_drives'] == 0 for r in xs
        if r['dummy']['balance']['state'] in ['FALLING','DOWN','CORPSE']))
    check(name + ': get-up powered only with ground contact', all(
        d['balance']['enabled_drives'] == 0 or d['balance']['usable_feet'] > 0 or
        d['recoverability']['body_ground_contact_age'] < .20 + r['world_delta'] + .001
        for r in xs if (d := r['dummy'])['balance']['state'] == 'GETTING UP'))
    check(name + ': capacity clamps respected', all(
        .25 <= c['strength'] <= 2 and .5 <= c['speed'] <= 1.80001 and
        12 <= c['reach_limit_cm'] <= 45 and .5 <= c['persistence_limit_seconds'] <= 4
        for r in xs for c in [r['dummy']['recoverability']]))
    check(name + ': no automatic timed leg invalidation', all(
        r['dummy']['balance']['left_leg_disabled'] == r['dummy']['balance']['right_leg_disabled'] == 0 for r in xs))
    check(name + ': fresh session assistance off', not xs[0]['combat']['recovery_assistance'])
    METRICS[name]['effort_limits'] = {k: xs[-1]['dummy']['recoverability'][k] for k in
        ['strength','speed','reach_limit_cm','persistence_limit_seconds','force_limit_sum_kg_cm_s2','torque_limit_sum_kg_cm2_s2']}

baseline = rows('Baseline-OneLeg01')
fall = next(r for r in baseline if r['dummy']['balance']['state'] == 'FALLING')
check('baseline: real calf bullet reproduces disabled-leg rejection', hits('Baseline-OneLeg01') == {'calf_l':1}
      and fall['dummy']['balance']['usable_feet'] == 1 and 'usable legs' in fall['dummy']['balance']['reason'])

settled_cases = ['Candidate07-OneLeg','Candidate06-OneLegComparable','Candidate07-TorsoBurstResume',
                'Candidate06-TorsoRearFast','Candidate06-TorsoRearOrdinary','Candidate06-BothWeak','Candidate06-SlowEpisode']
for name in settled_cases:
    xs = rows(name)
    gs = [geometry(r['leg_bones']) for r in xs]
    knee = max(g[s]['knee_to_toe'] for g in gs for s in ['l','r'])
    length_error = max(abs(g[s]['lengths'][i]-gs[0][s]['lengths'][i]) for g in gs for s in ['l','r'] for i in [0,1])
    drift = max(r['dummy']['step']['peak_support_drift_cm'] for r in xs)
    end = xs[-1]['dummy']
    foot_move = {s: norm(sub(xs[-1]['leg_bones']['foot_'+s]['p'][:2],xs[0]['leg_bones']['foot_'+s]['p'][:2])) for s in ['l','r']}
    METRICS[name]['geometry'] = dict(max_knee_to_toe_degrees=knee, final_knee_to_toe_degrees=max(gs[-1][s]['knee_to_toe'] for s in ['l','r']),
        maximum_segment_length_change_cm=length_error, peak_support_drift_cm=drift, foot_displacement_cm=foot_move,
        pelvis_displacement_cm=norm(sub(xs[-1]['leg_bones']['pelvis']['p'][:2],xs[0]['leg_bones']['pelvis']['p'][:2])),
        final_sole_gaps_cm=[end['balance']['sole_left_z']-end['balance']['ground_z'],end['balance']['sole_right_z']-end['balance']['ground_z']])
    check(name + ': final supported settlement without fall', end['balance']['state']=='STANDING' and end['balance']['falls']==0 and end['balance']['usable_feet']==2)
    # Geometric engineering bounds, not clinical joint angles or motion acceptance.
    check(name + ': knees remain in the toe-facing half-plane', knee < 90)
    check(name + ': segment lengths preserve anatomy within 1 cm', length_error < 1)
    check(name + ': planted support drift below retained 2 cm diagnostic', drift < 2)
    check(name + ': settled sole calibration within retained 1 cm tolerance', all(-.2 <= z <= 1 for z in METRICS[name]['geometry']['final_sole_gaps_cm']))
    check(name + ': targets respect fixed joint envelope', max(r['dummy']['step']['joint_limit_error_degrees'] for r in xs) <= 3)
    check(name + ': active step clock is not reset by a hit', all(
        b['dummy']['step']['seconds'] >= a['dummy']['step']['seconds'] for a,b in zip(xs,xs[1:])
        if a['dummy']['step']['started']==b['dummy']['step']['started'] and
        a['dummy']['step']['phase']!='IDLE' and b['dummy']['step']['phase']!='IDLE'))

leg=rows('Candidate07-OneLeg')[-1]['dummy']
check('one leg: true calf hit, damage and displaced-leg replant', hits('Candidate07-OneLeg') == {'calf_l':1}
      and leg['health']==75 and leg['step']['completed']>=1 and METRICS['Candidate07-OneLeg']['geometry']['foot_displacement_cm']['l']>5
      and METRICS['Candidate07-OneLeg']['geometry']['pelvis_displacement_cm']>5)
burst=rows('Candidate07-TorsoBurstResume')
completed=[b for a,b in zip(burst,burst[1:]) if b['dummy']['step']['completed']>a['dummy']['step']['completed']]
check('burst: all 30 actual bullets hit torso', sum(hits('Candidate07-TorsoBurstResume').values())==30 and all(k.startswith('spine_') for k in hits('Candidate07-TorsoBurstResume')))
check('burst: at least three placements complete while firing is held', sum(r['rifle']['fire_held'] for r in completed)>=3)
press=[e for e in DATA['Candidate07-TorsoBurstResume']['events'] if e['key']=='LeftMouseButton' and e['value']==1]
resume=next(r for r in burst if r['t']>=press[1]['t'])
check('burst: resumed before recovery settled', len(press)==2 and resume['dummy']['balance']['state']!='STANDING'
      and burst[-1]['rifle']['input_presses']==2 and burst[-1]['rifle']['shots']==30)
sessions=collections.Counter(s['session'] for s in burst[-1]['rifle']['recent_shots'])
METRICS['Candidate07-TorsoBurstResume']['rifle_sessions']=dict(sessions)
check('burst: resumed trigger produces multiple real bullets', len(sessions)==2 and min(sessions.values())>=2)

ordinary, fast = DATA['Candidate06-TorsoRearOrdinary']['config'].copy(),DATA['Candidate06-TorsoRearFast']['config'].copy()
for c in [ordinary,fast]:
    c.pop('name'); c.pop('tuning',None)
check('settings: same representative and scenario, only speed changes', ordinary==fast and
      DATA['Candidate06-TorsoRearFast']['config']['tuning']=={'recovery_speed':1.5})
check('settings: bounded speed changes completed recovery capacity', METRICS['Candidate06-TorsoRearFast']['steps']>
      METRICS['Candidate06-TorsoRearOrdinary']['steps'] and METRICS['Candidate06-TorsoRearOrdinary']['steps']>2)
check('both-leg recoverable: two simultaneous controlled disturbances',
      [e['value'][3] for e in DATA['Candidate06-BothWeak']['events'] if e['key']=='@impulse']==['calf_l','calf_r']
      and rows('Candidate06-BothWeak')[-1]['rifle']['shots']==0)

no=rows('Candidate06-NoSupportAssist'); event=next(e for e in DATA['Candidate06-NoSupportAssist']['events'] if e['key']=='@environment')
lost=next(r for r in no if r['t']>event['t'] and r['dummy']['balance']['usable_feet']==0)
fell=next(r for r in no if r['dummy']['balance']['state']=='FALLING')
METRICS['Candidate06-NoSupportAssist']['loss']=dict(remove_time=event['t'],zero_drive_time=lost['t'],fall_time=fell['t'],
    pelvis_drop_after_loss_cm=lost['dummy']['bodies']['pelvis']['position'][2]-no[-1]['dummy']['bodies']['pelvis']['position'][2])
check('no support: assistance cannot veto loss of both feet', lost['combat']['recovery_assistance'] and lost['dummy']['balance']['enabled_drives']==0
      and fell['t']-event['t']<.3 and no[-1]['dummy']['balance']['state']=='FALLING')
check('no support: physical downward motion, no suspension', METRICS['Candidate06-NoSupportAssist']['loss']['pelvis_drop_after_loss_cm']>200)

asset=json.loads((OUT/'baseline-asset01.json').read_text())
excluded={frozenset([e['a'],e['b']]) for e in asset['excluded_pairs']}
pairs=list(itertools.product(['thigh_l','calf_l','foot_l'],['thigh_r','calf_r','foot_r']))
check('asset: all nine opposite-leg pairs enabled, selective exclusions retained', len(excluded)>0 and all(frozenset(p) not in excluded for p in pairs))
contact=rows('Candidate06-LegContactWeak')
index=next(i for i,r in enumerate(contact) if r['dummy']['recoverability']['leg_contacts'])
first=contact[index]['dummy']['recoverability']['leg_contacts'][0]
dist=DATA['Candidate06-LegContactWeak']['events']
fall=next(r for r in contact if r['dummy']['balance']['state']=='FALLING')
METRICS['Candidate06-LegContactWeak']['collision']=dict(t=contact[index]['t'],contact=first,
    impulse_magnitude_kg_cm_s=norm(first['normal_impulse']), actual_external_impulse_kg_cm_s=norm(next(r['dummy']['step']['impulse'] for r in contact if r['t']>=dist[0]['t'])),
    right_calf_velocity_before=contact[index-1]['dummy']['bodies']['calf_r']['linear_velocity'],
    right_calf_velocity_at_contact=first['calf_r_velocity'],
    support_slip_before_cm_s=contact[index-1]['dummy']['recoverability']['feet'][1]['slip_cm_s'],
    support_slip_next_cm_s=contact[index+1]['dummy']['recoverability']['feet'][1]['slip_cm_s'],
    peak_support_drift_cm=max(r['dummy']['step']['peak_support_drift_cm'] for r in contact),fall_time=fall['t'],fall_reason=fall['dummy']['balance']['reason'])
check('contact: only left calf receives injected impulse', len(dist)==1 and dist[0]['key']=='@sweep_leg' and dist[0]['applied_to']=='calf_l')
check('contact: solver records actual opposite-leg collision and right-side motion', {first['a'],first['b']}=={'foot_l','calf_r'}
      and norm(first['normal_impulse'])>1 and norm(sub(first['calf_r_velocity'],contact[index-1]['dummy']['bodies']['calf_r']['linear_velocity']))>5)
check('contact: support disturbed and bounded landing fails', METRICS['Candidate06-LegContactWeak']['collision']['support_slip_next_cm_s']>5
      and 'failed to land' in fall['dummy']['balance']['reason'])
check('contact: retained living fall/get-up completes', contact[-1]['dummy']['balance']['get_ups']==1 and contact[-1]['dummy']['balance']['state']=='STANDING'
      and contact[-1]['dummy']['health']==100)

death=rows('Candidate06-DeathDuring'); dead=next(r for r in death if r['dummy']['health']==0)
check('death: real second bullet terminates active swing', any(e['key']=='during_step_kill' and e['step']['phase']=='SWING' for e in DATA['Candidate06-DeathDuring']['events'])
      and dead['rifle']['shots']==2 and dead['dummy']['deaths']==1 and death[-1]['dummy']['balance']['state']=='CORPSE'
      and death[-1]['dummy']['balance']['get_ups']==0)
controls=DATA['Candidate07-Controls']['rows']
reset=next(e for e in DATA['Candidate07-Controls']['events'] if e['key']=='during_step_reset')
after=next(r for r in controls if r['t']>reset['t'] and r['dummy']['epoch']==2)
off=next(r for r in controls if r['counts']['dummy']==0)
on=next(r for r in controls if r['t']>off['t'] and r['counts']['dummy']==3)
check('controls: F6 cancels swing and clears recovery while retaining assistance', reset['step']['phase']=='SWING' and after['combat']['recovery_assistance']
      and after['dummy']['step']['started']==0 and after['dummy']['recoverability']['leg_contacts']==[])
check('controls: F10 removes and recreates exactly three identities with assistance', off['combat']['recovery_assistance'] and on['combat']['recovery_assistance']
      and [f['profile'] for f in on['fixtures']]==[1,2,3] and on['dummy']['step']['started']==0)
check('controls: Ctrl+F9 returns to ordinary bounded capacity', not controls[-1]['combat']['recovery_assistance']
      and controls[-1]['dummy']['recoverability']['strength']==1)
slow=rows('Candidate06-SlowEpisode')
active=[r for r in slow if r['global_dilation']==.25 and r['dummy']['step']['phase']!='IDLE']
check('slowdown: affected step uses world time with partial player slowdown', len(active)>5 and all(abs(r['combat']['player_action_rate']-.65)<1e-5
      and abs(r['player_dilation']-2.6)<1e-5 for r in active) and slow[-1]['global_dilation']==1)
clock_errors=[abs((b['dummy']['step']['seconds']-a['dummy']['step']['seconds'])-(b['world_time']-a['world_time']))
              for a,b in zip(active,active[1:]) if a['dummy']['step']['started']==b['dummy']['step']['started']]
check('slowdown: step clock follows measured world delta', bool(clock_errors) and max(clock_errors)<.04)
check('render: three original fixture identities present', all([f['profile'] for f in r['fixtures']]==[1,2,3] for r in rows('Candidate07-ThreeRendered')))

audits=[]
for name in settled_cases+['Candidate06-LegContactWeak']:
    for path in sorted(OUT.glob(name+'-*pose-*.json')):
        p=json.loads(path.read_text()); ground=p['runtime']['balance']['ground_z']
        gaps={s:min(v['world'][2] for v in p['skin']['foot_vertices'] if v['bone'].endswith('_'+s))-ground for s in ['l','r']}
        audits.append(dict(file=path.name,sole_gaps_cm=gaps))
check('skin: all retained settled CPU sole audits satisfy 1 cm calibration', len(audits)>=len(settled_cases) and all(-.2<=v<=1 for a in audits for v in a['sole_gaps_cm'].values()))
result=dict(candidate='Candidate07',checks=CHECKS,passed=sum(c['passed'] for c in CHECKS),total=len(CHECKS),
            samples=sum(len(d['rows']) for d in DATA.values()),metrics=METRICS,skin_audits=audits,
            applicability='Candidate06 non-initialization behavior reused; Candidate07 rechecks finite disabled drive creation, F6/F10, one-leg replant and sustained torso burst. See the report for exact source differences.')
destination=OUT/(sys.argv[1] if len(sys.argv)>1 else 'self-checks02.json')
with destination.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
print(json.dumps(dict(passed=result['passed'],total=result['total'],samples=result['samples'],skin_audits=len(audits),
                     failures=[c for c in CHECKS if not c['passed']])))
sys.exit(0 if result['passed']==result['total'] else 1)
