"""Partition the existing convex facing meshes into real, matching ceramic shards."""
import importlib.util
import json
import math
from pathlib import Path

ROOT = Path('D:/devgames/MeridianSquad')
spec = importlib.util.spec_from_file_location('facing04', ROOT/'Assets/Source/DemoTiledColumn01/Correction04/generate.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
source = json.loads((ROOT/'Assets/Source/DemoTiledColumn01/Correction04/cladding.json').read_text(encoding='utf-8-sig'))
groups = []
for index, original in enumerate(source['meshes']):
    if original['area_cm2'] < 450:
        continue
    polygon = [(v[1], v[2]) for v in original['vertices'] if v[0] > 0]
    _, center = module.area_centroid(polygon)
    angle = .31 + (index % 7)*.12
    offset = [original['uvs'][0][i] - original['vertices'][0][i+1]/240. for i in range(2)]
    pieces = []
    for first, second in ((1,1),(1,-1),(-1,1),(-1,-1)):
        poly = polygon
        for sign, theta in ((first,angle),(second,angle+math.pi*.5)):
            ny, nz = sign*math.cos(theta), sign*math.sin(theta)
            poly = module.clip(poly,ny,nz,ny*center[0]+nz*center[1])
        mesh, y, z = module.make_mesh(poly,'impact_shard')
        for uv in mesh['uvs']:
            uv[0] += offset[0]
            uv[1] += offset[1]
        pieces.append(dict(mesh=mesh,offset=[0,y,z]))
    ratio = sum(p['mesh']['area_cm2'] for p in pieces)/original['area_cm2']
    assert .9998 < ratio < 1.0001
    groups.append(dict(source=f'/Game/Experiments/DemoTiledColumn01/Correction04/SM_Tile04_{index:03}',pieces=pieces))
out=ROOT/'Saved/DemoColumnExperiment08/ceramic.json'
assert not out.exists()
out.write_text(json.dumps(dict(groups=groups)),encoding='utf-8')
print(json.dumps(dict(mesh_variants=len(groups),shard_meshes=sum(len(g['pieces']) for g in groups))))
