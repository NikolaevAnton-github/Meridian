"""Owner-directed revision 07: thicker angular chunks and an inset steel cage.

Undo revision 04's large coordinate waves before applying a gentler depth map.
The intact stone planes remain fixed, while their fracture rims become straight
polygon segments. Join isolated stone chips to their concrete backing.
"""
import ast
import functools
import json
import math
from pathlib import Path

import generate_progressive as g
import shape_spalling as shape

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'Assets/Source/ReinforcedColumn01/ReinforcedColumn02-Candidate01'
LIMIT = 118.2
BAR_AXIS = 89.8


def unwarp(p):
    result=list(p)
    for k in (2,1,0):
        center=140. if k==2 else 0.
        limit=140. if k==2 else LIMIT
        value=result[k]-center
        if abs(value)>=limit-1e-8:
            continue
        a,b=result[(k+1)%3],result[(k+2)%3]
        shift=1.4*math.sin(a*.061+b*.047+k*1.9)
        shift+=4.5*math.sin(a*.173-b*.139+k*2.3)
        shift+=1.8*math.sin(a*.417+b*.329+k*1.7)
        shift+=.45*math.sin(a*1.07-b*.89+k*2.7)
        result[k]=center+limit*math.tanh(math.atanh(value/limit)-shift/limit)
    return result


def angular_map(p):
    x,y,z=p
    radius=max(abs(x),abs(y))
    if radius>=LIMIT-1e-6 or radius<1e-8 or z>280.00001:
        return tuple(round(v,5) for v in p)
    # A much weaker compression than revision 06 leaves substantial concrete
    # thickness. Remove its broad noisy shoulders and the previous 8 cm waves.
    r=radius/LIMIT
    mapped=radius/(.5+.5*r)
    qx,qy=x*LIMIT/radius,y*LIMIT/radius
    # Sub-centimetre faceted relief affects the concrete, fading at the stone.
    relief=.6*shape.noise(qx+7,qy-19,z+11,12.)*min(1.,(LIMIT-radius)/5.)
    mapped+=relief
    ratio=mapped/radius
    return (round(x*ratio,5),round(y*ratio,5),round(z,5))


@functools.lru_cache(maxsize=900000)
def transform(p):
    if p[2]>280.00001:
        return p
    return angular_map(unwarp(p))


def make_steel():
    # Reuse the original tube construction without executing that generator's
    # top-level authoring or overwriting its immutable source files.
    tree=ast.parse((ROOT/'Scripts/ReinforcedColumn01/generate_source.py').read_text())
    names={'mesh','sub','cross','dot','tri','quad','tube'}
    module=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[])
    context={'math':math,'steel':dict(vertices=[],triangles=[])}
    exec(compile(module,'original-steel-tubes','exec'),context)
    tube=context['tube']
    bars=set()
    for i in range(8):
        t=round(-BAR_AXIS+2*BAR_AXIS*i/7,5)
        bars.update([(t,-BAR_AXIS),(t,BAR_AXIS),(-BAR_AXIS,t),(BAR_AXIS,t)])
    for x,y in sorted(bars):
        points=[];radii=[]
        for z in range(-40,341,4):
            for dz,radius in [(0,1.4),(.6,1.54),(1.2,1.4)]:
                points.append([x,y,z+dz]);radii.append(radius)
        tube(points,radii)
    for z in range(10,311,20):
        points=[]
        for sx,sy,start in [(1,1,0),(-1,1,90),(-1,-1,180),(1,-1,270)]:
            for i in range(7):
                angle=math.radians(start+i*15)
                points.append([sx*(BAR_AXIS-2.2)+4.2*math.cos(angle),sy*(BAR_AXIS-2.2)+4.2*math.sin(angle),float(z)])
        points.append(points[0]);tube(points,.6)
        for t in [-3*BAR_AXIS/7,3*BAR_AXIS/7]:
            tube([[-BAR_AXIS,t,z],[BAR_AXIS,t,z],[BAR_AXIS-3,t-3,z]],.6)
            tube([[t,-BAR_AXIS,z],[t,BAR_AXIS,z],[t-3,BAR_AXIS-3,z]],.6)
    return context['steel']


