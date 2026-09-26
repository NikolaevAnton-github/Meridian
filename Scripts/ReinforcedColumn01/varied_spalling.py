"""Revision 08: varied angular fragments and deeply irregular concrete interfaces.

Shared monotone coordinate flows preserve mating surfaces and the column envelope.
Surface unions use real shared faces; balancing interior splits retain 480 bodies.
"""
import collections
import functools
import itertools
import json
import math
from pathlib import Path

import angular_spalling as angular
import generate_progressive as g
import shape_spalling as shape

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'Assets/Source/ReinforcedColumn01/ReinforcedColumn02-Candidate01'
LIMIT = 118.2


def distribution(value, lo, hi, amplitude, phase):
    if value <= lo or value >= hi:
        return value
    t = (value-lo)/(hi-lo)
    # Derivative is 1 + amplitude*cos(...), strictly positive. Two broad
    # regions of compression/stretch change cell size without adding bodies.
    w = 4*math.pi
    return lo+(hi-lo)*(t+amplitude*(math.sin(w*t+phase)-math.sin(phase))/w)


def macro(p):
    x,y,z = p
    if z > 280.00001:
        return p
    fade = min(1., max(0., (280-z)/35.))
    x += fade*(distribution(x,-LIMIT,LIMIT,.76,.4)-x)
    y += fade*(distribution(y,-LIMIT,LIMIT,.69,2.1)-y)
    z = distribution(z,0.,280.,.72,1.3)
    return x,y,z


def noise2(a,b,scale,seed):
    a,b = a/scale,b/scale
    i,j = math.floor(a),math.floor(b)
    u,v = a-i,b-j
    # Linear interpolation gives broken mineral-like slopes, not soft waves.
    return ((shape.lattice(i,j,seed)*(1-u)+shape.lattice(i+1,j,seed)*u)*(1-v)
            +(shape.lattice(i,j+1,seed)*(1-u)+shape.lattice(i+1,j+1,seed)*u)*v)


def roughen(p):
    if max(abs(p[0]),abs(p[1])) >= LIMIT-1e-6 or p[2] > 280.00001:
        return p
    result = list(p)
    for k in (0,1,2):
        center,limit = (140.,140.) if k==2 else (0.,LIMIT)
        value = result[k]-center
        if abs(value) >= limit-1e-8:
            continue
        a,b = result[(k+1)%3],result[(k+2)%3]
        if k == 2:
            skin_fade = min(1.,max(0.,(LIMIT-max(abs(a),abs(b)))/7.))
            amplitude = 1.
        else:
            transverse = result[1-k]
            skin_fade = min(1.,max(0.,(LIMIT-abs(transverse))/7.))
            skin_fade *= min(1.,max(0.,(280-result[2])/12.))
            amplitude = 2.25
        shift = (6.8*noise2(a+19,b-31,34.,41+k*7)
                 +3.0*noise2(a-37,b+13,13.,67+k*11)
                 +1.05*noise2(a+7,b+29,5.5,101+k*13))
        # Each move is strictly monotone in its moved coordinate. The offset
        # depends only on the other two axes; composition cannot fold solids.
        result[k] = center+limit*math.tanh(math.atanh(value/limit)
                                          +amplitude*skin_fade*shift/limit)
    return result


@functools.lru_cache(maxsize=1100000)
def transform(p):
    if p[2] > 280.00001:
        return p
    return tuple(round(v,5) for v in roughen(macro(angular.angular_map(angular.unwarp(p)))))


def transform_mesh(mesh,z_offset=0):
    original_normals = mesh['normals']
    original_vertices = mesh['vertices']
    shape.transform_mesh(mesh,z_offset)
    for i,(before,after) in enumerate(zip(original_vertices,mesh['vertices'])):
        if before == after:
            mesh['normals'][i] = original_normals[i]
    # Restore world-aligned stone projection after tangential redistribution.
    # Each exterior surface owns its vertices, independently of fracture faces.
    for i in {i for t in mesh['triangles'] if t[3]==0 for i in t[:3]}:
        n = original_normals[i]
        u = g.unit(g.cross((0,0,1) if abs(n[2])<.9 else (0,1,0),n))
        v = g.cross(n,u)
        p = list(mesh['vertices'][i]); p[2] += z_offset
        mesh['uvs'][i] = [round(g.dot(p,u)/1000,7),round(g.dot(p,v)/1000,7)]


def adjacency(pieces,meta,clusters):
    shared = collections.Counter()
    for cluster in clusters:
        faces = {}
        for i in cluster:
            if i >= len(pieces) or meta[i]['layer'] != 0:
                continue
            for t in pieces[i]['triangles']:
                key = tuple(sorted(tuple(pieces[i]['vertices'][v]) for v in t[:3]))
                other = faces.pop(key,None)
                if other is None:
                    faces[key] = i
                elif other != i:
                    shared[tuple(sorted((i,other)))] += 1
    return {pair for pair,count in shared.items() if count >= 4}


