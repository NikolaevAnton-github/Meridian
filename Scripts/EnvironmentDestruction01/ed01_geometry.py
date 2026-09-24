"""Deterministic editable ED-01 cell recipe; centimetres, column-local X/world Z."""
import json
import random
from pathlib import Path

def clip(poly, nx, nz, limit):
    out = []
    for p, q in zip(poly, poly[1:] + poly[:1]):
        dp, dq = p[0] * nx + p[1] * nz - limit, q[0] * nx + q[1] * nz - limit
        if dp <= 1e-9:
            out.append(p)
        if (dp < 0) != (dq < 0):
            t = dp / (dp - dq)
            out.append([p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])])
    return out

def recipe():
    rng = random.Random(14101)
    pieces = []
    for slab in range(2):
        left = -120 + slab * 120
        sites = [[left + (x + .5) * 30 + rng.uniform(-6, 6), (z + .5) * 60 + rng.uniform(-12, 12)]
                 for z in range(4) for x in range(4)]
        for site in sites:
            poly = [[left, 0], [left + 120, 0], [left + 120, 240], [left, 240]]
            for other in sites:
                if other != site:
                    nx, nz = other[0] - site[0], other[1] - site[1]
                    poly = clip(poly, nx, nz, (other[0] ** 2 + other[1] ** 2 - site[0] ** 2 - site[1] ** 2) / 2)
            cross = [p[0] * q[1] - q[0] * p[1] for p, q in zip(poly, poly[1:] + poly[:1])]
            area = sum(cross) / 2
            assert area > 100
            center = [sum((p[k] + q[k]) * c for p, q, c in zip(poly, poly[1:] + poly[:1], cross)) / (6 * area) for k in (0, 1)]
            pieces.append({'id': len(pieces), 'slab': slab, 'polygon_xz_cm': poly, 'centroid_xz_cm': center,
                           'area_cm2': area, 'mass_kg': area * 4 * .0026})
    assert abs(sum(p['area_cm2'] for p in pieces) - 240 * 240) < 1e-5
    return {'candidate': 'MSQ-141-Candidate01', 'seed': 14101, 'thickness_cm': 4,
            'source_actor': 'StaticMeshActor_35', 'column_origin_world_cm': [-1260, -240, 0],
            'face_local_y_cm': 120, 'course_world_z_cm': [0, 240],
            'density_kg_m3': 2600, 'support': 'Each cell independently bonded to intact backing',
            'pieces': pieces}

if __name__ == '__main__':
    path = Path(__file__).resolve().parents[2] / 'Assets/Source/EnvironmentDestruction01/MSQ-141-Candidate01/cladding-recipe.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        json.dump(recipe(), f, indent=2)
    print(str(path))
