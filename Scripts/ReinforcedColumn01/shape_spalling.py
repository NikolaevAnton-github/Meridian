"""Derive a thicker, irregular retained core and matching concrete flakes.

The shared radial map is strictly increasing along every square-section ray.
It fixes the cladding, leaves the steel and upper architecture unchanged, and
transforms every matching fragment/core interface together. No new bodies.
"""
import argparse
import functools
import hashlib
import json
import math
from pathlib import Path

import generate_progressive as g

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'Assets/Source/ReinforcedColumn01/ReinforcedColumn02-Candidate01'
LIMIT = 118.2


def lattice(x, y, z):
    n = (x * 374761393 + y * 668265263 + z * 2147483647 + 15604) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffffff) / 8388607.5 - 1.0


def noise(x, y, z, scale):
    q = [v / scale for v in (x, y, z)]
    lo = [math.floor(v) for v in q]
    t = [v - i for v, i in zip(q, lo)]
    # Linear interpolation deliberately keeps small changes of slope in the
    # fracture relief instead of rounding every exposed concrete feature.
    return sum(lattice(lo[0]+a, lo[1]+b, lo[2]+c)
               * (t[0] if a else 1-t[0]) * (t[1] if b else 1-t[1])
               * (t[2] if c else 1-t[2])
               for a in (0, 1) for b in (0, 1) for c in (0, 1))


def raw_transform(p):
    x, y, z = p
    radius = max(abs(x), abs(y))
    if radius >= LIMIT - 1e-7 or radius < 1e-8 or z > 280.00001:
        return p
    qx, qy = x * LIMIT / radius, y * LIMIT / radius
    # Typical core depth becomes 5-18 cm, with local deeper pockets. Large
    # concrete shoulders cross the rod plane; small relief breaks their rims.
    field = (2.9 * noise(qx+13, qy-29, z+17, 62.)
             + .95 * noise(qx-31, qy+11, z+37, 23.)
             + .28 * noise(qx+7, qy+19, z-13, 9.))
    alpha = math.exp(-2.35 + field)
    r = radius / LIMIT
    ratio = 1. / (alpha + (1. - alpha) * r)
    return (x*ratio, y*ratio, z)


@functools.lru_cache(maxsize=900000)
def transform(p):
    result = raw_transform(p)
    if result == p:
        return p
    return (round(result[0], 5), round(result[1], 5), p[2])


def transform_mesh(mesh, z_offset=0):
    original = mesh['vertices']
    mapped = [transform((p[0], p[1], round(p[2]+z_offset, 5))) for p in original]
    mesh['vertices'] = [[p[0], p[1], round(p[2]-z_offset, 5)] for p in mapped]
    normals = [[0., 0., 0.] for _ in mapped]
    smallest_area = float('inf')
    for a, b, c, material in mesh['triangles']:
        normal = g.cross(g.sub(mapped[b], mapped[a]), g.sub(mapped[c], mapped[a]))
        smallest_area = min(smallest_area, g.length(normal) * .5)
        for i in (a, b, c):
            for axis in range(3):
                normals[i][axis] += normal[axis]
    mesh['normals'] = [list(g.key(g.unit(n))) for n in normals]
    # Preserve exact shading and UVs for unchanged outer/stone vertices.
    assert smallest_area > 0, smallest_area
    return smallest_area


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--revision', default='06')
    args = parser.parse_args()
    assert args.revision.isdigit()
    output = SOURCE / ('column'+args.revision+'.json')
    design_path = SOURCE / ('design'+args.revision+'.json')
    collision_path = SOURCE / ('collision'+args.revision+'.json')
    assert not any(p.exists() for p in (output, design_path, collision_path))
    source_path = SOURCE/'column05.json'
    source = json.loads(source_path.read_text())
    design = json.loads((SOURCE/'design05.json').read_text())
    old_normals = source['core']['normals']
    old_vertices = source['core']['vertices']
    transform_mesh(source['core'], 900)
    for i, (before, after) in enumerate(zip(old_vertices, source['core']['vertices'])):
        if before == after:
            source['core']['normals'][i] = old_normals[i]
    for i, mesh in enumerate(source['pieces'] + source['anchors']):
        old_normals, old_vertices = mesh['normals'], mesh['vertices']
        transform_mesh(mesh)
        for j, (before, after) in enumerate(zip(old_vertices, mesh['vertices'])):
            if before == after:
                mesh['normals'][j] = old_normals[j]
        if i % 80 == 0:
            print('Reshaped', i, flush=True)
    source['preserve_static_meshes'] = False
    collision = json.loads((SOURCE/'collision04.json').read_text())
    # Preserve the 644->480 mapping, transforming its original sparse hulls
    # through the exact same map. The native union adapter takes convex envelopes.
    for leaf in collision['leaves']:
        for i, p in enumerate(leaf):
            leaf[i] = transform(tuple(p))
    design.update(revision=args.revision, source_revision='05',
        source_sha256=hashlib.sha256(source_path.read_bytes()).hexdigest(),
        geometry_operation='Shared monotone square-radial depth compression with multiscale angular relief',
        radial_alpha='exp(-2.35 + 2.9*N62 + 0.95*N23 + 0.28*N9)',
        collision_source='collision04 sparse hull points transformed with the same map and original design05 merge groups',
        core_triangles=len(source['core']['triangles']),
        fragment_triangles=sum(len(m['triangles']) for m in source['pieces']),
        steel_preserved=True, outer_cladding_preserved=True)
    design['source_seed_layers_cm'] = design.pop('seed_layers_cm')
    design['source_roughness_max_displacement_per_axis_cm'] = design.pop('roughness_max_displacement_per_axis_cm')
    design['warp'] = 'Revision-04 fracture flow followed by monotone square-radial spalling map'
    for row in design.get('piece_meta', []):
        if 'seed' in row:
            row['seed'] = transform(tuple(row['seed']))
    output.write_text(json.dumps(source, separators=(',', ':')), encoding='utf-8')
    collision_path.write_text(json.dumps(collision, separators=(',', ':')), encoding='utf-8')
    design_path.write_text(json.dumps(design, indent=2), encoding='utf-8')
    print(json.dumps(dict(source=str(output), bytes=output.stat().st_size,
                          dynamic_bodies=len(source['pieces']), anchors=len(source['anchors']),
                          core_triangles=design['core_triangles'], fragments=design['fragment_triangles'])))


if __name__ == '__main__':
    main()
