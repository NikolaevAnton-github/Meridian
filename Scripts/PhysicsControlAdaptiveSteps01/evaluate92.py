"""Evaluate affected native motion records with the retained anatomical evaluator."""
import collections
import json
import math
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlAdaptiveSteps01/Worker'
sys.path.insert(0, str(ROOT / 'Scripts/PhysicsControlLegPose01'))
from inspect91 import geometry

PREFIX = 'Candidate03-'
NAMES = ['Small', 'Large', 'Replan', 'Blocked', 'Slow', 'Controls', 'Rifle', 'ReferenceSpeed', 'TorsoTempo', 'ThreeRendered']
RECORDS = {name:PREFIX+name for name in NAMES}
RECORDS.update(Blocked='Candidate03-Blocked02', TorsoTempo='Candidate05-TorsoTempo', Replan='Candidate05-Replan')
RECORDS.update(Small='Candidate05-Small', Large='Candidate05-Large')
DATA = {name: json.loads((OUT / (RECORDS[name] + '.json')).read_text()) for name in NAMES}
CHECKS, METRICS = [], {}

def check(name, passed, detail=None):
    CHECKS.append(dict(name=name, passed=bool(passed), detail=detail))

def dist(a, b):
    return math.dist(a[:2], b[:2])

def rows(name):
    return [r for r in DATA[name]['rows'] if r.get('dummy')]

def phase_rows(name):
    return [r for r in rows(name) if r['dummy']['step']['phase'] != 'IDLE']

