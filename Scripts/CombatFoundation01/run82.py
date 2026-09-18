"""MSQ-82 focused cases on the existing transport, recorder and native probe seam."""
import json
import sys
from pathlib import Path
from client68 import epic, work as original_work
import run68

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/CombatTiming01/Worker'

def work(operation, argument=''):
    return original_work('timing_' + operation if operation in
                         ['frame_rate', 'verify', 'state', 'close', 'handoff', 'probe', 'ballistics', 'corrections']
                         else operation, argument)

def fill(prefix, duration=2.0, step=1/60):
    result = list(prefix)
    while sum(result) < duration - 1e-10:
        result.append(min(step, duration - sum(result)))
    return result

def controlled_cases():
    cases = [dict(name=f'Cadence{fps}', deltas=fill([], step=1/fps)) for fps in [10, 30, 60, 120, 144]]
    cases += [dict(name='Hitch150', deltas=fill([1/60]*12 + [.15])),
              dict(name='Hitch250', deltas=fill([.25])),
              dict(name='Jitter', deltas=fill([.011, .1, .007, .033, .15, .25]*3)),
              dict(name='Clamp50', interval=.001, deltas=[.25]*4),
              dict(name='Extreme', deltas=[.1, 2.0, .1, .25, .1, .1],
                   events=[dict(frame=4, type='release'), dict(frame=5, type='press')]),
              dict(name='ReleaseRepress', deltas=[.25]*4,
                   events=[dict(frame=1, type='release'), dict(frame=2, type='press')]),
              dict(name='Capacity', capacity=1, scale=0, deltas=[.25]*3),
              dict(name='Empty', magazine=2, reserve=0, deltas=[.25]*3),
              dict(name='Mode', deltas=[.1]*6,
                   events=[dict(frame=1, type='mode'), dict(frame=2, type='release'),
                           dict(frame=2, type='mode'), dict(frame=3, type='press'),
                           dict(frame=4, type='release'), dict(frame=5, type='press')]),
              dict(name='Reset', deltas=[.25]*4,
                   events=[dict(frame=1, type='reset'), dict(frame=3, type='press')]),
              dict(name='ReloadCommit', magazine=5, reserve=10, deltas=[.25]*6,
                   events=[dict(frame=1, type='reload'), dict(frame=2, type='commit')]),
              dict(name='ReloadCancel', magazine=5, reserve=10, deltas=[.25]*4,
                   events=[dict(frame=1, type='reload'), dict(frame=2, type='cancel')]),
              dict(name='ActionLock', deltas=[.25]*5,
                   events=[dict(frame=1, type='lock'), dict(frame=2, type='unlock')]),
              dict(name='Resume', scale=0, deltas=[.25]*3,
                   events=[dict(frame=1, type='release'), dict(frame=2, type='scale', value=1)])]
    for scale in [1, .25, 0]:
        for label, deltas in [('Long', [.25]), ('Fine', [.005]*50)]:
            cases.append(dict(name=f'Birth{scale}-{label}', scale=scale, deltas=deltas))
            cases.append(dict(name=f'MoveTurn{scale}-{label}', scale=scale, deltas=deltas,
                              view_speed=100, strafe_speed=70, yaw_speed=180))
    for distance in [25, 300]:
        for label, deltas in [('Long', [.25]), ('Fine', [.005]*50)]:
            cases.append(dict(name=f'Cover{distance}-{label}', cover_x=distance, deltas=deltas,
                              view_speed=20, strafe_speed=30, yaw_speed=30, speed=30000))
    cases.append(dict(name='FrozenSelf', kind='self', scale=0, view_speed=400, deltas=[.25]))
    cases.append(dict(name='Contracts', kind='contracts'))
    return cases

