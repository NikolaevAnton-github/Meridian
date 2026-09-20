"""Focused acceptance against actual motion/skin, never the generated targets alone."""
import json
import math
import sys
from pathlib import Path
from inspect91 import geometry, sub, norm

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/CombatSlice01/PhysicsControlLegPose01/Worker'
NAMES=[('Candidate06-' if s in ['Lateral','TurnedLateral','Corrective'] else 'Candidate05-')+s
       for s in ['Rear','Side','Lateral','RepeatedReset','TurnedLateral','Corrective','Infeasible','ResetDuring']]
checks=[];cases=[];joints={};episodes=[];all_skins=[]
def check(name,passed,value=None):checks.append(dict(name=name,passed=bool(passed),value=value))
def distance2(a,b):return math.dist(a[:2],b[:2])

for name in NAMES:
    data=json.loads((OUT/(name+'.json')).read_text());rows=data['rows']
    check(name+': recorder completed',not data['error'] and rows[-1]['t']>=data['config']['duration'],data['error'])
    stepping=[r for r in rows if r['dummy']['balance']['state']=='STEPPING']
    standing=[r for r in rows if r['dummy']['balance']['state']=='STANDING' and r['dummy']['balance']['instability']==0]
    post=[r for r in standing if r['dummy']['step']['completed']>0]
    check(name+': stepping observed',bool(stepping))
    check(name+': complete neutral and step skeleton',all(r['dummy']['step']['neutral_bones']==89 for r in rows) and all(r['dummy']['step']['full_pose_bones']==89 for r in stepping))
    check(name+': two-step episode budget',max(r['dummy']['step']['episode_steps'] for r in rows)<=2)
    drift=max(r['dummy']['step']['peak_support_drift_cm'] for r in stepping)
    check(name+': support planted within 2 cm',drift<=2,drift)
    target_changes=[];targets={}
    for r in stepping:
        s=r['dummy']['step'];key=(r['dummy']['epoch'],s['started'])
        if key in targets:target_changes.append(math.dist(targets[key],s['plant_target']))
        targets[key]=s['plant_target']
    check(name+': planted target does not slide',max(target_changes,default=0)<1e-6,max(target_changes,default=0))
    geoms=[geometry(r['leg_bones']) for r in stepping]
    yaw=max(g[side]['knee_to_toe'] for g in geoms for side in ['l','r'])
    flex=[g[side]['flex'] for g in geoms for side in ['l','r']]
    check(name+': no knee reversal during step',yaw<45,yaw)
    check(name+': bounded actual knee flexion',min(flex)>8 and max(flex)<95,[min(flex),max(flex)])
    lengths=[g[side]['lengths'] for g in geoms for side in ['l','r']]
    check(name+': segment reach retained',all(abs(a-43.4)<1.0 and abs(b-42.3)<1.0 for a,b in lengths),
          [min(x[0] for x in lengths),max(x[0] for x in lengths),min(x[1] for x in lengths),max(x[1] for x in lengths)])
    # Limit values must be fixed throughout stepping, including the second step.
    limits={}
    for r in stepping:
        for j in r['dummy']['step']['leg_joints']:
            key=j['child']+'/'+j['parent'];limits.setdefault(key,set()).add(tuple(j['effective_degrees']))
            if name.startswith(('Candidate05','Candidate06')):
                a=joints.setdefault(key,dict(authored=j['authored_degrees'],effective=j['effective_degrees'],motion=j['motion_swing1_swing2_twist'],min=[1e9]*3,max=[-1e9]*3))
                a['min']=[min(x,y) for x,y in zip(a['min'],j['observed_degrees'])]
                a['max']=[max(x,y) for x,y in zip(a['max'],j['observed_degrees'])]
    check(name+': no target-dependent joint widening',all(len(v)==1 for v in limits.values()))
    check(name+': targets remain within fixed angular envelope',max(r['dummy']['step']['joint_limit_error_degrees'] for r in stepping)<=3)
    soles=[r['dummy']['balance'][key]-r['dummy']['balance']['ground_z'] for r in standing for key in ['sole_left_z','sole_right_z']]
    check(name+': settled sole contact 0 to 1 cm',min(soles)>=0 and max(soles)<=1,[min(soles),max(soles)])
    if post:
        pg=[geometry(r['leg_bones']) for r in post]
        yaw_post=max(g[s]['knee_to_toe'] for g in pg for s in ['l','r'])
        flex_post=[g[s]['flex'] for g in pg for s in ['l','r']]
        check(name+': settled knee/foot alignment',yaw_post<25,yaw_post)
        check(name+': credible standing knee range',min(flex_post)>8 and max(flex_post)<45,[min(flex_post),max(flex_post)])
        check(name+': bounded settled pelvis height',max(abs(r['dummy']['step']['stance_pelvis'][2]-rows[0]['dummy']['step']['stance_pelvis'][2]) for r in post)<=4)
        check(name+': unfinished stance never labelled standing',all(not r['dummy']['step']['stance_correction_pending'] for r in post))
        initial_sep=sub(rows[0]['leg_bones']['foot_l']['p'],rows[0]['leg_bones']['foot_r']['p']);initial_sep[2]=0
        width=norm(initial_sep);across=[x/width for x in initial_sep]
        widths=[sum(x*y for x,y in zip(sub(r['leg_bones']['foot_l']['p'],r['leg_bones']['foot_r']['p']),across)) for r in post]
        check(name+': settled stance width bounded',min(widths)>width*.55-.5 and max(widths)<width+16.5,[min(widths),max(widths)])
    check(name+': other five fixtures preserved',all(len(r['fixtures'])==6 and all(d['health']==100 and d['hits']==0 and d['deaths']==0 for d in r['fixtures'] if d['profile']!=1) for r in rows))
    for f in OUT.glob(name+'-pose-*.json'):
        d=json.loads(f.read_text());ground=d['runtime']['balance']['ground_z']
        gaps={s:min(v['world'][2] for v in d['skin']['foot_vertices'] if v['bone'].endswith('_'+s))-ground for s in ['l','r']}
        check(f.stem+': CPU-skinned sole contact',all(0<=x<=1 for x in gaps.values()),gaps)
        all_skins.append(dict(file=f.name,vertices=len(d['skin']['foot_vertices']),gaps=gaps))
    # Report one actual late standing pose per completed step, before the next hit/reset.
    by_step={}
    for r in post:by_step[(r['dummy']['epoch'],r['dummy']['step']['completed'])]=r
    for key,r in by_step.items():
        episodes.append(dict(case=name,epoch=key[0],completed=key[1],t=r['t'],geometry=geometry(r['leg_bones']),
            stance_pelvis=r['dummy']['step']['stance_pelvis'],foot_separation_cm=distance2(r['leg_bones']['foot_l']['p'],r['leg_bones']['foot_r']['p'])))
    if name.endswith('RepeatedReset'):
        check(name+': four completed episodes',max(r['dummy']['step']['completed'] for r in rows)==4)
        paired=[r for r in post if r['dummy']['step']['completed'] in [2,4]]
        check(name+': no accumulated crouch',max(abs(r['leg_bones']['pelvis']['p'][2]-rows[0]['leg_bones']['pelvis']['p'][2]) for r in paired)<1)
    if name.endswith(('RepeatedReset','ResetDuring')):
        d=rows[-1]['dummy'];s=d['step']
        check(name+': F6 clears new and retained state',d['epoch']>rows[0]['dummy']['epoch'] and all(s[k]==0 for k in ['started','completed','episode_steps','height_correction_cm','joint_limit_error_degrees','full_pose_bones']) and not s['stance_correction_pending'] and not s['corrective'] and s['neutral_bones']==89)
        check(name+': F6 restores calibrated geometry',max(math.dist(rows[0]['leg_bones'][bone]['p'],rows[-1]['leg_bones'][bone]['p']) for bone in rows[0]['leg_bones'])<1)
    if name.endswith('Corrective'):
        check(name+': exactly two steps for one disturbance',sum(e.get('key')=='@push' for e in data['events'])==1 and rows[-1]['dummy']['step']['completed']==2)
        check(name+': corrective step observed',any(r['dummy']['step']['corrective'] for r in stepping))
        check(name+': corrective finishes standing',rows[-1]['dummy']['balance']['state']=='STANDING' and not rows[-1]['dummy']['step']['stance_correction_pending'])
    if name.endswith('Infeasible'):
        fallen=[r for r in rows if r['dummy']['balance']['state'] in ['FALLING','DOWN']]
        check(name+': infeasible geometry releases all drives',bool(fallen) and all(r['dummy']['balance']['enabled_drives']==0 for r in fallen))
        check(name+': rejected geometry physically collapses',bool(fallen) and min(r['leg_bones']['pelvis']['p'][2]-r['dummy']['balance']['ground_z'] for r in fallen)<30)
        check(name+': living full snapshot get-up retained',rows[-1]['dummy']['balance']['state']=='STANDING' and rows[-1]['dummy']['balance']['get_ups']>=1 and max(r['dummy']['balance']['snapshot_bones'] for r in rows)==89)
    else:
        check(name+': no unintended collapse',all(r['dummy']['balance']['falls']==0 for r in rows))
    capture=json.loads((OUT/'Video'/(name+'.capture.json')).read_text());frames=capture['frames']
    gaps=[b['t']-a['t'] for a,b in zip(frames,frames[1:])]
    check(name+': continuous ordinary-time capture',len(frames)>20 and frames[-1]['t']>=data['config']['duration']+1.5)
    cases.append(dict(name=name,samples=len(rows),video_frames=len(frames),capture_fps=(len(frames)-1)/(frames[-1]['t']-frames[0]['t']),max_capture_gap=max(gaps),support_drift_cm=drift,knee_to_toe_max=yaw,knee_flex_range=[min(flex),max(flex)]))

result=dict(checks=checks,passed=sum(c['passed'] for c in checks),failed=[c for c in checks if not c['passed']],cases=cases,joints=joints,episodes=episodes,skin_audits=all_skins)
dest=OUT/sys.argv[1];assert not dest.exists();dest.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(dict(passed=result['passed'],failed=result['failed'],samples=sum(c['samples'] for c in cases)),indent=2))
sys.exit(bool(result['failed']))