for name, data in DATA.items():
    xs = rows(name)
    active = phase_rows(name)
    post = [r for r in xs if r['dummy']['balance']['state'] == 'STANDING' and r['dummy']['step']['completed']]
    final = xs[-1]['dummy']
    check(name + ': native record completed', data['error'] is None and data['rows'][-1]['t'] >= data['config']['duration'])
    frames = json.loads((OUT / 'Video' / (RECORDS[name] + '.capture.json')).read_text())
    times = [f['t'] for f in frames['frames']]
    check(name + ': continuous ordinary-speed WGC evidence', frames['backend'] == 'WGC' and len(times) > 25
          and all(b > a for a, b in zip(times, times[1:])) and times[-1] >= data['config']['duration'])
    groups = collections.defaultdict(list)
    for r in active:
        groups[(r['dummy']['epoch'], r['dummy']['step']['started'])].append(r)
    transitions, prior = [], None
    for r in xs:
        d = r['dummy']; s = d['step']; b = d['balance']
        key = (b['state'], s['phase'], s['completed'], d['epoch'])
        if key != prior:
            transitions.append(dict(t=r['t'], world_time=r['world_time'], state=b['state'], phase=s['phase'], completed=s['completed'], reason=b['reason']))
            prior = key
    hits = {}
    for r in xs:
        c = r['combat']
        if c['last_hit_shot'] and c['last_hit'].startswith('PHYSICS HIT'):
            hits[c['last_hit_shot']] = c['last_hit'].split('|')[1].strip()
    metrics = METRICS[name] = dict(record=RECORDS[name],samples=len(xs), final_state=final['balance']['state'], steps=final['step']['completed'],
        falls=final['balance']['falls'], hits=dict(collections.Counter(hits.values())), transitions=transitions,
        video=dict(frames=len(times), seconds=times[-1], fps=(len(times)-1)/times[-1], max_gap=max(b-a for a,b in zip(times,times[1:]))), steps_measured=[])
    if name != 'Controls':
        check(name + ': three identities retained', all([f['profile'] for f in r['fixtures']] == [1,2,3] for r in xs))
    check(name + ': bounded drives and support retained', all(
        (d['balance']['enabled_drives'] == 0 or d['balance']['usable_feet'] > 0) and
        all(c['max_force'] > 0 and c['max_torque'] > 0 for c in d['controls'])
        for r in active if (d := r['dummy'])))
    check(name + ': falling releases all drives', all(r['dummy']['balance']['enabled_drives'] == 0 for r in xs
        if r['dummy']['balance']['state'] in ['FALLING','DOWN','CORPSE']))
    for key, group in groups.items():
        first, last = group[0], group[-1]
        s = first['dummy']['step']; foot = s['swing_foot']; side = foot[-1]
        durations = s['phase_durations_seconds']
        label = name + ': step ' + str(key)
        check(label + ' deadlines frozen', all(r['dummy']['step']['phase_durations_seconds'] == durations for r in group))
        check(label + ' clock never restarts', all(b['dummy']['step']['seconds'] > a['dummy']['step']['seconds']
              for a,b in zip(group,group[1:])))
        check(label + ' reachable targets and bounded replans', all(
            dist(t['destination'],t['swing_start']) <= r['dummy']['recoverability']['reach_limit_cm'] + .01 and
            t['replans'] <= 2 and t['replan_travel_cm'] <= 6.001
            for r in group for t in [r['dummy']['step']]))
        check(label + ' stable planted target', all(dist(s['plant_target'],r['dummy']['step']['plant_target']) < 1e-6 for r in group))
        drift = max(r['dummy']['step']['peak_support_drift_cm'] for r in group)
        check(label + ' planted drift below 2 cm', drift <= 2, drift)
        target_rates = [dist(a['dummy']['step']['destination'],b['dummy']['step']['destination']) /
            max(1e-8,b['world_time']-a['world_time']) for a,b in zip(group,group[1:])]
        check(label + ' filtered target at most 50 cm/s', max(target_rates,default=0) <= 50.1, max(target_rates,default=0))
        swing = [r for r in group if r['dummy']['step']['phase'] == 'SWING']
        interior = [r for r in swing if .15 <= (r['dummy']['step']['seconds']-durations[0])/durations[1] <= .85]
        sole_key = 'sole_left_z' if side == 'l' else 'sole_right_z'
        gaps = [r['dummy']['balance'][sole_key]-r['dummy']['balance']['ground_z'] for r in swing]
        check(label + ' swing floor clearance', all(r['dummy']['balance'][sole_key]-r['dummy']['balance']['ground_z'] > .1 for r in interior))
        geoms = [geometry(r['leg_bones']) for r in group]
        alignment = max(g[x]['knee_to_toe'] for g in geoms for x in ['l','r'])
        check(label + ' anatomical bend and reach', alignment < 45 and all(
            7 < g[x]['flex'] < 95 and abs(g[x]['lengths'][0]-43.4) < 1 and abs(g[x]['lengths'][1]-42.3) < 1
            for g in geoms for x in ['l','r']), alignment)
        check(label + ' fixed target joint envelope', max(r['dummy']['step']['joint_limit_error_degrees'] for r in group) <= 3)
        completed = next((r for r in xs if r['world_time'] > first['world_time'] and
            r['dummy']['epoch'] == key[0] and r['dummy']['step']['completed'] >= key[1]), None)
        m = dict(epoch=key[0], index=key[1], impulse=s['impulse'], body_direction=s['body_direction'], entry_velocity=s['entry_velocity_cm_s'],
            lean=s['entry_lean_degrees'], lean_excursion=s['entry_lean_excursion_degrees'], demand=s['entry_demand_cm'],
            length=s['selected_length_cm'], lift=s['selected_lift_cm'], phase_seconds=durations, reaction_seconds=s['reaction_seconds'],
            speed=s['entry_speed'], peak_lift=max(gaps,default=0), minimum_swing_gap=min(gaps,default=0),
            peak_support_drift=drift, replans=max(r['dummy']['step']['replans'] for r in group),
            replan_travel=max(r['dummy']['step']['replan_travel_cm'] for r in group), max_target_rate=max(target_rates,default=0),
            actual_step_seconds=completed['world_time']-first['world_time'] if completed else None,
            actual_foot_displacement=dist(first['leg_bones'][foot]['p'],completed['leg_bones'][foot]['p']) if completed else None,
            pelvis_displacement=dist(first['leg_bones']['pelvis']['p'],completed['leg_bones']['pelvis']['p']) if completed else None)
        metrics['steps_measured'].append(m)
    if name in ['Small','Large','Replan','Slow','Rifle','ReferenceSpeed','TorsoTempo']:
        check(name + ': physical recovery completes', bool(post) and final['balance']['falls'] == 0 and final['step']['completed'] > 0)
        if post:
            gs = [geometry(r['leg_bones']) for r in post]
            yaw = max(g[x]['knee_to_toe'] for g in gs for x in ['l','r'])
            gaps = [r['dummy']['balance'][k]-r['dummy']['balance']['ground_z'] for r in post for k in ['sole_left_z','sole_right_z']]
            check(name + ': final alignment and sole contact', yaw < 25 and min(gaps) >= 0 and max(gaps) <= 1, dict(knee_to_toe=yaw,gaps=[min(gaps),max(gaps)]))
            metrics['final_knee_to_toe_max'] = yaw
            metrics['final_sole_gaps'] = [min(gaps),max(gaps)]
            skin_files = list(OUT.glob(RECORDS[name] + '-recovery-pose-*.json'))
            check(name + ': final CPU-skinned audit available', bool(skin_files))
            metrics['skin_gaps'] = []
            for file in skin_files:
                audit = json.loads(file.read_text()); ground = audit['runtime']['balance']['ground_z']
                gap = {side:min(v['world'][2] for v in audit['skin']['foot_vertices'] if v['bone'].endswith('_'+side))-ground for side in ['l','r']}
                check(file.stem + ': actual skinned soles 0-1 cm', all(0 <= x <= 1 for x in gap.values()), gap)
                metrics['skin_gaps'].append(dict(file=file.name,gaps=gap))

