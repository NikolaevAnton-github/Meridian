"""Revision 13: bounded concrete relief without accumulated profile distortion.

Rebuild from the original shared cells, retaining revision-08 body grouping and
size variation. A single moderate coordinate flow replaces the stacked rough
maps and sampled radial normalization that stretched undercuts into thin fins.
"""
import ast
import argparse
import functools
import json
import math

import angular_spalling as angular
import generate_progressive as g
import shape_spalling as shape
import varied_spalling as varied
from profile_spalling import core_uv
from rough_spalling import smooth_core_concrete

ROOT, SOURCE, LIMIT = varied.ROOT, varied.SOURCE, varied.LIMIT
REVISION = '13'
BAR_AXIS = 65.8
RADIAL_ALPHA = .8


@functools.lru_cache(maxsize=1100000)
def transform(p):
    if p[2] > 280.00001:
        return p
    result = list(varied.macro(angular.angular_map(angular.unwarp(p))))
    # Each step is monotone in the moved coordinate and fixes the envelope.
    # Limit the relief amplitude and slope instead of normalizing a folded
    # surface through its outermost radial intersection.
    if max(abs(result[0]), abs(result[1])) < LIMIT-1e-6:
        for k in range(3):
            center, limit = (140., 140.) if k == 2 else (0., LIMIT)
            value = result[k]-center
            if abs(value) >= limit-1e-8:
                continue
            a,b = result[(k+1)%3], result[(k+2)%3]
            if k == 2:
                fade = min(1., max(0., (LIMIT-max(abs(a),abs(b)))/10.))
                strength = .65
            else:
                fade = min(1., max(0., (LIMIT-abs(result[1-k]))/10.))
                fade *= min(1., max(0., (280-result[2])/16.))
                strength = 1.
            shift = (4.0*varied.noise2(a+19,b-31,34.,41+k*7)
                     +1.5*varied.noise2(a-37,b+13,13.,67+k*11)
                     +.35*varied.noise2(a+7,b+29,5.5,101+k*13))
            result[k] = center+limit*math.tanh(math.atanh(value/limit)
                                              +strength*fade*shift/limit)
    radius = max(abs(result[0]),abs(result[1]))
    if radius < LIMIT-1e-6:
        alpha = 1.-(1.-RADIAL_ALPHA)*min(1.,max(0.,(280-result[2])/16.))
        ratio = 1./(alpha+(1-alpha)*radius/LIMIT)
        result[0] *= ratio
        result[1] *= ratio
    return tuple(round(v,5) for v in result)


def rebuild_anchors(source, collision):
    tree = ast.parse((ROOT/'Scripts/ReinforcedColumn01/check_progression.py').read_text())
    context = dict(math=math, source=source, core_bins={})
    module = ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)
                             and n.name=='crossings'], type_ignores=[])
    exec(compile(module,'core-intersection','exec'),context)
    crossings = context['crossings']
    records = []
    for i,old in enumerate(source['anchors']):
        center = transform(g.mean(sorted(set(tuple(p) for p in old['vertices']))))
        for attempt in range(30):
            x,y,z = center[0]*.96**attempt, center[1]*.96**attempt, center[2]
            anchor = g.empty()
            for _,poly in g.box(x-.4,x+.4,y-.4,y+.4,z-.4,z+.4):
                g.append(anchor,g.surface(poly,2,rough=False))
            probes = set(tuple(p) for p in anchor['vertices'])
            probes.update([(x+s*.4,y,z) for s in (-1,1)])
            probes.update([(x,y+s*.4,z) for s in (-1,1)])
            probes.update([(x,y,z+s*.4) for s in (-1,1)])
            clearances = []
            for p in probes:
                hits = crossings(source['core'],0,1,p[1],p[2],900,240)
                if len(hits)<2 or len(hits)%2:
                    break
                clearance = max(min(120-p[0]-a,b-(120-p[0])) for a,b in zip(hits[::2],hits[1::2]))
                if clearance <= .15:
                    break
                clearances.append(clearance)
            else:
                break
        else:
            raise AssertionError(('Anchor containment',i))
        source['anchors'][i] = anchor
        collision['leaves'][644+i] = sorted(set(tuple(p) for p in anchor['vertices']))
        records.append(dict(anchor=i,center=[x,y,z],inward_steps=attempt,min_x_clearance_cm=min(clearances)))
    return records


