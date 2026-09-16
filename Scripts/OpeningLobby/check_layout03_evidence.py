"""Independent schedule checks on saved actor bounds and capture metadata."""
from pathlib import Path
import hashlib
import json
import struct

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'Saved/OpeningLobby/Layout03'

def dimensions():
    s = json.loads((ROOT/'Assets/Concepts/OpeningLobby/ScaleReview01/schedule.json').read_text())
    a,e,h = s['architecture']['candidate'],s['end_fields']['candidate'],s['human_elements']
    b = json.loads((OUT/'construction.json').read_text())['actor_bounds']
    checks = []
    def check(name,actual,expected):
        checks.append(dict(name=name,actual_m=actual,expected_m=expected,error_m=abs(actual-expected),passed=abs(actual-expected)<=.05))
    def center(name,axis): return b[name]['center'][axis]/100
    def size(name,axis): return b[name]['extent'][axis]/50
    def face(name,axis,sign): return center(name,axis)+sign*size(name,axis)/2
    check('Interior length',face('InnerBoundary',0,-1)-face('EntranceBoundary',0,1),a['length'])
    check('Interior width',face('SideWall_1',1,-1)-face('SideWall_-1',1,1),a['width'])
    check('Interior height',face('CentralCeiling',2,-1)-face('Floor',2,1),a['height'])
    check('Floor datum',face('Floor',2,1),0)
    check('Central clear',face('Pier_0_1',1,-1)-face('Pier_0_-1',1,1),a['central_clear'])
    for sign in [-1,1]:
        check(f'Aisle {sign} width',abs(face('SideWall_'+str(sign),1,-sign)-face('Pier_0_'+str(sign),1,sign)),a['aisle_clear'])
        check(f'Aisle {sign} ceiling',face('SideAisleCeiling_'+str(sign),2,-1),a['aisle_height'])
        for axis,key in [(1,'lintel_width'),(2,'lintel_depth')]:
            check(f'Lintel {sign} {key}',size('LongLintel_'+str(sign),axis),a[key])
        check(f'Lintel {sign} underside',face('LongLintel_'+str(sign),2,-1),a['lintel_underside'])
        check(f'Strip {sign} width',size('FloorStrip_'+str(sign),1),a['floor_strip_width'])
        check(f'Strip {sign} center',center('FloorStrip_'+str(sign),1),sign*a['floor_strip_y'])
        for index,x in enumerate(a['pier_x']):
            name = f'Pier_{index}_{sign}'
            for axis,val in enumerate([x,sign*a['pier_y'],a['shaft_height']/2]):
                check(f'{name} center {axis}',center(name,axis),val)
            for axis,val in enumerate([a['pier_size'],a['pier_size'],a['shaft_height']]):
                check(f'{name} size {axis}',size(name,axis),val)
            if index:
                previous = f'Pier_{index-1}_{sign}'
                check(f'{name} pitch',center(name,0)-center(previous,0),a['bay_pitch'])
                check(f'{name} clear gap',face(name,0,-1)-face(previous,0,1),a['bay_clear'])
    for name,w,height,sill in [('EntranceUpperGlazing',e['entrance_field_width'],e['upper_height'],e['upper_sill']),
                              ('EntranceLowerField',e['entrance_field_width'],e['entry_field_height'],0),
                              ('InnerHighWindow',e['inner_window_width'],e['inner_window_height'],e['inner_window_sill'])]:
        check(name+' width',size(name,1),w)
        check(name+' height',size(name,2),height)
        check(name+' sill',face(name,2,-1),sill)
    for name,w,height in [('InnerDoorLeaf',h['inner_door']['candidate_width'],h['inner_door']['candidate_height']),
                          ('InnerDoorFrame',h['inner_door']['candidate_frame_width'],h['inner_door']['candidate_frame_height'])]+[
                          ('EntranceLeaf_'+str(sign),h['entrance_leaves']['candidate_leaf_width'],h['entrance_leaves']['candidate_leaf_height']) for sign in [-1,1]]:
        check(name+' width',size(name,1),w)
        check(name+' height',size(name,2),height)
        check(name+' floor',face(name,2,-1),0)
    d = h['detector']
    check('Detector clear width',face('DetectorPost_1',1,-1)-face('DetectorPost_-1',1,1),d['clear_width'])
    check('Detector clear height',face('DetectorHeader',2,-1),d['clear_height'])
    check('Detector outer width',size('DetectorHeader',1),d['clear_width']+2*d['post_width'])
    check('Detector outer height',face('DetectorHeader',2,1),d['clear_height']+d['header_depth'])
    for name in ['DetectorPost_-1','DetectorPost_1','DetectorHeader']:
        check(name+' depth',size(name,0),d['depth'])
        check(name+' X',center(name,0),d['x'])
    for sign in [-1,1]: check(f'Detector post {sign} width',size('DetectorPost_'+str(sign),1),d['post_width'])
    check('Detector header thickness',size('DetectorHeader',2),d['header_depth'])
    check('Detector Y',center('DetectorHeader',1),d['y'])
    station = h['station']
    for name,keys in [('StationBody',['depth_x','width_y','body_height']),('StationWorktop',['worktop_depth_x','worktop_width_y','worktop_thickness'])]:
        for axis,key in enumerate(keys): check(name+' '+key,size(name,axis),station[key])
        check(name+' X',center(name,0),station['x'])
        check(name+' Y',center(name,1),station['y'])
    check('Worktop top',face('StationWorktop',2,1),station['worktop_height'])
    # Nominal end-plane interpretation: measure leaf CENTER X, not a face.
    for name,plane in [('InnerDoorLeaf',a['length']/2),('EntranceLeaf_-1',-a['length']/2),('EntranceLeaf_1',-a['length']/2)]:
        check(name+' nominal end-plane center X',center(name,0),plane)
    for end,sign in [('Entrance',-1),('Inner',1)]:
        for side in [-1,1]:
            name = end+'EndBand_'+str(side)
            gap = -sign*(face(name,0,-sign)-face(end+'Boundary',0,-sign))
            check(name+' exposed facing offset',gap,.03)
            assert 0 < gap <= .05,(name,gap)
            check(name+' row Y',center(name,1),side*a['pier_y'])
            check(name+' width',size(name,1),a['pier_size'])
            check(name+' height',size(name,2),a['height'])
    # Require strictly separated layer volumes where their Y/Z areas overlap.
    for name,back,front,sign in [('Inner frame/leaf','InnerDoorFrame','InnerDoorLeaf',-1),
                                ('Entrance field/leaf','EntranceLowerField','EntranceLeaf_1',1),
                                ('Entrance field/leaf negative','EntranceLowerField','EntranceLeaf_-1',1),
                                ('Inner wall/frame','InnerBoundary','InnerDoorFrame',-1),
                                ('Entrance wall/field','EntranceBoundary','EntranceLowerField',1)]+[
                                ('Entrance leaf/trim '+str(y),'EntranceLeaf_1','EntranceLeafMullion_'+str(y),1) for y in [-1.04,0,1.04]]+[
                                ('Entrance leaf/head','EntranceLeaf_1','EntranceLeafHead',1)]:
        gap = sign*(face(front,0,-sign)-face(back,0,sign))
        checks.append(dict(name=name+' layer separation',actual_m=gap,expected_m='> 0',error_m=0,passed=gap>0))
    report = dict(passed=all(c['passed'] for c in checks),tolerance_m=.05,checks=checks)
    (OUT/'schedule-verification.json').write_text(json.dumps(report,indent=2))
    assert report['passed']
    print(f'{len(checks)} independent saved-bound schedule checks passed; max error {max(c["error_m"] for c in checks):.8f} m')

def captures():
    result = []
    for name in ['C1-90','C1-75','C2-90','C2-75','C3-90','C3-context-90','EndEntrance-110','EndInner-110']:
        path = OUT/(name+'.png')
        data = path.read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n'
        wh = struct.unpack('>II',data[16:24])
        assert wh == (1920,1080),(name,wh)
        camera = json.loads((OUT/(name+'-camera.json')).read_text())
        assert max(abs(a-b) for a,b in zip(camera['actual_xyz_cm'],camera['requested_xyz_cm'])) < 1
        assert abs(camera['actual_hfov']-camera['horizontal_fov']) < .01
        for actual,expected in zip(camera['actual_rotation'],[camera['pitch'],camera['yaw'],camera['roll']]):
            assert abs((actual-expected+180)%360-180) < .01
        result.append(dict(filename=path.name,resolution=wh,sha256=hashlib.sha256(data).hexdigest(),camera=camera))
    (OUT/'capture-inventory.json').write_text(json.dumps(result,indent=2))
    print('Six comparison and two supplemental full-resolution captures and camera metadata verified')

if __name__ == '__main__':
    import sys
    dimensions()
    if '--captures' in sys.argv:
        captures()
