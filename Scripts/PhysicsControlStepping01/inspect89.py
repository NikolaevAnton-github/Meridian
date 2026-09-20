"""Focused state/foot summaries and timestamped frames from continuous video."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlStepping01/Worker'
name = sys.argv[1]
if len(sys.argv) > 2:
    sys.path.insert(0, str(ROOT / 'Saved/PurchasedArms04/Worker/PythonPackages'))
    import av
    times = [float(x) for x in sys.argv[2:]]
    dest = OUT / 'Video' / (name + '-Frames')
    dest.mkdir(exist_ok=True)
    with av.open(str(OUT / 'Video' / (name + '.mp4'))) as video:
        for frame in video.decode(video=0):
            if times and frame.time >= times[0]:
                t = times.pop(0)
                frame.to_image().save(dest / f'{t:06.2f}.png')
            if not times:
                break
    print(dest)
else:
    data = json.loads((OUT / (name + '.json')).read_text())
    changes = []
    previous = None
    for row in data['rows']:
        d = row['dummy']
        if not d:
            continue
        b, s = d['balance'], d['step']
        key = (b['state'], b['reason'], s['phase'], d['health'], d['epoch'], s['completed'])
        if key != previous:
            changes.append(dict(t=round(row['t'],3),health=d['health'],state=b['state'],reason=b['reason'],
                phase=s['phase'],step_reason=s['reason'],completed=s['completed'],started=s['started'],
                lean=b['lean_degrees'],soles=[b['sole_left_z'],b['sole_right_z']],drift=s['peak_support_drift_cm'],
                direction=s['direction'],swing=s['swing_foot'],stance=s['stance_pelvis']))
            previous = key
    print(json.dumps(dict(name=name,error=data['error'],counts=data['rows'][0]['counts'],
        ammo=[data['rows'][0]['rifle']['magazine'],data['rows'][-1]['rifle']['magazine']],changes=changes),indent=2))