def regroup(pieces,meta,clusters,old_groups):
    groups = [set(group) for group in old_groups]
    edges = adjacency(pieces,meta,clusters)
    bounds = {}
    for i,piece in enumerate(pieces):
        if meta[i]['layer'] != 0:
            continue
        axis = 0 if meta[i]['side']%2 == 0 else 1
        points = [piece['vertices'][j] for t in piece['triangles'] if t[3]==0 for j in t[:3]]
        if points:
            bounds[i] = (min(p[axis] for p in points),max(p[axis] for p in points),
                         min(p[2] for p in points),max(p[2] for p in points))
    merges = []
    surface_clusters = [c for c in clusters if meta[c[0]]['layer']==0]
    for ordinal,cluster in enumerate(surface_clusters):
        if ordinal%2:
            continue
        candidates = [group for group in groups if group <= set(cluster) and any(i in bounds for i in group)]
        kind = ('compact','horizontal','vertical')[(ordinal//2)%3]
        choices = []
        for count in (2,3):
            for combo in itertools.combinations(candidates,count):
                connected = {0}
                while True:
                    new = connected | {j for j in range(count) if any(
                        tuple(sorted((a,b))) in edges for k in connected for a in combo[k] for b in combo[j])}
                    if new == connected:
                        break
                    connected = new
                if len(connected) != count:
                    continue
                members = set().union(*combo)
                boxes = [bounds[i] for i in members if i in bounds]
                width = max(b[1] for b in boxes)-min(b[0] for b in boxes)
                height = max(b[3] for b in boxes)-min(b[2] for b in boxes)
                if max(width,height)>105 or min(width,height)<10:
                    continue
                target = 1. if kind=='compact' else 2.65 if kind=='horizontal' else 1/2.65
                score = abs(math.log(width/height/target)) + .55*abs(math.log(max(width,height)/76))
                choices.append((score,sorted(members),combo,width,height))
        if not choices:
            continue
        _,members,combo,width,height = min(choices,key=lambda c:(c[0],c[1]))
        for group in combo:
            groups.remove(group)
        groups.append(set(members))
        merges.append(dict(kind=kind,original_piece_ids=members,width_cm=width,height_cm=height))
    # Removing old two-piece interior unions supplies smaller concrete chunks.
    # Every original stone-only chip remains bonded to its concrete backing.
    splits = []
    for group in list(reversed(groups)):
        if len(groups)==480:
            break
        if len(group)==2 and all(meta[i]['layer']>0 for i in group):
            groups.remove(group)
            groups.extend({i} for i in sorted(group))
            splits.append(sorted(group))
    assert len(groups)==480, len(groups)
    return sorted([sorted(group) for group in groups],key=min),merges,splits


def main():
    paths = [SOURCE/(name+'08.json') for name in ('column','collision','design')]
    assert not any(p.exists() for p in paths), 'Previous source revisions are immutable.'
    source = json.loads((SOURCE/'column04.json').read_text())
    design = json.loads((SOURCE/'design04.json').read_text())
    previous = json.loads((SOURCE/'design07.json').read_text())
    shape.transform = transform
    transform_mesh(source['core'],900)
    for i,piece in enumerate(source['pieces']+source['anchors']):
        transform_mesh(piece)
        if i%80==0:
            print('Varied concrete',i,flush=True)
    pieces = source['pieces']
    groups,merges,splits = regroup(pieces,design['piece_meta'],source['clusters'],previous['merge_groups'])
    source['pieces'] = [angular.merge(pieces,members) for members in groups]
    remap = {old:i for i,group in enumerate(groups) for old in group}
    source['clusters'] = [sorted({remap[i] if i<644 else 480+i-644 for i in cluster}) for cluster in source['clusters']]
    source['steel'] = angular.make_steel()
    source['preserve_static_meshes'] = False
    source.pop('previews',None)
    collision = json.loads((SOURCE/'collision04.json').read_text())
    for leaf in collision['leaves']:
        for i,p in enumerate(leaf):
            leaf[i] = transform(tuple(p))
    piece_meta = []
    for group in groups:
        row = dict(design['piece_meta'][min(group)],original_piece_ids=group)
        row['seed'] = transform(tuple(g.warp(row['seed'])))
        piece_meta.append(row)
    # Authoring metrics describe the actual body silhouette on its source face.
    silhouettes = []
    for i,piece in enumerate(source['pieces']):
        axis = 0 if piece_meta[i]['side']%2==0 else 1
        p = piece['vertices']
        width = max(v[axis] for v in p)-min(v[axis] for v in p)
        height = max(v[2] for v in p)-min(v[2] for v in p)
        silhouettes.append(dict(piece=i,width_cm=width,height_cm=height,aspect=max(width,height)/min(width,height)))
    record = dict(revision='08',source_revision='04',previous_revision='07',units='centimetres',
        outer_cm=[240,240,1800],affected_height_cm=[0,280],stone_thickness_cm=1.8,
        geometry_operation='Monotone size redistribution, shared multiscale concrete relief, connected compact/elongated surface unions and balancing interior splits',
        relief_scales_cm=[34,13,5.5],relief_shift_amplitudes_cm=[6.8,3.,1.05],
        distribution_min_derivative=[.24,.31,.28],dynamic_bodies=480,original_dynamic_bodies=644,
        anchors=len(source['anchors']),merge_groups=groups,surface_unions=merges,interior_splits=splits,
        standalone_stone_chips=0,steel_preserved=True,longitudinal_axis_offset_cm=angular.BAR_AXIS,
        core_triangles=len(source['core']['triangles']),
        fragment_triangles=sum(len(p['triangles']) for p in source['pieces']),
        piece_meta=piece_meta,silhouettes=silhouettes)
    paths[0].write_text(json.dumps(source,separators=(',',':')),encoding='utf-8')
    paths[1].write_text(json.dumps(collision,separators=(',',':')),encoding='utf-8')
    paths[2].write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps(dict(revision='08',dynamic_bodies=480,anchors=len(source['anchors']),
        surface_unions=len(merges),interior_splits=len(splits),core_triangles=record['core_triangles'],
        fragment_triangles=record['fragment_triangles'],
        widths_cm=[min(r['width_cm'] for r in silhouettes),max(r['width_cm'] for r in silhouettes)],
        heights_cm=[min(r['height_cm'] for r in silhouettes),max(r['height_cm'] for r in silhouettes)],
        compact=sum(r['aspect']<1.5 for r in silhouettes),elongated=sum(r['aspect']>2 for r in silhouettes))),flush=True)


if __name__=='__main__':
    main()
