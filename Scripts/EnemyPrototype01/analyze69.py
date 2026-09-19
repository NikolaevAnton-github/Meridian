"""Evaluate focused observed gameplay contracts; preserve raw rows and failed runs."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/EnemyPrototype01/Worker'
checks, metrics = {}, {}

def check(name, result): checks[name] = bool(result)
def read(name): return json.loads((OUT / (name + '.json')).read_text())
def length(v): return math.sqrt(sum(n*n for n in v))
def distance(a,b): return length([x-y for x,y in zip(a,b)])
def at(rows,time): return min(rows,key=lambda r:abs(r['t']-time))

for label in ['IdleHitDeathReset','MovingHits','HoldFirePresentation','ActiveRagdollReset']:
    name = ('Candidate07-' if label=='ActiveRagdollReset' else 'Candidate06-') + label
    result = read(name)
    rows = result['rows']
    check(label + '.completed', not result['error'] and rows[-1]['t'] >= result['config']['duration'])
    check(label + '.starts_fresh', rows[0]['rifle']['magazine'] == 30 and rows[0]['enemy']['health'] == 100)
    check(label + '.no_overload', rows[-1]['ballistics']['overload_frames'] == 0)
    check(label + '.no_geometry_barrier', rows[-1]['ballistics']['geometry_barriers'] == 0)
    check(label + '.finite_bones', all(math.isfinite(n) for r in rows for v in r['enemy']['bones'].values() for n in v))
    check(label + '.bounded_pose', all(distance(v,r['enemy']['pelvis']) < 160 for r in rows for v in r['enemy']['bones'].values()))
    metrics[label] = dict(rows=len(rows), world_seconds=rows[-1]['t'], min_health=min(r['enemy']['health'] for r in rows),
        final_ammunition=rows[-1]['rifle']['magazine'], max_speed=max(length(r['enemy']['velocity']) for r in rows))
    if label == 'IdleHitDeathReset':
        check(label+'.idle_hit', at(rows,2.5)['enemy']['health']==75 and at(rows,2.5)['enemy']['hits']==1)
        check(label+'.hit_animation', any('Template_Hit' in r['enemy']['animation'] for r in rows if 2<r['t']<3))
        dead=[r for r in rows if 6.3<r['t']<12.8]
        check(label+'.one_death_four_hits', dead and all(r['enemy']['health']==0 and r['enemy']['hits']==4 and r['enemy']['deaths']==1 for r in dead))
        check(label+'.corpse_not_damageable', all(not r['enemy']['spheres'] for r in dead))
        check(label+'.no_floor_escape', min(r['enemy']['pelvis'][2] for r in dead)>0 and max(r['enemy']['pelvis'][2] for r in dead)<150)
        settled=[r for r in rows if 12<r['t']<12.8]
        drift=max(distance(r['enemy']['pelvis'],settled[0]['enemy']['pelvis']) for r in settled)
        check(label+'.settled', drift<1 and not settled[-1]['enemy']['awake'])
        check(label+'.reset', rows[-1]['enemy']['health']==100 and rows[-1]['enemy']['hits']==0 and not rows[-1]['enemy']['dead'])
        check(label+'.finite_ammo_no_reset_refill', rows[-1]['rifle']['magazine']==25)
        metrics[label].update(pelvis_settled_drift_cm=drift, last_dead_pelvis=settled[-1]['enemy']['pelvis'])
    elif label == 'MovingHits':
        travel=max(r['enemy']['location'][1] for r in rows)-min(r['enemy']['location'][1] for r in rows)
        check(label+'.F7_motion', travel>100 and any(r['enemy']['moving'] for r in rows))
        check(label+'.two_hits', at(rows,6)['enemy']['hits']==2 and at(rows,6)['enemy']['health']==50)
        check(label+'.movement_resumes_after_hit', any(length(r['enemy']['velocity'])>50 for r in rows if 3.1<r['t']<4))
        check(label+'.reset_stops_preview', not rows[-1]['enemy']['moving'] and rows[-1]['enemy']['health']==100)
        metrics[label]['lateral_span_cm']=travel
    elif label == 'HoldFirePresentation':
        check(label+'.fire_pose_then_idle', any('Template_Fire' in r['enemy']['animation'] for r in rows) and 'Template_Idle' in rows[-1]['enemy']['animation'])
        check(label+'.no_enemy_projectiles_or_player_ammo', rows[-1]['ballistics']['launched']==0 and rows[-1]['rifle']['magazine']==30)
    else:
        check(label+'.first_active_death', at(rows,2.5)['enemy']['dead'] and at(rows,2.5)['enemy']['awake'])
        check(label+'.reset_while_falling', at(rows,3)['enemy']['health']==100 and not at(rows,3)['enemy']['simulating'])
        second=[r for r in rows if 5<r['t']<11.8]
        check(label+'.second_death', all(r['enemy']['dead'] and r['enemy']['deaths']==1 and r['enemy']['hits']==4 for r in second))
        check(label+'.second_physics_bounded', all(0<r['enemy']['pelvis'][2]<150 for r in second))
        check(label+'.final_reset_and_ammo', rows[-1]['enemy']['health']==100 and rows[-1]['rifle']['magazine']==22)

probe=read('collision-probe-02')
probe.update(read('collision-probe-cover03'))
for key,value in probe.items():
    if isinstance(value,bool): check('collision.'+key,value)
    elif key=='regions':
        for region in value:
            for kind in ['aim_query','finite_flight_damage','region_matches']:
                check('collision.'+region['region']+'.'+kind, region[kind])
summary=dict(checks=checks, passed=sum(checks.values()), failed=[k for k,v in checks.items() if not v], metrics=metrics,
    evidence_reuse='Candidate06 native gameplay is reused; Candidate07 changes reset velocity clearing only. Probe02 adds thin-cover precedence and checks the final saved art subset.')
path=OUT/'verification-summary01.json'
assert not path.exists()
path.write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps({k:summary[k] for k in ['passed','failed','metrics']}))
assert all(checks.values()), summary['failed']
