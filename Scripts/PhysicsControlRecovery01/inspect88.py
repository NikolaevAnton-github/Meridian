"""Summaries and timestamped frames from the retained continuous recorder."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlRecovery01/Worker'
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
                frame.to_image().save(dest / f'{t:05.1f}.png')
            if not times:
                break
    print(dest)
else:
    data = json.loads((OUT / (name + '.json')).read_text())
    changes = []
    previous = None
    for row in data['rows']:
        d = row['dummy']; b = d['balance']
        key = (b['state'], b['reason'], d['health'], d['epoch'])
        if key != previous:
            changes.append(dict(t=round(row['t'], 3), health=d['health'], **b))
            previous = key
    print(json.dumps(dict(name=name, error=data['error'], counts=data['rows'][0]['counts'],
        ammo=[data['rows'][0]['rifle']['magazine'], data['rows'][-1]['rifle']['magazine']],
        changes=changes), indent=2))
