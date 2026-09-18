"""Final evaluated contact/recovery metrics and reviewable screen evidence."""
import json
import math
import wave
from pathlib import Path
import numpy as np
import av
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]/'Saved/PurchasedArms02/Worker'
def arm(r): return next(p for p in r['parts'] if p['component']=='CharacterMesh0')
def phase(r): return max((p for p in arm(r)['evaluation']['players'] if 'BlendSpacePlayer' in p['node']),key=lambda p:p['weight'])['phase']
def unique(rows):
    result=[]; previous=None
    for r in rows:
        value=arm(r)['evaluation']['evaluations']
        if value!=previous: result.append(r)
        previous=value
    return result
def main():
    result=[]
    files=sorted(ROOT.glob('Recovery02-*Reload.json'))+sorted(ROOT.glob('Recovery02-*Empty.json'))+sorted(ROOT.glob('Views01-*.json'))
    for path in files:
        data=json.loads(path.read_text()); rows=unique(data['rows'])
        control_name=path.stem.replace('Views01','Recovery02').replace('Reload','Control').replace('Empty','Control')
        controls=unique([r for r in json.loads((ROOT/(control_name+'.json')).read_text())['rows'] if r['t']>1.3])
        phases=np.array([phase(r) for r in controls]); end=max(r['t'] for r in rows if r['reloading'])
        recovered=[r for r in rows if r['t']>end+.25]
        metrics={n:[] for n in ['ik_hand_gun','hand_l','hand_r']}; rotations={n:[] for n in metrics}
        for r in recovered:
            diff=np.abs(phases-phase(r)); c=controls[int(np.argmin(np.minimum(diff,1-diff)))]
            for n in metrics:
                a,b=arm(r)['bones'][n],arm(c)['bones'][n]
                metrics[n].append(float(np.linalg.norm(np.array(a['p'])-b['p'])))
                dot=float(abs(np.dot(a['q'],b['q'])))/float(np.linalg.norm(a['q'])*np.linalg.norm(b['q']))
                rotations[n].append(math.degrees(2*math.acos(min(1,dot))))
        # Establish each magazine's identity from the initial assembled position, then retain that identity.
        initial_receiver=next(p for p in rows[0]['parts'] if p['component']=='SK_Receiver')
        magazines=[p for p in rows[0]['parts'] if p['component']=='SkeletalMesh' and 'BaseMagazine' in p['actor']]
        main_actor=min(magazines,key=lambda p:np.linalg.norm(np.array(p['camera']['p'])-initial_receiver['bones']['SOCKET_Magazine']['p']))['actor']
        seated=[]; clocks=[]
        for r in recovered:
            receiver=next(p for p in r['parts'] if p['component']=='SK_Receiver')
            for p in r['parts']:
                if p['component']=='SkeletalMesh' and p['actor']==main_actor:
                    seated.append(float(np.linalg.norm(np.array(p['camera']['p'])-receiver['bones']['SOCKET_Magazine']['p'])))
            if 'evaluation' in receiver: clocks.append(abs(receiver['evaluation']['action_time']-arm(r)['evaluation']['action_time']))
        result.append({'case':path.stem,'raw_samples':len(data['rows']),'unique_samples':len(rows),
            'recovery_seconds':rows[-1]['t']-end,'position_max_cm':{n:max(v) for n,v in metrics.items()},
            'rotation_max_degrees':{n:max(v) for n,v in rotations.items()},'seated_magazine_max_cm':max(seated,default=None),
            'recovered_clock_delta':max(clocks,default=None),'paused':any(r['paused'] for r in rows),
            'shadow_violations':sum(any(p['shadow_flags']) for r in rows for p in r['parts']),
            'physics_shadow_violations':sum(p['shadow'] for r in rows for a in r.get('physics',[]) for p in a['parts'])})
    video=[]
    for path in sorted((ROOT/'Video').glob('Views01-*.mp4'))+sorted((ROOT/'Video').glob('Feedback01-*.mp4')):
        meta=json.loads(path.with_suffix('.json').read_text()); stamps=[r['elapsed'] for r in meta['frames']]
        video.append({'file':path.name,'frames':len(stamps),'duration':stamps[-1], 'fps':(len(stamps)-1)/(stamps[-1]-stamps[0]),
            'max_interval':max(b-a for a,b in zip(stamps,stamps[1:]))})
        targets=[1.5,5.7,8.5] if path.stem.startswith('Views') else [2,5,8]
        captures=[]
        with av.open(str(path)) as container:
            for frame in container.decode(video=0):
                t=float(frame.pts*frame.time_base)
                if targets and t>=targets[0]:
                    targets.pop(0); im=frame.to_image(); im.thumbnail((620,440)); captures.append((t,im))
        if captures:
            board=Image.new('RGB',(sum(im.width for _,im in captures),470),(20,20,20)); draw=ImageDraw.Draw(board); x=0
            for t,im in captures:
                board.paste(im,(x,30));draw.text((x+8,8),f'{path.stem} / video {t:.2f}s',fill='white');x+=im.width
            board.save(ROOT/'Video'/(path.stem+'-comparison.png'))
    audio=[]
    for path in (ROOT/'Audio').glob('*.wav'):
        with wave.open(str(path)) as w:
            rate=w.getframerate(); channels=w.getnchannels(); data=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float).reshape(-1,channels)/32768
        if not len(data):
            audio.append({'file':path.name,'excluded':'Failed instrumentation probe; no audio frames.'})
            continue
        audio.append({'file':path.name,'rate':rate,'channels':channels,'duration':len(data)/rate,
            'peak':float(abs(data).max()),'rms_per_second':[float(np.sqrt(np.mean(data[i:i+rate]**2))) for i in range(0,len(data),rate)]})
    output={'recovery':result,'video':video,'audio':audio}
    (ROOT/'final-evaluated-analysis.json').write_text(json.dumps(output,indent=2))
    print(json.dumps(output,indent=2))
if __name__=='__main__': main()
