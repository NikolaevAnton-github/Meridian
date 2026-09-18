"""Correlate actual recording frames with physical/evaluated telemetry."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/PurchasedArms05/Worker'
sys.path.insert(0,str(ROOT/'Saved/PurchasedArms04/Worker/PythonPackages'))
import av
from PIL import Image,ImageDraw


def review(stem):
    data=json.loads((OUT/(stem+'.json')).read_text())
    rows=data['rows']
    jumps=[]
    for a,b in zip(rows,rows[1:]):
        if b['jump_starts']>a['jump_starts']:
            start=b['t']
            land=next(r['t'] for r in rows if r['t']>start and r['landings']>a['landings'])
            jumps.append((start,land))
    frames_meta=json.loads((OUT/'Video'/(stem+'.json')).read_text())['frames']
    frames=[]
    with av.open(str(OUT/'Video'/(stem+'.mp4'))) as stream:
        for f in stream.decode(video=0): frames.append(f.to_image())
    assert len(frames)==len(frames_meta)
    dest=OUT/'Views'
    dest.mkdir(exist_ok=True)
    records=[]
    for jump,(start,land) in enumerate(jumps,1):
        stamps=[start-.1,start+.08,start+.27,land-.2,land-.02,land+.06,land+.18,land+.7,land+1.02,land+1.3]
        sheet=Image.new('RGB',(1280,5*455),'#111111')
        draw=ImageDraw.Draw(sheet)
        for index,t in enumerate(stamps):
            row=min(rows,key=lambda r:abs(r['t']-t))
            i=min(range(len(frames_meta)),key=lambda i:abs(frames_meta[i]['wall']-row['capture_wall_monotonic']))
            actual=min(rows,key=lambda r:abs(r['capture_wall_monotonic']-frames_meta[i]['wall']))
            view=frames[i].copy()
            view.thumbnail((640,431))
            x,y=index%2*640,index//2*455
            sheet.paste(view,(x,y+24))
            label=f't={actual["t"]:.3f} floor={not actual["falling"]} jump={actual["jump_phase"]:.3f} ammo={actual["ammo"]} ADS={actual["aim_requested"]}'
            draw.text((x+5,y+5),label,fill='white')
            records.append(dict(jump=jump,requested_t=t,actual_t=actual['t'],video_frame=i,
                sample_delta_ms=1000*(actual['capture_wall_monotonic']-frames_meta[i]['wall']),
                contact_offset_ms=1000*(actual['t']-land),falling=actual['falling'],jump_phase=actual['jump_phase']))
            if index in [3,5,6]:
                frames[i].save(dest/f'{stem}-jump{jump}-{index}.png')
        sheet.save(dest/f'{stem}-jump{jump}-sequence.jpg',quality=92)
    path=dest/(stem+'-frames.json')
    assert not path.exists()
    path.write_text(json.dumps(records,indent=2))
    print(json.dumps(dict(case=stem,frames=len(frames),jumps=len(jumps),selected=len(records))))


if __name__=='__main__':
    for stem in sys.argv[1:]: review(stem)
