"""Assert the bounded review corrections against actual capsule and returned view."""
import json
from pathlib import Path
import numpy as np
import av
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parents[2]/'Saved/PurchasedArms02/Worker'

def read(name):
    data=json.loads((OUT/(name+'.json')).read_text())
    assert not data['error'],data['error']
    assert not any(r['paused'] for r in data['rows'])
    return data['rows']

def degrees(q):
    q=np.array(q,dtype=float)
    return float(np.degrees(2*np.arccos(np.clip(abs(q[3])/np.linalg.norm(q),0,1))))

def main():
    rows=read('Correction01-Capsule')
    assert all(r['capsule_radius']==34 for r in rows)
    assert all(r['capsule_half_height']==(56 if r['crouched'] else 88) for r in rows)
    assert all(('CROUCH' in r['source_stance'])==r['crouched'] for r in rows)
    blocked=[r for r in rows if 3.4<r['t']<4.8]
    assert blocked and all(r['crouched'] for r in blocked)
    standing=[r for r in rows if r['t']>9]
    assert all(not r['crouched'] for r in standing)
    assert all(np.linalg.norm(r['velocity'])<1 for r in standing)
    assert all(abs(r['camera']['p'][2]-r['location'][2]-82)<.001 for r in standing)
    capsule={'samples':len(rows),'radius_cm':[34,34],'half_heights_cm':[56,88],
        'blocked_samples':len(blocked),'wall_samples':len(standing),'wall_center':standing[-1]['location'],
        'last_camera_height_cm':standing[-1]['camera']['p'][2]-standing[-1]['location'][2]}
    cameras=[]
    for name in ['Correction02-CameraOff','Correction02-CameraOn']:
        data=read(name)
        action=[r for r in data if r['montage']=='AM_TFA_FP_AR_Inspect_Empty']
        assert action
        angles=[degrees(r['camera']['q']) for r in action]
        last=[r for r in data if r['t']>8]
        assert all(not r['camera_animation'] for r in last)
        assert max(degrees(r['camera']['q']) for r in last)<.001
        enabled=name.endswith('On')
        if enabled:
            assert all(r['camera_animation'] and not r['source_head_lock'] for r in action)
            assert max(angles)>1
            camera_error=max(float(np.linalg.norm(np.array(r['camera']['p'])-r['source_camera']['p'])) for r in action)
            rotation_error=max(float(2*np.degrees(np.arccos(np.clip(abs(np.dot(r['camera']['q'],r['source_camera']['q'])),0,1)))) for r in action)
            assert camera_error<.001 and rotation_error<.001
        else:
            assert max(angles)<.001
            camera_error=rotation_error=None
        cameras.append({'case':name,'samples':len(data),'action_samples':len(action),'returned_view_rotation_max_degrees':max(angles),
            'source_camera_position_error_cm':camera_error,'source_camera_rotation_error_degrees':rotation_error,
            'restored_view_rotation_max_degrees':max(degrees(r['camera']['q']) for r in last),
            'source_flag_means_head_reference_lock':True})
    result={'passed':True,'capsule':capsule,'camera':cameras}
    (OUT/'Correction01/targeted-verification.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
    frames=[]
    for name in ['Correction02-CameraOff','Correction02-CameraOn']:
        for frame in av.open(str(OUT/'Video'/(name+'.mp4'))).decode(video=0):
            if float(frame.pts*frame.time_base)>3.9:
                im=frame.to_image();im.thumbnail((800,550));frames.append((name,im));break
    board=Image.new('RGB',(sum(im.width for _,im in frames),580),(20,20,20));d=ImageDraw.Draw(board);x=0
    for name,im in frames:
        d.text((x+8,8),name+' / authored inspection action',fill='white');board.paste(im,(x,30));x+=im.width
    board.save(OUT/'Video/Correction02-Camera-comparison.png')

if __name__=='__main__': main()