def correction_cases():
    def event(frame, kind, **extra): return dict(frame=frame,type=kind,**extra)
    cases=[
        dict(name='SemiQuick',automatic=0,deltas=[.25],events=[event(0,'release')]),
        dict(name='AutoQuick',deltas=[.25],events=[event(0,'release')]),
        dict(name='SameSampleRepress',automatic=0,deltas=[.25],events=[event(0,'release'),event(0,'press'),event(0,'release')]),
        dict(name='EmptyQuick',automatic=0,magazine=0,reserve=0,deltas=[.1]*5,
             events=[event(0,'release'),event(1,'press'),event(1,'release'),event(4,'press'),event(4,'release')]),
        dict(name='Spacing85',automatic=0,deltas=[.02]*6,
             events=[event(0,'release'),event(1,'press'),event(1,'release'),event(4,'press'),event(4,'release'),event(5,'press'),event(5,'release')]),
        dict(name='Spacing50',automatic=0,interval=.001,deltas=[.02]*7,
             events=[event(0,'release'),event(1,'press'),event(1,'release'),event(3,'press'),event(3,'release'),event(5,'press'),event(5,'release'),event(6,'press'),event(6,'release')]),
        dict(name='ReloadTie',automatic=0,magazine=5,reserve=10,deltas=[.1]*3,
             events=[event(0,'release'),event(0,'reload'),event(1,'cancel'),event(2,'press'),event(2,'release')]),
        dict(name='ResetTie',automatic=0,deltas=[.1]*3,
             events=[event(0,'release'),event(0,'reset'),event(1,'press'),event(1,'release')]),
        dict(name='ActionTie',automatic=0,deltas=[.1]*3,
             events=[event(0,'release'),event(0,'lock'),event(1,'unlock'),event(2,'press'),event(2,'release')]),
        dict(name='CapacityRecovery',capacity=1,scale=0,deltas=[.25]*3,events=[event(2,'capacity',value=128)]),
    ]
    for label,deltas in [('Long',[.25]),('Fine',[.005]*50)]:
        cases.append(dict(name='BackwardBirth-'+label,kind='self',scale=0,view_speed=-400,deltas=deltas))
    for label,deltas in [('Long',[.18]),('Fine',[.005]*36)]:
        cases.append(dict(name='OlderHistory-'+label,kind='self',scale=0,view_speed=100,deltas=deltas))
    # The new press queue also participates in continuous auto at the lowest FPS.
    cases.append(dict(name='Cadence10',deltas=fill([],step=.1)))
    cases.append(dict(name='Contracts',kind='contracts'))
    return cases

def correction2_cases():
    return [
        dict(name='ResetSpacing85',deltas=[.01,.09],events=[dict(frame=1,type='reset'),dict(frame=1,type='press')]),
        dict(name='ResetSpacing50',interval=.001,deltas=[.01,.05],events=[dict(frame=1,type='reset'),dict(frame=1,type='press')]),
        dict(name='ResetSemiSpacing',automatic=0,deltas=[.01,.04,.04,.01],events=[dict(frame=1,type='reset'),dict(frame=1,type='press'),dict(frame=1,type='release'),dict(frame=3,type='press'),dict(frame=3,type='release')]),
    ]

if __name__ == '__main__':
    mode = sys.argv[1]
    prefix = sys.argv[2] if len(sys.argv) > 2 else 'Candidate01-'
    if mode in ['controlled', 'correction', 'correction2']:
        assert not epic('EditorToolset.EditorAppToolset', 'IsPIERunning')
        work('performance')
        try:
            epic('EditorToolset.EditorAppToolset', 'StartPIE', {'options': dict(
                bSimulate=False, playMode='PlayMode_InViewPort', warmupSeconds=.5)})
            selected_cases = correction2_cases() if mode == 'correction2' else correction_cases() if mode == 'correction' else controlled_cases()
            for case in selected_cases:
                case['name'] = prefix + case['name']
                case['correction'] = 2 if mode == 'correction2' else mode == 'correction'
                if len(sys.argv) > 3 and sys.argv[3] not in case['name']:
                    continue
                if any(e['type'] == 'reload' for e in case.get('events', [])):
                    # Authored mode montages from another synthetic case may still
                    # own a busy lock. Reload evidence needs a fresh pawn/session.
                    epic('EditorToolset.EditorAppToolset', 'StopPIE')
                    epic('EditorToolset.EditorAppToolset', 'StartPIE', {'options': dict(
                        bSimulate=False, playMode='PlayMode_InViewPort', warmupSeconds=.5)})
                result = work('probe', json.dumps(case))
                print(json.dumps(dict(name=case['name'], shots=result.get('rifle', {}).get('shots'),
                                      overloads=result.get('world', {}).get('overload_frames'),
                                      barriers=result.get('world', {}).get('geometry_barriers'),
                                      failures=[k for k, v in result.items() if v is False],
                                      error=result.get('error'))), flush=True)
            if len(sys.argv) <= 3 and mode == 'controlled':
                for kind in ['ballistics', 'corrections']:
                    result = work(kind, prefix.rstrip('-'))
                    print(json.dumps(dict(name=kind, failures=[k for k,v in result.items() if v is False])), flush=True)
        finally:
            if epic('EditorToolset.EditorAppToolset', 'IsPIERunning'):
                epic('EditorToolset.EditorAppToolset', 'StopPIE')
            work('performance', 'restore')
    elif mode in ['actual','corrected_actual','correction2_actual']:
        run68.OUT = OUT / ('Correction02' if mode == 'correction2_actual' else 'Correction01') if mode != 'actual' else OUT
        run68.work = work
        file = 'timing-correction02-cases.json' if mode == 'correction2_actual' else 'timing-input-cases.json' if mode == 'corrected_actual' else 'timing-cases.json'
        for case in json.loads((ROOT / 'Scripts/CombatFoundation01' / file).read_text()):
            if len(sys.argv) > 4 and sys.argv[4] not in case['name']:
                continue
            case['name'] = prefix + case['name']
            case['correction'] = 2 if mode == 'correction2_actual' else mode == 'corrected_actual'
            if case.pop('capture', False):
                case['video_pid'] = int(sys.argv[3])
            run68.run(case)