def main():
    global REVISION, BAR_AXIS, RADIAL_ALPHA
    parser = argparse.ArgumentParser()
    parser.add_argument('--revision', choices=['12','13'], default='13')
    REVISION = parser.parse_args().revision
    BAR_AXIS, RADIAL_ALPHA = (79.8,1.) if REVISION=='12' else (65.8,.8)
    paths = [SOURCE/(name+REVISION+'.json') for name in ('column','collision','design')]
    assert not any(p.exists() for p in paths), 'Previous source revisions are immutable.'
    source = json.loads((SOURCE/'column04.json').read_text())
    original_design = json.loads((SOURCE/'design04.json').read_text())
    design = json.loads((SOURCE/'design08.json').read_text())
    collision = json.loads((SOURCE/'collision04.json').read_text())
    shape.transform = transform
    varied.transform_mesh(source['core'],900)
    for i,piece in enumerate(source['pieces']):
        varied.transform_mesh(piece)
        if i%100==0:
            print('Bounded relief',i,flush=True)
    groups = design['merge_groups']
    pieces = source['pieces']
    source['pieces'] = [angular.merge(pieces,members) for members in groups]
    remap = {old:i for i,group in enumerate(groups) for old in group}
    source['clusters'] = [sorted({remap[i] if i<644 else 480+i-644 for i in group}) for group in source['clusters']]
    smooth_core_concrete(source['core'])
    core_uv(source['core'])
    angular.BAR_AXIS = BAR_AXIS
    source['steel'] = angular.make_steel()
    source['preserve_static_meshes'] = False
    source.pop('previews',None)
    for leaf in collision['leaves'][:644]:
        for i,p in enumerate(leaf):
            leaf[i] = transform(tuple(p))
    anchors = rebuild_anchors(source,collision)
    meta = [dict(original_design['piece_meta'][min(group)],original_piece_ids=group) for group in groups]
    for row in meta:
        row['seed'] = transform(g.warp(row['seed']))
    silhouettes=[]
    for i,piece in enumerate(source['pieces']):
        axis = 0 if meta[i]['side']%2==0 else 1
        points=piece['vertices']
        width=max(p[axis] for p in points)-min(p[axis] for p in points)
        height=max(p[2] for p in points)-min(p[2] for p in points)
        silhouettes.append(dict(piece=i,width_cm=width,height_cm=height,aspect=max(width,height)/min(width,height)))
    design.update(revision=REVISION,source_revision='04',previous_revision='11',
        geometry_operation='Original shared cells with retained size redistribution; bounded monotone relief and mild radial expansion; no sampled radial normalization',
        relief_shift_amplitudes_cm=[4.,1.5,.35],relief_axis_strengths=[1.,1.,.65],
        radial_expansion_alpha=RADIAL_ALPHA,
        steel_preserved=False,longitudinal_axis_offset_cm=BAR_AXIS,
        reinforcement_additional_inset_cm=89.8-BAR_AXIS,
        longitudinal_diameter_cm=2.8,tie_diameter_cm=1.2,tie_spacing_cm=20,
        anchors_rebuilt=anchors,piece_meta=meta,silhouettes=silhouettes,
        core_uv='Continuous cylindrical concrete projection; planar caps finalized during import')
    for path,data in zip(paths,(source,collision,design)):
        path.write_text(json.dumps(data,indent=2) if path==paths[2] else json.dumps(data,separators=(',',':')),encoding='utf-8')
    print(json.dumps(dict(revision=REVISION,bodies=len(source['pieces']),anchors=len(source['anchors']),
        bar_axis_cm=BAR_AXIS,min_anchor_x_clearance_cm=min(r['min_x_clearance_cm'] for r in anchors))),flush=True)


if __name__=='__main__':
    main()