def merge(pieces,members):
    if len(members)==1:
        return pieces[members[0]]
    faces={}
    for i in members:
        for triangle in pieces[i]['triangles']:
            key=tuple(sorted(tuple(pieces[i]['vertices'][v]) for v in triangle[:3]))
            if key in faces:
                del faces[key]
            else:
                faces[key]=(i,triangle)
    result=g.empty();vertices={}
    for i,triangle in faces.values():
        indices=[]
        for v in triangle[:3]:
            if (i,v) not in vertices:
                vertices[i,v]=len(result['vertices'])
                for field in ['vertices','normals','uvs']:
                    result[field].append(pieces[i][field][v])
            indices.append(vertices[i,v])
        result['triangles'].append(indices+[triangle[3]])
    return result


def main():
    output=SOURCE/'column07.json'
    assert not output.exists(), 'Keep previous source revisions immutable.'
    source=json.loads((SOURCE/'column04.json').read_text())
    design=json.loads((SOURCE/'design04.json').read_text())
    old_design=json.loads((SOURCE/'design05.json').read_text())
    shape.transform=transform
    shape.transform_mesh(source['core'],900)
    for i,piece in enumerate(source['pieces']):
        shape.transform_mesh(piece)
        if i%100==0:
            print('Angular pieces',i,flush=True)
    # Eliminate the sixteen isolated 1.8 cm stone-only leaves. Split the same
    # number of old interior unions to retain 480 physical bodies overall.
    groups=[list(group) for group in old_design['merge_groups']]
    shallow=[i for i,row in enumerate(design['piece_meta']) if row['shallow']]
    for chip in shallow:
        base=next(group for group in groups if chip-1 in group)
        extra=next(group for group in groups if chip in group)
        assert base is not extra and len(extra)==1
        base.extend(extra);groups.remove(extra)
    for _ in shallow:
        group=next(group for group in reversed(groups) if len(group)>1 and all(design['piece_meta'][i]['layer']>0 for i in group))
        groups.append([group.pop()])
    groups=sorted([sorted(group) for group in groups],key=min)
    pieces=source['pieces']
    source['pieces']=[merge(pieces,members) for members in groups]
    remap={old:i for i,group in enumerate(groups) for old in group}
    source['clusters']=[sorted({remap[i] if i<644 else 480+i-644 for i in group}) for group in source['clusters']]
    source['steel']=make_steel()
    source['preserve_static_meshes']=False
    # No new authoring previews: the owner explicitly requested no further
    # viewing/testing. Existing revision-06 preview assets remain historical.
    source.pop('previews',None)
    collision=json.loads((SOURCE/'collision04.json').read_text())
    for leaf in collision['leaves'][:644]:
        for i,p in enumerate(leaf):
            leaf[i]=transform(tuple(p))
    for row in design['piece_meta']:
        row['seed']=angular_map(row['seed'])
    record=dict(revision='07',source_revision='04',units='centimetres',
        outer_cm=[240,240,1800],affected_height_cm=[0,280],stone_thickness_cm=1.8,
        geometry_operation='Undo large smooth fracture waves, then apply half-depth radial map with 0.6 cm faceted relief',
        dynamic_bodies=480,original_dynamic_bodies=644,anchors=len(source['anchors']),
        merge_groups=groups,standalone_stone_chips=0,bonded_stone_chip_merges=len(shallow),
        longitudinal_bars=28,longitudinal_diameter_cm=2.8,longitudinal_axis_offset_cm=BAR_AXIS,
        longitudinal_spacing_cm=2*BAR_AXIS/7,tie_diameter_cm=1.2,tie_spacing_cm=20,
        reinforcement_inset_delta_cm=110.8-BAR_AXIS,
        core_triangles=len(source['core']['triangles']),
        fragment_triangles=sum(len(p['triangles']) for p in source['pieces']),
        steel_triangles=len(source['steel']['triangles']),
        piece_meta=[dict(design['piece_meta'][min(group)],original_piece_ids=group) for group in groups],
        owner_requested_no_additional_tests=True)
    output.write_text(json.dumps(source,separators=(',',':')),encoding='utf-8')
    (SOURCE/'collision07.json').write_text(json.dumps(collision,separators=(',',':')),encoding='utf-8')
    (SOURCE/'design07.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in record.items() if k not in ['piece_meta','merge_groups']}))


if __name__=='__main__':
    main()
