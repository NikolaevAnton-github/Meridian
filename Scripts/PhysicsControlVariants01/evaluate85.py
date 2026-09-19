"""Evaluate only MSQ-85's changed behavior from the recorded native samples."""
import json
import math
import statistics
from pathlib import Path
from metrics85 import reactions, local, norm, sub, angle
OUT=Path(__file__).resolve().parents[2]/'Saved/CombatSlice01/PhysicsControlVariants01/Worker'
TIME_CANDIDATE='Candidate04-'

def load(name): return json.loads((OUT/(name+'.json')).read_text())
def rows(name):
    d=load(TIME_CANDIDATE+name)
    assert d['error'] is None
    return d['rows']
def checks_for_rows(rs):
    return dict(no_added_overload=rs[-1]['combat']['overload_frames']==rs[0]['combat']['overload_frames'],
        unique_scheduled_ids=len({s['id'] for s in rs[-1]['rifle']['recent_shots']})==len(rs[-1]['rifle']['recent_shots']),
        one_manager=all(s['counts']['manager']==1 for s in rs),
        no_legacy=all(s['counts']['legacy']==0 for s in rs),
        no_duplicate_fixtures=all(s['counts']['dummy'] in [0,6] for s in rs))

def reaction_summary():
    torso=[]
    for n in range(1,7):
        name='Candidate03-Torso'+str(n)
        chest=reactions(name,'spine_05')['contacts'][0]
        struck=reactions(name)['contacts'][0]
        rs=load(name)['rows']
        pre=[s for s in rs if .3<s['t']<.9]
        start=pre[0]['dummy']['bodies']
        drift=max(norm(sub(b['position'],start[k]['position'])) for s in pre for k,b in s['dummy']['bodies'].items())
        torso.append(dict(profile=n,chest_cm=chest['peak_local_cm'],chest_degrees=chest['peak_local_degrees'],
            struck_degrees=struck['peak_local_degrees'],impulse=chest['impulse'],
            late_chest_cm=chest['late_local_cm'],late_max_speed=chest['late_max_speed'],
            joint_gap=max(s['dummy'].get('max_joint_anchor_gap_cm',0) for s in rs),idle_drift_cm=drift,
            profile_settings={k:rs[0]['dummy'][k] for k in ['impulse_cap','velocity_cap','hit_strength','hit_hold','hit_recovery']},
            checks={**checks_for_rows(rs),'single_torso_contact':chest['contact_bone']=='spine_03' and rs[-1]['dummy']['physical_hits']==1,
                    'independent_health':sorted(x['health'] for x in rs[-1]['fixtures'])==[75,100,100,100,100,100],
                    'finite_recovery':chest['late_local_cm']<2 and chest['late_max_speed']<12 and chest['late_recovering']==0,
                    'stable_idle':drift<1,'joints_bounded':max(s['dummy'].get('max_joint_anchor_gap_cm',0) for s in rs)<3}))
    ordering=[dict(pair=[a['profile'],b['profile']],ratio=b['chest_cm']/a['chest_cm'],gain_cm=b['chest_cm']-a['chest_cm'],
        passed=b['chest_cm']>=a['chest_cm']*1.15 and b['chest_cm']>=a['chest_cm']+1) for a,b in zip(torso,torso[1:])]
    return dict(torso=torso,ordering=ordering,low_profile_pass=torso[0]['chest_cm']>=3 and torso[0]['struck_degrees']>=6)

def clocks():
    movement={}
    for mode in ['Normal','Slow']:
        rs=rows('Movement'+mode)
        steady=[s for s in rs if 1.4<s['t']<2.4]
        a,b=steady[0],steady[-1]
        movement[mode]=dict(wall_speed=norm(sub(b['player_location'],a['player_location']))/(b['wall']-a['wall']),
            manager_speed=norm(sub(b['player_location'],a['player_location']))/(b['t']-a['t']),
            simulation_speed=statistics.median(norm(s['player_velocity']) for s in steady),
            world_to_wall=(b['world_time']-a['world_time'])/(b['wall']-a['wall']),
            checks=checks_for_rows(rs))
    ratio=movement['Slow']['wall_speed']/movement['Normal']['wall_speed']
    movement['ratio']=ratio; movement['pass']=abs(ratio/.65-1)<.03
    cadence={}
    for name in ['CadenceTransitions','LowFPSSlow']:
        rs=rows(name); shots=rs[-1]['rifle']['recent_shots']; spacings=[]
        for a,b in zip(shots,shots[1:]):
            candidates=[s for s in rs if a['time']<=s['combat']['firing_clock']<=b['time']]
            rates={s['combat']['player_action_rate'] for s in candidates}
            spacings.append(dict(action=b['action_time']-a['action_time'],manager=b['time']-a['time'],rates=sorted(rates)))
        counts=[s['rifle']['shots'] for s in rs]
        wall_events=[dict(t=s['t'],wall=s['wall'],new=count-prev) for s,count,prev in zip(rs[1:],counts[1:],counts[:-1]) if count>prev]
        cadence[name]=dict(shots=len(shots),spacings=spacings,delivery_wall_events=wall_events,
            delivered_manager_frame_max=max(s['combat']['frame_delta'] for s in rs),
            checks={**checks_for_rows(rs),'action_spacing':all(abs(s['action']-.085)<1e-5 for s in spacings),
                'saved_ammo':rs[-1]['rifle']['magazine']==30-len(shots),
                'manager_spacing':all(len(s['rates'])!=1 or abs(s['manager']-.085/s['rates'][0])<1e-5 for s in spacings)})
    bullets={}
    for mode in ['Normal','Slow']:
        rs=rows('Bullet'+mode); sampled=[]
        for a,b in zip(rs,rs[1:]):
            old={x['id']:x for x in a['combat']['bullets']}
            for x in b['combat']['bullets']:
                if x['id'] in old and b['t']>a['t']:
                    sampled.append(norm(sub(x['position'],old[x['id']]['position']))/(b['t']-a['t']))
        bullets[mode]=dict(manager_speed_median=statistics.median(sampled),samples=len(sampled),checks=checks_for_rows(rs))
    bullets['ratio']=bullets['Slow']['manager_speed_median']/bullets['Normal']['manager_speed_median']
    bullets['pass']=abs(bullets['ratio']/.25-1)<.03
    return dict(movement=movement,cadence=cadence,bullets=bullets)

if __name__=='__main__':
    import sys
    result=reaction_summary() if sys.argv[1]=='reactions' else clocks()
    name=OUT/(sys.argv[2]+'.json')
    assert not name.exists()
    name.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
