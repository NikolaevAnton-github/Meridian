"""Focused acceptance over real input, collision, ammo and evaluated-pose evidence."""
import json
import math
import statistics
from pathlib import Path

OUT=Path(__file__).resolve().parents[2]/'Saved/PurchasedArms05/Worker'
CASES=['Focus02-ShiftLanding','Final01-ExtendedShift','Final01-OrdinaryHip',
       'Final02-OrdinaryAuto','Final01-OrdinaryADS','Final01-AltBoundary',
       'Final01-BusyOwnership','AimOnly01-OrdinaryThenShift',
       'Correction01-ShiftHeldHip','Correction01-ShiftReleasedADS',
       'Correction01-ShiftHeldADS','Correction01-ShiftAimOnly']


def distance(a,b): return math.dist(a,b)
def speed(r): return math.hypot(*r['velocity'][:2])
def inspect(name):
    data=json.loads((OUT/(name+'.json')).read_text())
    assert data['error'] is None, data['error']
    rows=data['rows']
    scope='Focused numerical checks; visual review is recorded separately.'
    if name=='AimOnly01-OrdinaryThenShift':
        # The initial fast-jump landing recovery was corrected later. Retain only
        # the unchanged ordinary ADS-only portion as acceptance evidence here.
        rows=[r for r in rows if r['t']<2.65]
        data['events']=[e for e in data['events'] if e['t']<2.65]
        scope='Ordinary ADS-only portion; Shift recovery superseded by Correction01-ShiftAimOnly.'
    assert {r['fast_input_bindings'] for r in rows}=={4}
    jumps=[]
    for a,b in zip(rows,rows[1:]):
        if b['jump_starts']==a['jump_starts']: continue
        flight=[r for r in rows if r['jump_starts']==b['jump_starts'] and r['falling']]
        land=next(r for r in rows if r['t']>b['t'] and r['landings']>a['landings'])
        assert flight and all(r['jump_phase']<=.30001 for r in flight), name
        assert all(not r['running'] and not r['sprinting'] for r in flight), name
        fast=b['jump_z_velocity']==352
        expected=540 if fast else 360
        assert all(abs(speed(r)-expected)<.02 for r in flight), (name,expected)
        assert land['jump_z_velocity']==320 and not land['jump_pending_landing']
        jumps.append(dict(number=b['jump_starts'],first_airborne_t=b['t'],collision_t=land['t'],
            actual_landing_world_time=land['last_landing_time'],takeoff_setting=b['jump_z_velocity'],
            apex_rise=max(r['location'][2] for r in flight)-a['location'][2],
            sampled_travel=distance(land['location'][:2],a['location'][:2]),
            flight_seconds=land['t']-b['t'],speed_range=[min(map(speed,flight)),max(map(speed,flight))],
            max_airborne_jump_phase=max(r['jump_phase'] for r in flight)))
    requests=[]
    for e in data['events']:
        if 'after_air_frame' not in e: continue
        assert e['after_air_frame'] in [0,1] and e['falling'] and e['vertical_velocity']>250
        following=[r for r in rows if r['t']>e['t']]
        if e['key']=='LeftMouseButton':
            response=next(r for r in following if r['ammo']<e['ammo_before'])
        else:
            response=next(r for r in following if r['aim_requested'])
        latency=response['t']-e['t']
        assert latency<.05, (name,e,latency)
        requests.append(dict(key=e['key'],air_frame=e['after_air_frame'],request_t=e['t'],
            response_t=response['t'],latency_ms=1000*latency,
            frame_delta=response['frame']-e['frame'],response_ammo=response['ammo'],
            response_falling=response['falling']))
    shots=[b for a,b in zip(rows,rows[1:]) if b['ammo']<a['ammo']]
    aim=[r for r in rows if r['aim_requested'] and 'aim_offset' in r]
    aim_result={}
    if aim:
        for jump in jumps:
            air_aim=[r for r in aim if jump['first_airborne_t']<=r['t']<jump['collision_t']]
            if air_aim:
                first,last=air_aim[0],air_aim[-1]
                aim_result[str(jump['number'])]=dict(first_current=first['aim_offset']['p'],
                    last_current=last['aim_offset']['p'],last_target=last['aim_target']['p'],
                    settled_translation_error=distance(last['aim_offset']['p'],last['aim_target']['p']),
                    actual_translation_change=distance(first['aim_offset']['p'],last['aim_offset']['p']))
                assert aim_result[str(jump['number'])]['actual_translation_change']>.1
    if name.startswith('Correction01-'):
        first=jumps[0]
        protected=[r for r in rows if r['jump_starts']==1 and r['t']>=first['first_airborne_t']
            and (r['falling'] or r['aim_requested'] or r['airborne_fire_held'])]
        assert protected and all(r['animation_jump_base'] for r in protected), name
    if 'Auto' in name or name in ['Correction01-ShiftHeldHip','Correction01-ShiftHeldADS','Correction01-ShiftReleasedADS']:
        assert len([r for r in shots if r['falling']])>=6, name
        assert len([r for r in shots if not r['falling']])>=4, name
        assert max(b['t']-a['t'] for a,b in zip(shots,shots[1:]))<.17, name
    if name=='Final01-AltBoundary':
        assert all(r['jump_starts']==0 for r in rows if r['t']<1.25)
        assert any(r['sprinting'] and speed(r)>719 for r in rows if r['t']<1.25)
        assert [j['takeoff_setting'] for j in jumps]==[320,352]
    if name=='Final01-BusyOwnership':
        assert len(jumps)==1 and not shots
        assert all(r['busy'] and 'Reload' in r['montage'] for r in rows if 1.3<r['t']<3.5)
    if name=='Correction01-ShiftReleasedADS':
        assert [j['takeoff_setting'] for j in jumps]==[352,320]
        assert not any(r['running'] or r['sprinting'] for r in rows if r['t']>jumps[0]['collision_t'])
    if name in ['Correction01-ShiftHeldHip','Correction01-ShiftHeldADS','Correction01-ShiftAimOnly']:
        assert any(r['running'] and not r['aim_requested'] and not r['airborne_fire_held']
                   and r['t']>jumps[0]['collision_t'] for r in rows), name
    return dict(scope=scope,samples=len(rows),jumps=jumps,requests=requests,shots=len(shots),
        airborne_shots=sum(r['falling'] for r in shots),
        shot_interval_median=statistics.median([b['t']-a['t'] for a,b in zip(shots,shots[1:])]) if len(shots)>1 else None,
        max_shot_gap=max((b['t']-a['t'] for a,b in zip(shots,shots[1:])),default=None),
        max_physics_props=max(len(r['physics']) for r in rows),aim_interpolation=aim_result,
        final={k:rows[-1][k] for k in ['falling','running','sprinting','busy','aim_requested','aim_blocked','airborne_fire_held','jump_starts','landings']})


if __name__=='__main__':
    result={name:inspect(name) for name in CASES}
    path=OUT/'focused-analysis-final.json'
    assert not path.exists()
    path.write_text(json.dumps(result,indent=2))
    print(json.dumps(dict(passed=True,cases=len(result),samples=sum(r['samples'] for r in result.values()),
        jumps=sum(len(r['jumps']) for r in result.values()),requests=sum(len(r['requests']) for r in result.values()))))
