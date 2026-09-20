"""Acceptance facts from actual continuous runtime records, not a simulated oracle."""
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/CombatSlice01/PhysicsControlBalance01/Worker'
checks=[]
def check(name,value,detail=None):
    checks.append(dict(name=name,passed=bool(value),detail=detail))
def read(name):
    data=json.loads((OUT/(name+'.json')).read_text())
    check(name+' recorder completed',data['error'] is None)
    return data['rows'],data['events']
def b(r):return r['dummy']['balance']
def states(rows,state):return [r for r in rows if b(r)['state']==state]
def norm(v):return math.sqrt(sum(x*x for x in v))

core,events=read('Candidate03-Core')
moderate=[r for r in core if 1.03<r['t']<3.9]
check('Moderate contact preserves life without falling',all(r['dummy']['health']==75 and b(r)['falls']==0 for r in moderate))
drop=max(b(r)['pelvis_drop_cm'] for r in moderate)
lean=max(b(r)['lean_degrees'] for r in moderate)-b(core[0])['lean_degrees']
check('Moderate contact buckles and leans',drop>3 and lean>4,dict(pelvis_drop_cm=drop,lean_excursion_degrees=lean))
check('Moderate contact returns to standing',any(r['t']>3 and b(r)['state']=='STANDING' for r in moderate))
fall=states(core,'FALLING')[0]
check('Repeated real contacts accumulate into a living fall',fall['dummy']['health']==25 and b(fall)['instability']>=1,dict(time=fall['t'],health=fall['dummy']['health'],instability=b(fall)['instability']))
back=states(core,'GETTING UP')
check('Back get-up selected from actual fall',back and all(b(r)['animation']=='A_GetUp_Back' for r in back))
recovered=[r for r in core if b(r)['get_ups']==1 and b(r)['state']=='STANDING']
check('Back get-up completes without healing',recovered and all(r['dummy']['health']==25 for r in recovered))
check('Fall and get-up preserve physical pose epoch',len({r['dummy']['epoch'] for r in core if 5<r['t']<22.9})==1)
check('F6 restores standing without ammunition refill',b(core[-1])['state']=='STANDING' and core[-1]['dummy']['health']==100 and core[-1]['rifle']['magazine']==26)

leg,events=read('Candidate03-LegInterruptedDeath')
first=states(leg,'FALLING')[0]
check('Both unavailable legs release a living body',first['dummy']['health']==50 and b(first)['left_leg_disabled']>0 and b(first)['right_leg_disabled']>0 and b(first)['enabled_drives']==0 and b(first)['instability']<1)
interrupt=[r for r in leg if b(r)['state']=='FALLING' and b(r)['interruptions']>=1]
check('Actual rifle hit interrupts living get-up',interrupt and interrupt[0]['dummy']['health']==25)
dead=states(leg,'CORPSE')
check('Death during subsequent get-up remains terminal',dead and leg[-1]['t']-dead[0]['t']>10 and all(b(r)['state']=='CORPSE' and not r['dummy']['controls'] and r['dummy']['health']==0 for r in leg if r['t']>=dead[0]['t']))

front,events=read('Candidate03-FrontSlow')
check('External impulse causes a living fall without damage',states(front,'FALLING') and all(r['dummy']['health']==100 for r in front) and front[-1]['rifle']['magazine']==30)
prone=states(front,'GETTING UP')
check('Stomach get-up selected and completes',prone and all(b(r)['animation']=='A_GetUp_Stomach' for r in prone) and b(front[-1])['get_ups']==1)
slow=[r for r in front if r['global_dilation']<.5 and b(r)['state']=='GETTING UP']
ratio=(b(slow[-1])['state_seconds']-b(slow[0])['state_seconds'])/(slow[-1]['t']-slow[0]['t'])
check('Get-up clock follows quarter-speed world',abs(ratio-.25)<.015,dict(recovery_seconds_per_manager_second=ratio))
check('Retained relative player slowdown remains .65',all(abs(r['global_dilation']*r['player_dilation']-.65)<.001 for r in slow))

