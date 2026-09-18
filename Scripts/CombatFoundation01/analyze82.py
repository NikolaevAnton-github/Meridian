"""Independent timestamp/flight oracle; never collapse multi-shot frames."""
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/CombatTiming01/Worker'
checks = []

def check(name, passed, detail=None):
    checks.append(dict(name=name, passed=bool(passed), detail=detail))

def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))

def lattice(start, end, interval=.085):
    # Independent closed-form enumeration with a half-open ending boundary.
    count = max(0, math.ceil((end - start) / interval - 1e-8))
    return [start + i * interval for i in range(count)]

def stamps(name, result, expected):
    shots = result['rifle']['recent_shots']
    actual = [s['time'] for s in shots]
    check(name + ':timestamps', len(actual) == len(expected) and
          all(abs(a-b) <= 1e-6 for a,b in zip(actual, expected)), dict(expected=expected, actual=actual))
    check(name + ':unique', len(set(s['id'] for s in shots)) == len(shots))

def controlled(prefix):
    names = [f'Cadence{fps}' for fps in [10,30,60,120,144]] + ['Hitch150','Hitch250','Jitter']
    for name in names:
        result = read(f'controlled-{prefix}{name}.json')
        stamps(name, result, lattice(0, 2))
        check(name + ':ammo', result['rifle']['magazine'] == 6)
        check(name + ':work', all(f['steps'] <= 32 and f['attempts'] <= 6 for f in result['frames']) and
              result['world']['overload_frames'] == 0 and result['world']['geometry_barriers'] == 0)
        # Compare each equal-clock prefix, including the final endpoint.
        check(name + ':frame_prefixes', all(f['shots'] == len(lattice(0, f['time'])) for f in result['frames']))
    result = read(f'controlled-{prefix}Cadence10.json')
    check('10fps:multiple_due', max(f['attempts'] for f in result['frames']) >= 2)
    result = read(f'controlled-{prefix}Clamp50.json')
    stamps('Clamp50', result, lattice(0, 1, .05))
    check('Clamp50:budget', max(f['steps'] for f in result['frames']) <= 32 and max(f['attempts'] for f in result['frames']) <= 6)
    expected = {
        'Extreme':[0,.085,2.55,2.635],
        'ReleaseRepress':lattice(0,.25)+lattice(.5,1),
        'Capacity':[0], 'Empty':[0,.085], 'Mode':[0,.085,.17,.3,.5],
        'Reset':lattice(0,.25)+lattice(.75,1),
        'ReloadCancel':[0,.085,.17,.75,.835],
        'ActionLock':lattice(0,.25)+lattice(.75,1.25),
        'Resume':[0,.085,.17],
    }
    for name, times in expected.items():
        result = read(f'controlled-{prefix}{name}.json')
        stamps(name, result, times)
        check(name + ':caps', all(f['steps'] <= 32 and f['attempts'] <= 6 for f in result['frames']))
    result = read(f'controlled-{prefix}Extreme.json')
    check('Extreme:drop_no_debt', result['world']['overload_frames'] == 1 and result['world']['dropped_time'] == 2 and
          result['frames'][1]['steps'] == 0 and all(f['shots'] == 2 for f in result['frames'][1:5]))
    result = read(f'controlled-{prefix}Capacity.json')
    check('Capacity:conservation', result['rifle']['magazine'] == 29 and result['world']['active'] == 1)
    result = read(f'controlled-{prefix}Empty.json')
    check('Empty:no_ammo_created', result['rifle']['magazine'] == result['rifle']['reserve'] == 0)
    result = read('controlled-Isolated01-ReloadCommit.json')
    stamps('ReloadCommit-isolated', result, lattice(0,.25)+lattice(.75,1.5))
    check('ReloadCommit:once_and_conserved', result['rifle']['transfers'] == 1 and result['rifle']['transferred_rounds'] == 10 and
          result['rifle']['magazine'] == 3 and result['rifle']['reserve'] == 0)
    result = read(f'controlled-{prefix}ReloadCancel.json')
    check('ReloadCancel:no_transfer', result['rifle']['transfers'] == 0 and result['rifle']['reserve'] == 10 and result['rifle']['magazine'] == 0)
    result = read(f'controlled-{prefix}Resume.json')
    check('Resume:only_unfrozen_age', len(result['world']['bullets']) == 3 and all(abs(b['age']-.25)<1e-6 for b in result['world']['bullets']))
    for scale in [1,.25,0]:
        for kind in ['Birth', 'MoveTurn']:
            long = read(f'controlled-{prefix}{kind}{scale}-Long.json')
            fine = read(f'controlled-{prefix}{kind}{scale}-Fine.json')
            stamps(f'{kind}{scale}', long, [0,.085,.17])
            left = sorted(long['world']['bullets'],key=lambda b:b['birth_time'])
            right = sorted(fine['world']['bullets'],key=lambda b:b['birth_time'])
            check(f'{kind}{scale}:count', len(left) == len(right) == 3)
            for i,(a,b) in enumerate(zip(left,right)):
                expected_age = (.25 - i*.085)*scale
                check(f'{kind}{scale}:age{i}', abs(a['age']-expected_age)<=1e-6)
                check(f'{kind}{scale}:distance{i}', abs(a['travel']-expected_age*1000)<=.01)
                check(f'{kind}{scale}:fine_comparison{i}', math.dist(a['position'],b['position'])<=.02 and abs(a['age']-b['age'])<=1e-6)
                shot = long['rifle']['recent_shots'][i]
                t=i*.085
                yaw=math.radians(180*t if kind=='MoveTurn' else 0)
                vx=100*t if kind=='MoveTurn' else 0
                vy=8000+(70*t if kind=='MoveTurn' else 0)
                expected_birth=[vx+55*math.cos(yaw)-12*math.sin(yaw),vy+55*math.sin(yaw)+12*math.cos(yaw),11992]
                check(f'{kind}{scale}:birth_pose{i}', math.dist(shot['position'],expected_birth)<=.001)
                expected_position=[s+v*expected_age for s,v in zip(shot['position'],shot['velocity'])]
                check(f'{kind}{scale}:residual_flight{i}', math.dist(a['position'],expected_position)<=.01)
    previous_hits = read(f'controlled-{prefix}MoveTurn0-Fine.json')['world']['hits']
    for distance in [25,300]:
        long = read(f'controlled-{prefix}Cover{distance}-Long.json')
        fine = read(f'controlled-{prefix}Cover{distance}-Fine.json')
        check(f'Cover{distance}:consumed', long['world']['active'] == fine['world']['active'] == 0 and long['rifle']['shots'] == fine['rifle']['shots'] == 3)
        check(f'Cover{distance}:birth_side', all(s['position'][0] < distance-.6 for s in long['rifle']['recent_shots']))
        for label, data in [('Long', long), ('Fine', fine)]:
            check(f'Cover{distance}:{label}:three_contacts', data['world']['hits']-previous_hits==3,
                  dict(previous=previous_hits, current=data['world']['hits']))
            previous_hits=data['world']['hits']
    result=read(f'controlled-{prefix}FrozenSelf.json')
    check('FrozenSelf:old_and_three_new_hit_once', result['new_self_hits'] == 4 and result['world']['active'] == 0 and result['rifle']['shots'] == 3)
    check('FrozenSelf:attribution', result['world']['last_hit_shooter'].endswith('BP_TFA_BaseCharacter_C_0'))
    for kind in ['contracts','ballistics','corrections']:
        filename = f'controlled-{prefix}Contracts.json' if kind=='contracts' else f'{kind}-{prefix.rstrip("-")}.json'
        result=read(filename)
        for key,value in result.items():
            if isinstance(value,bool): check(f'{kind}:{key}',value)