small, large = [METRICS[name]['steps_measured'][0] for name in ['Small','Large']]
check('pair: visibly different placement', large['actual_foot_displacement'] > small['actual_foot_displacement'] * 1.5,
      [small['actual_foot_displacement'],large['actual_foot_displacement']])
check('pair: measured lift scales', large['peak_lift'] > small['peak_lift'] + 1.5, [small['peak_lift'],large['peak_lift']])
check('pair: geometry and duration selected together', large['phase_seconds'] != small['phase_seconds'] and
      large['length']/large['phase_seconds'][1] > small['length']/small['phase_seconds'][1])
check('pair: body lean drives meaningful scaling', large['lean_excursion'] > small['lean_excursion'] + 2)
replan = METRICS['Replan']['steps_measured'][0]
check('mid-step: bounded nonzero replan observed', 0 < replan['replans'] <= 2 and .5 < replan['replan_travel'] <= 6)
check('blocked: invalid landing physically falls', any(e['key'] == 'block_landing' for e in DATA['Blocked']['events']) and
    any(r['dummy']['balance']['state'] == 'FALLING' and 'step support lost' in r['dummy']['balance']['reason'] for r in rows('Blocked')))
slow = [r for r in rows('Slow') if r['global_dilation'] == .25 and r['dummy']['step']['phase'] != 'IDLE']
check('slowdown: affected step uses world time, player remains relative', len(slow) > 8 and all(abs(r['player_dilation']-2.6) < .001 for r in slow))
check('slowdown: phase elapsed matches world delta', all(abs((b['dummy']['step']['seconds']-a['dummy']['step']['seconds'])-
    (b['world_time']-a['world_time'])) < .002 for a,b in zip(slow,slow[1:]) if a['dummy']['step']['started'] == b['dummy']['step']['started']))
controls = rows('Controls')
reset = [r for r in controls if r['dummy']['epoch'] > controls[0]['dummy']['epoch'] and r['t'] < 2.2]
check('F6: active adaptive state cleared', bool(reset) and all(r['dummy']['step']['started'] == 0 and
    r['dummy']['step']['selected_length_cm'] == r['dummy']['step']['selected_lift_cm'] == r['dummy']['step']['replans'] == 0 and
    not r['dummy']['step']['replan_pending'] and r['dummy']['step']['replan_goal'] == [0,0,0] for r in reset))
check('F10: removed and recreated', any(not r.get('dummy') for r in DATA['Controls']['rows']) and
      any(r['t'] > 2.8 and len(r['fixtures']) == 3 and r['dummy']['step']['started'] == 0 and r['dummy']['step']['selected_lift_cm'] == 0 for r in controls))
rifle, reference = [METRICS[name]['steps_measured'][0] for name in ['Rifle','ReferenceSpeed']]
check('tempo: adjustable speed 1.25, response and settle 20 percent shorter', rifle['speed'] == 1.25 and reference['speed'] == 1 and
      abs(rifle['reaction_seconds']/reference['reaction_seconds']-.8) < .0001 and
      abs(rifle['phase_seconds'][2]/reference['phase_seconds'][2]-.8) < .0001)
check('tempo: observed quicker rifle step', rifle['actual_step_seconds'] < reference['actual_step_seconds'] * .86,
      [rifle['actual_step_seconds'],reference['actual_step_seconds']])
check('tempo: same actual calf bullet at both speeds', METRICS['Rifle']['hits'] == METRICS['ReferenceSpeed']['hits'] == {'calf_l':1})
check('torso: repeated rifle hits settle with bounded replan budget', sum(METRICS['TorsoTempo']['hits'].values()) >= 8 and METRICS['TorsoTempo']['steps'] >= 2)
result = dict(candidate='Candidate05 native source and build; branch-applicable Candidate03 evidence', records=RECORDS, checks=CHECKS, metrics=METRICS,
              passed=sum(c['passed'] for c in CHECKS), total=len(CHECKS), failures=[c for c in CHECKS if not c['passed']])
name = sys.argv[1] if len(sys.argv) > 1 else 'self-checks01.json'
with (OUT / name).open('x', encoding='utf-8') as stream:
    json.dump(result, stream, indent=2)
print(json.dumps(dict(passed=result['passed'], total=result['total'], failures=result['failures'])))
