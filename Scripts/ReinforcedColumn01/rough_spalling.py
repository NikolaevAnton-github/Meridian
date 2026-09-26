"""Revision 09: break broad core facets while retaining revision-08 fragment variety."""
import collections
import functools
import json
import math

import generate_progressive as g
import shape_spalling as shape
from varied_spalling import ROOT, SOURCE, LIMIT


@functools.lru_cache(maxsize=1100000)
def transform(p):
    x,y,z=p
    radius=max(abs(x),abs(y))
    if radius>=LIMIT-1e-6 or radius<1e-8 or z>280.00001:
        return p
    qx,qy=x*LIMIT/radius,y*LIMIT/radius
    fade=min(1.,max(0.,(280-z)/14.))
    field=(.85*shape.noise(qx+17,qy-31,z+29,34.)
           +.42*shape.noise(qx-13,qy+7,z-19,13.)
           +.14*shape.noise(qx+37,qy-11,z+5,5.5))
    # Alpha is constant along a square-section ray. This map stays strictly
    # increasing, preserves matching interfaces and pins the stone boundary.
    alpha=math.exp(fade*(math.log(.82)+field))
    ratio=1./(alpha+(1-alpha)*radius/LIMIT)
    return round(x*ratio,5),round(y*ratio,5),z


def smooth_core_concrete(mesh):
    accumulated=collections.defaultdict(lambda:[0.,0.,0.])
    concrete=set()
    for a,b,c,material in mesh['triangles']:
        if material!=2:
            continue
        face=g.cross(g.sub(mesh['vertices'][b],mesh['vertices'][a]),
                     g.sub(mesh['vertices'][c],mesh['vertices'][a]))
        for i in (a,b,c):
            concrete.add(i)
            normal=accumulated[tuple(mesh['vertices'][i])]
            for axis in range(3):
                normal[axis]+=face[axis]
    for i in concrete:
        mesh['normals'][i]=list(g.key(g.unit(accumulated[tuple(mesh['vertices'][i])])))


def main():
    paths=[SOURCE/(name+'09.json') for name in ('column','collision','design')]
    assert not any(p.exists() for p in paths)
    source=json.loads((SOURCE/'column08.json').read_text())
    design=json.loads((SOURCE/'design08.json').read_text())
    shape.transform=transform
    meshes=[(source['core'],900)]+[(m,0) for m in source['pieces']+source['anchors']]
    for ordinal,(mesh,z_offset) in enumerate(meshes):
        vertices,normals=mesh['vertices'],mesh['normals']
        shape.transform_mesh(mesh,z_offset)
        for i,(before,after) in enumerate(zip(vertices,mesh['vertices'])):
            if before==after:
                mesh['normals'][i]=normals[i]
        if ordinal%80==0:
            print('Rough interfaces',ordinal,flush=True)
    smooth_core_concrete(source['core'])
    collision=json.loads((SOURCE/'collision08.json').read_text())
    for leaf in collision['leaves']:
        for i,p in enumerate(leaf):
            leaf[i]=transform(tuple(p))
    for row in design['piece_meta']:
        row['seed']=transform(tuple(row['seed']))
    silhouettes=[]
    for i,piece in enumerate(source['pieces']):
        axis=0 if design['piece_meta'][i]['side']%2==0 else 1
        p=piece['vertices']
        width=max(v[axis] for v in p)-min(v[axis] for v in p)
        height=max(v[2] for v in p)-min(v[2] for v in p)
        silhouettes.append(dict(piece=i,width_cm=width,height_cm=height,aspect=max(width,height)/min(width,height)))
    design.update(revision='09',source_revision='08',previous_revision='08',
        geometry_operation=design['geometry_operation']+'; additional monotone radial relief and continuous concrete core normals',
        radial_relief_alpha='exp(fade * (log(0.82) + 0.85*N34 + 0.42*N13 + 0.14*N5.5))',
        core_concrete_normals='Area-weighted normals shared at coincident concrete vertices; stone and fragment edge normals retained',
        silhouettes=silhouettes)
    for path,data in zip(paths,(source,collision,design)):
        path.write_text(json.dumps(data,indent=2) if path==paths[2] else json.dumps(data,separators=(',',':')),encoding='utf-8')
    print(json.dumps(dict(revision='09',dynamic_bodies=len(source['pieces']),anchors=len(source['anchors']),
        widths_cm=[min(r['width_cm'] for r in silhouettes),max(r['width_cm'] for r in silhouettes)],
        heights_cm=[min(r['height_cm'] for r in silhouettes),max(r['height_cm'] for r in silhouettes)],
        compact=sum(r['aspect']<1.5 for r in silhouettes),elongated=sum(r['aspect']>2 for r in silhouettes))),flush=True)


if __name__=='__main__':
    main()
