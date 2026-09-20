"""Read retained runtime records; extract unmodified timestamped video frames."""
import json
import math
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlLegPose01/Worker'

def sub(a,b): return [x-y for x,y in zip(a,b)]
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def norm(a): return math.sqrt(dot(a,a))
def unit(a): return [x/max(norm(a),1e-10) for x in a]
def angle(a,b): return math.degrees(math.acos(max(-1,min(1,dot(unit(a),unit(b))))))
def geometry(bones):
    result={}
    for side in ['l','r']:
        h,k,f,t=[bones[n+'_'+side]['p'] for n in ['thigh','calf','foot','ball']]
        axis=unit(sub(f,h)); upper=sub(k,h)
        bend=sub(upper,[x*dot(upper,axis) for x in axis])
        result[side]=dict(flex=angle(sub(k,h),sub(f,k)),bend_yaw=math.degrees(math.atan2(bend[1],bend[0])),
            toe_yaw=math.degrees(math.atan2(t[1]-f[1],t[0]-f[0])),
            knee_to_toe=angle([*bend[:2],0],[t[0]-f[0],t[1]-f[1],0]),
            lengths=[norm(sub(k,h)),norm(sub(f,k))])
    result['pelvis_z']=bones['pelvis']['p'][2]
    return result

if __name__=='__main__':
    name=sys.argv[1]
    if len(sys.argv)>2:
        sys.path.insert(0,str(ROOT/'Saved/PurchasedArms04/Worker/PythonPackages'))
        import av
        times=[float(t) for t in sys.argv[2:]]
        dest=OUT/'Video'/(name+'-Frames'); dest.mkdir(exist_ok=True)
        with av.open(str(OUT/'Video'/(name+'.mp4'))) as video:
            for frame in video.decode(video=0):
                if times and frame.time>=times[0]:
                    t=times.pop(0); frame.to_image().save(dest/f'{t:06.2f}.png')
                if not times: break
        print(dest)
    else:
        data=json.loads((OUT/(name+'.json')).read_text()); changes=[]; previous=None
        for r in data['rows']:
            d=r['dummy']; b,s=d['balance'],d['step']
            key=(b['state'],s['phase'],s['completed'],d['epoch'])
            if key!=previous:
                changes.append(dict(t=round(r['t'],3),state=b['state'],reason=b['reason'],phase=s['phase'],
                    step_reason=s['reason'],completed=s['completed'],swing=s['swing_foot'],drift=s['peak_support_drift_cm'],
                    geometry=geometry(r['leg_bones'])))
                previous=key
        print(json.dumps(dict(name=name,error=data['error'],changes=changes,final=geometry(data['rows'][-1]['leg_bones'])),indent=2))
