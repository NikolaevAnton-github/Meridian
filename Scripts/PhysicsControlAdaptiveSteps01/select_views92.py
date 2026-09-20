"""Select actual capture frames using retained monotonic probe/capture clocks."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlAdaptiveSteps01/Worker'
sys.path.insert(0,str(ROOT/'Saved/PurchasedArms04/Worker/PythonPackages'))
import av

index = []
for name in sys.argv[1:]:
    data = json.loads((OUT/(name+'.json')).read_text())
    rows = [r for r in data['rows'] if r.get('dummy')]
    clock = json.loads((OUT/(name+'-clock.json')).read_text())['recording_monotonic_start']
    ready = json.loads((OUT/'Video'/(name+'.ready.json')).read_text())['wall']
    chosen = [('initial',rows[0])]
    active = [r for r in rows if r['dummy']['step']['started'] == 1 and r['dummy']['step']['phase'] != 'IDLE']
    if active:
        transfer = [r for r in active if r['dummy']['step']['phase'] == 'TRANSFER']
        chosen.append(('transfer',transfer[-1]))
        swing = [r for r in active if r['dummy']['step']['phase'] == 'SWING']
        if swing:
            foot = swing[0]['dummy']['step']['swing_foot']
            sole = 'sole_left_z' if foot.endswith('_l') else 'sole_right_z'
            chosen.append(('apex',max(swing,key=lambda r:r['dummy']['balance'][sole])))
    falls = [r for r in rows if r['dummy']['balance']['state'] == 'FALLING']
    if falls:
        chosen.append(('fall',next((r for r in falls if r['world_time'] >= falls[0]['world_time']+.5),falls[-1])))
    chosen.append(('final',rows[-1]))
    requests = sorted([(clock-ready+r['wall'],label,r['t']) for label,r in chosen])
    dest = OUT/'Video'/(name+'-Frames'); dest.mkdir(exist_ok=True)
    with av.open(str(OUT/'Video'/(name+'.mp4'))) as video:
        for frame in video.decode(video=0):
            while requests and frame.time >= requests[0][0]:
                expected,label,t = requests.pop(0)
                path = dest/(label+'.png')
                frame.to_image().save(path)
                index.append(dict(record=name,label=label,probe_t=t,video_requested=expected,video_frame=frame.time,
                    clock_offset=clock-ready,path=path.relative_to(ROOT).as_posix()))
            if not requests:
                break
    assert not requests,(name,requests)
with (OUT/'selected-views01.json').open('x',encoding='utf-8') as stream:
    json.dump(index,stream,indent=2)
print(json.dumps(index))
