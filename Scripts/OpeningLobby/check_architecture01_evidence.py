"""Reuse accepted dimensional checks and verify native Architecture01 evidence."""
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/OpeningLobby/Stage2/Architecture01'

def dimensions():
    spec=importlib.util.spec_from_file_location('accepted_schedule_checker',ROOT/'Scripts/OpeningLobby/check_layout03_evidence.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.OUT=OUT/'Assembled'
    module.dimensions()

def captures():
    inventory=[]
    views=['C1-90','C1-75','C2-90','C2-75','C3-90','C3-context-90','Stone-90','Floor-90','MetalGlass-90','Checkpoint-90']
    for name in views:
        p=OUT/(name+'.png');data=p.read_bytes()
        assert data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==(1920,1080)
        camera=json.loads((OUT/(name+'-camera.json')).read_text())
        assert max(abs(a-b) for a,b in zip(camera['actual_xyz_cm'],camera['requested_xyz_cm']))<1
        assert abs(camera['actual_hfov']-camera['horizontal_fov'])<.01
        for a,b in zip(camera['actual_rotation'],[camera['pitch'],camera['yaw'],0]):
            assert abs((a-b+180)%360-180)<.01,(name,camera)
        if name.startswith('C') and name!='Checkpoint-90':
            old=json.loads((ROOT/'Saved/OpeningLobby/Layout03'/(name+'-camera.json')).read_text())
            assert max(abs(a-b) for a,b in zip(camera['actual_xyz_cm'],old['actual_xyz_cm']))<.1
            assert abs(camera['actual_hfov']-old['actual_hfov'])<.01
        inventory.append(dict(filename=p.name,sha256=hashlib.sha256(data).hexdigest(),resolution=[1920,1080],camera=camera))
    (OUT/'capture-inventory.json').write_text(json.dumps(inventory,indent=2))
    print('Six matched comparison and four detail views verified at native 1920x1080.')

if __name__=='__main__':
    import sys
    dimensions()
    if '--captures' in sys.argv:captures()