def actual(prefix):
    summaries=[]
    for path in sorted(OUT.glob(prefix+'*.json')):
        data=read(path.name)
        if 'rows' not in data: continue
        name=path.stem
        rows=[]
        for row in data['rows']:
            if not rows or row['ballistics']['firing_clock'] != rows[-1]['ballistics']['firing_clock']: rows.append(row)
        if not rows: continue
        last=rows[-1]
        check(name+':transport',data['error'] is None)
        check(name+':work',all(r['ballistics']['frame_steps']<=32 and r['rifle']['frame_shots']<=6 for r in rows))
        shots=last['rifle']['recent_shots']
        supplied=[e[2][0] for e in data['config']['events'] if e[1]=='@ammo']
        initial_ammo=supplied[-1] if supplied else 30
        check(name+':unique_and_ammo',len({s['id'] for s in shots}) == last['rifle']['shots'] and
              last['rifle']['magazine']+last['rifle']['shots'] == initial_ammo+last['rifle']['transferred_rounds'])
        check(name+':presentation_bounded',last['rifle']['presentations']<=last['rifle']['shots'] and all(r['rifle']['effects']<=64 and r['rifle']['props']<=64 for r in rows))
        deltas=[r['ballistics']['frame_delta'] for r in rows]
        measured=[r['capture_wall_monotonic']-p['capture_wall_monotonic'] for p,r in zip(rows,rows[1:])
                  if r['capture_wall_monotonic']>p['capture_wall_monotonic']]
        summary=dict(case=name,requested_fps=data['config']['fps'],
                     observed_world_samples_per_wall_second=(len(rows)-1)/(rows[-1]['capture_wall_monotonic']-rows[0]['capture_wall_monotonic']),
                     world_delta_min=min(deltas),world_delta_max=max(deltas),world_delta_median=statistics.median(deltas),
                     distinct_frames=len(rows),shots=last['rifle']['shots'],max_frame_shots=last['rifle']['max_frame_shots'],
                     presentations=last['rifle']['presentations'],overloads=last['ballistics']['overload_frames'],
                     geometry_barriers=last['ballistics']['geometry_barriers'])
        if 'Cadence' in name or 'Hitch' in name:
            # Input reports in the first post-frame sample. Its observed firing
            # interval starts at that frame's left clock boundary, not at the
            # Slate injection event or at a rounded nominal recording time.
            pressed=next(i for i,r in enumerate(rows) if r['rifle']['fire_held'])
            released=next(i for i in range(pressed+1,len(rows)) if not rows[i]['rifle']['fire_held'])
            start=rows[pressed]['ballistics']['firing_clock']-rows[pressed]['ballistics']['frame_delta']
            end=rows[released]['ballistics']['firing_clock']-rows[released]['ballistics']['frame_delta']
            expected=lattice(start,end)
            actual_times=[s['time'] for s in shots]
            check(name+':clock_window',len(actual_times)==len(expected) and all(abs(a-b)<=1e-6 for a,b in zip(actual_times,expected)),
                  dict(start=start,end=end,expected=expected,actual=actual_times))
            check(name+':no_barrier',summary['overloads']==summary['geometry_barriers']==0)
            summary.update(window_start=start,window_end=end,expected_shots=len(expected))
        if 'HipADS' in name:
            check(name+':hip_and_aim_fire',any(r['rifle']['frame_shots']>0 and not r['aim_requested'] for r in rows) and
                  any(r['rifle']['frame_shots']>0 and r['aim_requested'] and abs(r['view_fov']-78)<.01 for r in rows))
            check(name+':reset_cleanup',last['ballistics']['active']==last['ballistics']['impacts']==last['rifle']['props']==last['rifle']['effects']==0)
        if 'Airborne' in name:
            check(name+':two_takeoffs_landings',last['jump_starts']==last['landings']==2)
            for begin,end in [(1.0,1.7),(3.5,4.3)]:
                flight=[r for r in rows if begin<=r['t']<=end and r['falling']]
                check(name+f':air_fire_{begin}',any(r['rifle']['frame_shots']>0 and r['aim_requested'] and not r['aim_blocked'] for r in flight))
                check(name+f':air_ads_{begin}',any(abs(r['view_fov']-78)<.01 and r['aim_requested'] for r in flight))
            stopped=[r for r in rows if r['ballistics']['scale']==0]
            born_after=stopped[0]['ballistics']['firing_clock']
            newborn=[b for r in stopped for b in r['ballistics']['bullets'] if b['birth_time']>=born_after]
            check(name+':newborns_stop_exactly',bool(newborn) and all(b['age']==0 and b['travel']==0 for b in newborn))
            check(name+':reset_cleans',last['ballistics']['active']==last['rifle']['effects']==last['rifle']['props']==0)
        if 'StopSelf60' in name:
            stopped=[r for r in rows if r['ballistics']['scale']==0]
            check(name+':normal_movement_during_stop',max(math.dist(r['velocity'],[0,0,0]) for r in stopped)>=359)
            check(name+':own_contact_once',last['ballistics']['self_hits']==1 and any(r['ballistics']['last_hit']=='SELF HIT' and
                  r['ballistics']['last_hit_shooter'] for r in stopped))
            bullets=[b for r in stopped for b in r['ballistics']['bullets']]
            check(name+':stopped_age_distance',bool(bullets) and all(b['age']==b['travel']==0 for b in bullets))
            check(name+':resume_quarter_then_normal',any(r['ballistics']['scale']==.25 for r in rows) and
                  last['ballistics']['scale']==1 and last['rifle']['shots']==3 and last['ballistics']['active']==0)
        if 'Reload10' in name:
            reload_rows=[r for r in rows if r['rifle']['reloading']]
            check(name+':real_reload_blocks',bool(reload_rows) and len({r['rifle']['shots'] for r in reload_rows})==1)
            check(name+':real_commit_once',last['rifle']['reloads']==last['rifle']['transfers']==1 and last['rifle']['transferred_rounds']==6)
            committed=next(r for r in rows if r['rifle']['transfers']==1)
            later=[s['time'] for s in shots if s['time']>=committed['ballistics']['firing_clock']-1e-6]
            check(name+':resume_without_precommit_debt',bool(later) and later[0]>=committed['ballistics']['firing_clock']-1e-6 and
                  all(abs(b-a-.085)<1e-6 for a,b in zip(later,later[1:])))
        if 'Pair10' in name or 'SampledTap10' in name:
            summary.update(input_presses=last['rifle']['input_presses'],input_releases=last['rifle']['input_releases'],
                           last_press_sample=last['rifle']['last_press_sample'],last_release_sample=last['rifle']['last_release_sample'],
                           dry_feedback_requests=last['rifle']['dry_feedback_requests'],dry_montages=last['rifle']['dry_fire'])
            if 'SampledTap10' in name:
                check(name+':two_semi_shots',last['rifle']['shots']==2 and last['rifle']['input_presses']==2)
            elif last['rifle']['input_presses']:
                check(name+':delivered_press_retained',last['rifle']['dry_feedback_requests']==2 if 'Empty' in name else last['rifle']['shots']==2)
            else:
                check(name+':undelivered_edges_labeled',last['rifle']['shots']==0)
        if 'OneRound10' in name:
            fired=next(r for r in rows if r['rifle']['shots'])
            check(name+':accepted_round_presented',fired['rifle']['shots']==fired['rifle']['presentations']==1 and
                  fired['rifle']['dry_feedback_requests']==1 and fired['rifle']['dry_fire']==0 and
                  fired['montage']=='AM_TFA_FP_AR_Fire_Auto' and not fired['busy'])
            check(name+':later_dry_press',last['rifle']['shots']==last['rifle']['presentations']==last['rifle']['dry_fire']==1 and
                  last['rifle']['dry_feedback_requests']==2 and last['rifle']['magazine']==last['rifle']['reserve']==0)
        summaries.append(summary)
    return summaries

