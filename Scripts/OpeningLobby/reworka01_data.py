"""Candidate geometry from the immutable owner-selected A dimension source (metres)."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'Saved/OpeningLobby/ArchitectureReworkA01/Worker'
SRC = ROOT/'Assets/Source/OpeningLobby/ArchitectureReworkA01'
MAP = '/Game/Maps/L_OpeningLobby_ArchitectureReworkA01'
BASE = '/Game/Maps/L_OpeningLobby_Layout03'
ASSETS = '/Game/OpeningLobby/ArchitectureReworkA01'
DESIGN_PATH = ROOT/'Assets/Concepts/OpeningLobby/ArchitectureRework01/design.json'
D = json.loads(DESIGN_PATH.read_text())
S, A = D['shared'], D['variants']['A']

def geometry():
    modules, instances = {}, {}

    def add(name, bounds, material='Stone', module=None, blocking=True, solids=None):
        # Bounds use [Xmin,Xmax,Ymin,Ymax,Zmin,Zmax], as the approved drawing generator.
        center = [(bounds[i*2]+bounds[i*2+1])/2 for i in range(3)]
        size = [bounds[i*2+1]-bounds[i*2] for i in range(3)]
        module = module or name
        absolute = solids or [bounds]
        local = [[v-center[i//2] for i,v in enumerate(b)] for b in absolute]
        definition = dict(size_m=size, boxes_m=local, material=material)
        if module in modules:
            assert all(abs(a-b)<1e-6 for a,b in zip(modules[module]['size_m'],size)), module
        else:
            modules[module] = definition
        instances[name] = dict(module=module, center_m=center, size_m=size, bounds_m=bounds, blocking=blocking)

    p, q, e, upper, b, t = [A[n] for n in ['portal','shoulder','end_pier','upper','side_bay','transom']]
    height = S['hall']['height']
    for sign in [-1,1]:
        def sides(lo, hi):
            return [lo,hi] if sign>0 else [-hi,-lo]
        main = [p['back_x'],p['front_x'],*sides(p['abs_y_inner'],p['abs_y_outer']),0,height]
        lip = [p['back_x'],p['reveal_front_x'],*sides(p['reveal_abs_y_inner'],p['reveal_abs_y_outer']),0,p['top_band_bottom']]
        envelope = [p['back_x'],p['front_x'],*sides(p['reveal_abs_y_inner'],p['abs_y_outer']),0,height]
        add('PortalJamb_'+str(sign), envelope, solids=[main,lip])
        add('Shoulder_'+str(sign), [p['back_x'],q['front_x'],*sides(q['abs_y_min'],q['abs_y_max']),0,height], 'Wall','Shoulder')
        add('EndPier_'+str(sign), [e['back_x'],e['front_x'],*sides(e['abs_y_min'],e['abs_y_max']),0,e['height']], module='EndPier')
        beam = S['beam']
        add('Beam_'+str(sign), [e['front_x'],S['hall']['inner_x'],*sides(beam['abs_y_min'],beam['abs_y_max']),beam['z_min'],beam['z_max']], module='Beam')
        add('UpperWall_'+str(sign), [S['hall']['entrance_x'],S['hall']['inner_x'],*sides(upper['inner_abs_y'],upper['outer_abs_y']),upper['bottom_z'],height], 'Wall','UpperWall')
        x = S['piers']['x'][0]
        add('FirstPier_'+str(sign), [x-1.2,x+1.2,*sides(5.6,8),0,S['piers']['height']], module='FreePier')
        yl,yh = sides(b['abs_y_min'],b['abs_y_max'])
        x0,x1,w = b['x_min'],b['x_max'],b['edge_width']
        z0,z1 = b['edge_bottom_z'],b['soffit_z']
        solids = [[x0,x0+w,yl,yh,z0,z1],[x1-w,x1,yl,yh,z0,z1],
                  [x0+w,x1-w,yl,yl+w,z0,z1],[x0+w,x1-w,yh-w,yh,z0,z1]]
        add('SoffitPerimeter_'+str(sign),[x0,x1,yl,yh,z0,z1],'Ceiling','SoffitPerimeter',solids=solids)
        # Close the exterior end of the pocket to the entrance wall and continue
        # its ceiling beyond the first pier without reducing any other bay field.
        add('TerminalEndCeiling_'+str(sign),[-30,x0,yl,yh,9.2,9.6],'Ceiling','TerminalEndCeiling')
        add('TerminalField_'+str(sign),[x0,x1,yl,yh,9.2,9.6],'Ceiling','TerminalField')
        add('ContextAisleCeiling_'+str(sign),[x1,30,yl,yh,9.2,9.6],'Ceiling','ContextAisleCeiling')
        # Existing outside shell datum retained, with a genuine opening for panes.
        add('EntranceBacking_'+str(sign),[-30.4,-30,*sides(2.6,8),0,height],'Wall','EntranceBacking')

    add('PortalHead',[p['back_x'],p['front_x'],-p['abs_y_inner'],p['abs_y_inner'],p['top_band_bottom'],height])
    add('Datum',[t['back_x'],t['front_x'],-t['half_width'],t['half_width'],t['bottom_z'],t['top_z']])
    dc = S['door_collar']
    collar = [[dc['back_x'],dc['front_x'],-dc['outer_half_width'],-dc['inner_half_width'],0,dc['head_top']],
              [dc['back_x'],dc['front_x'],dc['inner_half_width'],dc['outer_half_width'],0,dc['head_top']],
              [dc['back_x'],dc['front_x'],-dc['inner_half_width'],dc['inner_half_width'],dc['head_bottom'],dc['head_top']]]
    add('DoorCollar',[dc['back_x'],dc['front_x'],-dc['outer_half_width'],dc['outer_half_width'],0,dc['head_top']],'Metal',solids=collar)
    g = S['entrance']
    gx,hw = g['glass_x'],g['field_width']/2
    add('UpperGlazing',[gx-.02,gx,-hw,hw,A['upper_glazing_sill'],g['upper_head']],'Glazing')
    # Split lights around the leaves/collar, so no invisible old glazing spans doors.
    for sign in [-1,1]:
        yl,yh = (dc['outer_half_width'],hw) if sign>0 else (-hw,-dc['outer_half_width'])
        add('LowerSidelight_'+str(sign),[gx-.02,gx,yl,yh,0,g['lower_height']],'Glazing','LowerSidelight')
        yl,yh = (0,g['leaf_width']) if sign>0 else (-g['leaf_width'],0)
        add('DoorLeaf_'+str(sign),[gx-.02,gx,yl,yh,0,g['leaf_height']],'Glazing','DoorLeaf')
    add('LowerOverlight',[gx-.02,gx,-dc['outer_half_width'],dc['outer_half_width'],dc['head_top'],g['lower_height']],'Glazing')
    # Unchanged 5.2 m field; the dark collar occupies its remaining area.
    mullions = S['reference_mullions']
    fw,depth = mullions['width'],mullions['depth']
    for i in range(mullions['columns']+1):
        y = -hw+g['field_width']*i/mullions['columns']
        if i==0: y+=fw/2
        if i==mullions['columns']: y-=fw/2
        add('UpperMullion_'+str(i),[gx,gx+depth,y-fw/2,y+fw/2,A['upper_glazing_sill'],g['upper_head']],'Metal','UpperMullion',False)
    for i in range(mullions['upper_rows']+1):
        z = A['upper_glazing_sill']+(g['upper_head']-A['upper_glazing_sill'])*i/mullions['upper_rows']
        if i==0: z+=fw/2
        if i==mullions['upper_rows']: z-=fw/2
        # Butt into vertical mullions with no coplanar cross intersections.
        for col in range(mullions['columns']):
            y0 = -hw+g['field_width']*col/mullions['columns']+(fw if col==0 else fw/2)
            y1 = -hw+g['field_width']*(col+1)/mullions['columns']-(fw if col==mullions['columns']-1 else fw/2)
            add('UpperTransom_%s_%s'%(i,col),[gx,gx+depth,y0,y1,z-fw/2,z+fw/2],'Metal','TransomEdge' if col in (0,3) else 'TransomInner',False)
    add('DoorMeetingStile',[gx,gx+.05,-.0125,.0125,0,g['leaf_height']],'Metal',blocking=False)
    return dict(design_sha256=hashlib.sha256(DESIGN_PATH.read_bytes()).hexdigest(), modules=modules,instances=instances)

def replaced(name):
    return name.startswith(('EntranceUpper','EntranceLower','EntranceLeaf','EntranceFieldEdge','EntranceEndBand_',
                            'LongLintel_','UpperInfill_','SideAisleCeiling_','Pier_0_')) or name=='EntranceBoundary'

def imported_module(name):
    # FBX -> Unreal converts Blender's right-handed Y to Unreal's left-handed Y.
    # Reuse the opposite native hand to preserve the common world-space section,
    # without negative actor scale or destructive changes to source geometry.
    return {'PortalJamb_1':'PortalJamb_-1','PortalJamb_-1':'PortalJamb_1'}.get(name,name)
