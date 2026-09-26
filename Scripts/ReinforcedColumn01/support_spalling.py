"""Revision 10: place compact bond anchors safely inside the revision-09 core.

Do not deform tiny support cubes with the visual roughness field: large local
shear can invert their coarse triangles even when the continuous map is monotone.
"""
import ast
import json
import math

import generate_progressive as g
from varied_spalling import ROOT, SOURCE


def main():
    paths=[SOURCE/(name+'10.json') for name in ('column','collision','design')]
    assert not any(p.exists() for p in paths)
    source=json.loads((SOURCE/'column09.json').read_text())
    collision=json.loads((SOURCE/'collision09.json').read_text())
    design=json.loads((SOURCE/'design09.json').read_text())
    # Reuse the existing indexed core-intersection routine without running the
    # unrelated progression validator or its historical baseline assumptions.
    tree=ast.parse((ROOT/'Scripts/ReinforcedColumn01/check_progression.py').read_text())
    module=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='crossings'],type_ignores=[])
    context=dict(math=math,source=source,core_bins={})
    exec(compile(module,'core-intersection','exec'),context)
    crossings=context['crossings']
    records=[]
    for i,old in enumerate(source['anchors']):
        center=g.mean(sorted(set(tuple(p) for p in old['vertices'])))
        for attempt in range(25):
            x,y,z=center[0]*(.94**attempt),center[1]*(.94**attempt),center[2]
            anchor=g.empty()
            for _,poly in g.box(x-.4,x+.4,y-.4,y+.4,z-.4,z+.4):
                g.append(anchor,g.surface(poly,2,rough=False))
            clearances=[]
            for p in set(tuple(p) for p in anchor['vertices']):
                hits=crossings(source['core'],0,1,p[1],p[2],900,240)
                if len(hits)<2 or len(hits)%2:
                    break
                clearance=max(min(120-p[0]-a,b-(120-p[0])) for a,b in zip(hits[::2],hits[1::2]))
                if clearance<=.15:
                    break
                clearances.append(clearance)
            else:
                break
        else:
            raise AssertionError(('No contained anchor position',i,center))
        source['anchors'][i]=anchor
        collision['leaves'][644+i]=sorted(set(tuple(p) for p in anchor['vertices']))
        records.append(dict(anchor=i,center=[x,y,z],inward_steps=attempt,min_x_clearance_cm=min(clearances)))
    design.update(revision='10',source_revision='09',previous_revision='09',
        anchor_authoring='Rebuilt 0.8 cm cubes; indexed core containment for every corner and face center; inward correction only if needed',
        anchors_rebuilt=records)
    for path,data in zip(paths,(source,collision,design)):
        path.write_text(json.dumps(data,indent=2) if path==paths[2] else json.dumps(data,separators=(',',':')),encoding='utf-8')
    print(json.dumps(dict(revision='10',anchors=len(records),min_anchor_x_clearance_cm=min(r['min_x_clearance_cm'] for r in records),
        corrected_centers=sum(r['inward_steps']>0 for r in records),render_geometry='identical to revision 09 except hidden anchors')))


if __name__=='__main__':
    main()