def correction2():
    for name, times in [('ResetSpacing85',[0,.085]),('ResetSpacing50',[0,.05]),('ResetSemiSpacing',[0,.09])]:
        result=read('Correction02/controlled-Native02-'+name+'.json')
        stamps('correction2:'+name,result,times)
        check('correction2:'+name+':ammo',result['rifle']['magazine']==28)
        check('correction2:'+name+':bounded_clean',result['cleanup'] and
              all(f['steps']<=32 and f['attempts']<=6 for f in result['frames']))

def corrections():
    def record(name): return read('Correction01/controlled-Native01-'+name+'.json')
    expected={
        'SemiQuick':[0], 'AutoQuick':[0], 'SameSampleRepress':[0], 'EmptyQuick':[],
        'Spacing85':[0,.1], 'Spacing50':[0,.06,.12], 'ReloadTie':[.2],
        'ResetTie':[.1], 'ActionTie':[.2], 'CapacityRecovery':[0,.510,.595,.680],
        'Cadence10':lattice(0,2),
    }
    for name,times in expected.items():
        data=record(name)
        stamps('correction:'+name,data,times)
        check('correction:'+name+':caps',all(r['steps']<=32 and r['attempts']<=6 for r in data['frames']))
        check('correction:'+name+':cleanup',data['cleanup'])
    empty=record('EmptyQuick')
    check('correction:empty_feedback_bounded',empty['rifle']['dry_feedback_requests']==2 and empty['rifle']['magazine']==empty['rifle']['reserve']==0)
    reload=record('ReloadTie')
    check('correction:reload_tie_real_transaction',reload['reload_request_accepted'] and reload['rifle']['reloads']==1 and
          reload['rifle']['canceled_reloads']==1 and reload['rifle']['transfers']==0 and reload['rifle']['magazine']==4 and reload['rifle']['reserve']==10)
    capacity=record('CapacityRecovery')
    check('correction:capacity_recovery_conserved',capacity['rifle']['magazine']==26 and capacity['world']['active']==4)
    contract=OUT/'Correction01/controlled-Native01-Contracts.json'
    if contract.exists():
        for key,value in json.loads(contract.read_text()).items():
            if isinstance(value,bool): check('correction:contracts:'+key,value)
    for kind in ['BackwardBirth','OlderHistory']:
        long,fine=record(kind+'-Long'),record(kind+'-Fine')
        for label,result in [('Long',long),('Fine',fine)]:
            check(kind+label+':births',result['rifle']['shots']==3)
            bullets=result['world']['bullets']
            check(kind+label+':frozen',all(b['age']==0 and b['travel']==0 and b['launch_clear'] for b in bullets))
            if kind=='BackwardBirth':
                check(kind+label+':no_prebirth_contacts',result['new_self_hits']==0 and len(bullets)==4)
            else:
                check(kind+label+':old_contact_after_later_birth',result['new_self_hits']==1 and len(bullets)==3 and
                      result['world']['last_hit_shot']==result['older_shot'] and abs(result['world']['last_contact_time']-.155)<1e-6 and
                      result['rifle']['recent_shots'][1]['time']<result['world']['last_contact_time'])
                check(kind+label+':attributed',bool(result['world']['last_hit_shooter']) and result['world']['last_hit']=='SELF HIT')
        left=sorted(long['world']['bullets'],key=lambda b:b['id'])
        right=sorted(fine['world']['bullets'],key=lambda b:b['id'])
        check(kind+':long_fine_positions',len(left)==len(right) and all(math.dist(a['position'],b['position'])<.001 for a,b in zip(left,right)))

if __name__ == '__main__':
    controlled('Candidate01-')
    summaries=actual(sys.argv[1] if len(sys.argv)>1 else 'Actual02-')
    if (OUT/'Correction01/controlled-Native01-Cadence10.json').exists():
        corrections()
        root=OUT
        OUT=OUT/'Correction01'
        summaries+=actual('Input01-')
        OUT=root
    if (OUT/'Correction02/controlled-Native02-ResetSpacing85.json').exists():
        correction2()
        root=OUT
        OUT=OUT/'Correction02'
        summaries+=actual('AfterFix-')
        OUT=root
    result=dict(checks=checks,passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks),actual=summaries)
    dest=OUT/(sys.argv[2] if len(sys.argv)>2 else 'verification01.json')
    assert not dest.exists()
    dest.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(dict(passed=result['passed'],failed=result['failed'],failures=[c for c in checks if not c['passed']],actual=summaries),indent=2))
    if result['failed']: sys.exit(1)