blocked,events=read('Candidate04-BlockedAndAnchors')
wait=[r for r in blocked if 3<r['t']<6.9]
check('Physical overhead blocker keeps the body down',wait and all(b(r)['state']=='DOWN' and not b(r)['recovery_clear'] and b(r)['enabled_drives']==0 for r in wait))
check('Recovery retries after clearance returns',b(blocked[-1])['get_ups']==1 and b(blocked[-1])['state']=='STANDING')
joint_audit=json.loads((OUT/'joint-acceptance01.json').read_text())
check('All 21 position-locked joints remain connected',joint_audit['passed'],dict(
    max_locked_gap_cm=max(c['max_locked_gap_cm'] for c in joint_audit['cases']),
    evidence='joint-acceptance01.json; two free calf/pelvis constraints are correctly excluded from a positional-lock check. self-checks01 and raw measurements remain preserved.'))

unsupported,events=read('Candidate03-Unsupported')
removed=next(e['t'] for e in events if e['key']=='remove_actual_floor')
air=[r for r in unsupported if removed+.1<r['t']<8.9]
check('Removing real floor during get-up releases every drive',air and all(b(r)['state']=='FALLING' and b(r)['enabled_drives']==0 and not b(r)['recovery_floor'] for r in air))
check('Unsupported recovery never snaps upright',air[-1]['dummy']['bodies']['pelvis']['position'][2]<air[0]['dummy']['bodies']['pelvis']['position'][2]-100 and all(b(r)['get_ups']==0 for r in air))
check('F6 also restores the unsupported fixture',b(unsupported[-1])['state']=='STANDING' and b(unsupported[-1])['usable_feet']==2 and unsupported[-1]['rifle']['magazine']==30)

overview,_=read('Candidate04-SixRendered')
check('Six retained profiles, no legacy enemy',all(r['counts']==dict(dummy=6,legacy=0,manager=1,controller=1) and sorted(d['profile'] for d in r['fixtures'])==[1,2,3,4,5,6] for r in overview))

all_cases=[core,leg,front,blocked,unsupported]
check('All recorded falling/down states have zero enabled drives',all(b(r)['enabled_drives']==0 for rows in all_cases for r in rows if b(r)['state'] in ['FALLING','DOWN']))
check('All physical mannequin bodies stay simulated',all(v['simulating'] for rows in all_cases for r in rows for v in r['dummy']['bodies'].values()))
boundaries=[]
for rows in all_cases:
    for before,after in zip(rows,rows[1:]):
        if b(before)['state']!=b(after)['state'] and before['dummy']['epoch']==after['dummy']['epoch']:
            step=max(math.dist(v['position'],before['dummy']['bodies'][bone]['position']) for bone,v in after['dummy']['bodies'].items())
            boundaries.append(dict(t=after['t'],state=b(after)['state'],step_cm=step,dt=after['world_time']-before['world_time']))
check('Ordinary transitions do not teleport the bodies',max(x['step_cm'] for x in boundaries)<15,dict(max_body_step_cm=max(x['step_cm'] for x in boundaries)))

clips=['Candidate03-Core','Candidate03-LegInterruptedDeath','Candidate03-FrontSlow','Candidate04-BlockedAndAnchors','Candidate04-UnsupportedView','Candidate04-SixRendered']
for name in clips:
    data=json.loads((OUT/'Video'/(name+'.capture.json')).read_text())
    times=[r['t'] for r in data['frames']]
    check(name+' continuous WGC capture',len(times)>60 and all(x<y for x,y in zip(times,times[1:])),dict(frames=len(times),wall_seconds=times[-1],max_frame_gap_seconds=max(y-x for x,y in zip(times,times[1:]))))

manifest=json.loads((OUT/'Candidate05/manifest.json').read_text())
native=[r for r in manifest if r['path'].startswith(('Source/','Content/','Binaries/'))]
check('Final native and asset bytes match Candidate05',all(hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in native))
result=dict(task='MSQ-87',candidate='Candidate05',scope='Executor focused self-checks; independent review and owner feel acceptance pending',
    evidence_reuse='Candidate03 behavior and Candidate04 visuals apply: subsequent native changes only add joint diagnostics in GetDummyState. Candidate05-JointAnchors confirms the corrected metric through one full get-up. No behavior, physics settings or assets changed.',
    checks=checks,passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks),transition_boundaries=boundaries)
path=OUT/'self-checks02.json';assert not path.exists()
path.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:result[k] for k in ['candidate','passed','failed']}))
for row in checks:
    if not row['passed']:print(json.dumps(row))
