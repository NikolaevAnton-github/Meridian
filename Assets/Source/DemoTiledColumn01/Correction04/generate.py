"""Deterministic, world-centimetre cladding for the scale-1 demo column.

Coarse Voronoi regions and locally clustered sites give unequal convex fragments.
Small triangular corner chips are a second partition, not cosmetic triangles laid
over the larger pieces. Only the 5 mm panel joints should read before destruction.
This script is offline and writes only the adjacent cladding.json.
"""

import json
import math
import random
from pathlib import Path


OUT = Path(__file__).resolve().parent
SEED = 26092804
PANEL_WIDTH = 120.0
JOINT_HALF = 0.25
THICKNESS = 1.8
FACE_CENTER = 119.1
CORE_FACE = 118.2
TEXTURE_BASIS = 240.0
SEAM_SCALE = 0.99998
MATERIAL_ROOT = "/Game/Experiments/DemoTiledColumn01/Correction02/"


def cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def area_centroid(poly):
    twice_area = cy = cz = 0.0
    for a, b in zip(poly, poly[1:] + poly[:1]):
        det = a[0] * b[1] - b[0] * a[1]
        twice_area += det
        cy += (a[0] + b[0]) * det
        cz += (a[1] + b[1]) * det
    assert twice_area > 1.0e-7
    return twice_area * 0.5, (cy / (3.0 * twice_area), cz / (3.0 * twice_area))


def span(poly):
    return max(math.dist(a, b) for a in poly for b in poly)


def clean_polygon(poly):
    result = []
    for point in poly:
        if not result or math.dist(point, result[-1]) > 1.0e-7:
            result.append(point)
    if len(result) > 1 and math.dist(result[0], result[-1]) < 1.0e-7:
        result.pop()
    while len(result) > 3:
        index = next((i for i in range(len(result))
                      if abs(cross(result[i - 1], result[i], result[(i + 1) % len(result)])) < 1.0e-7), None)
        if index is None:
            break
        result.pop(index)
    return result


def clip(poly, ny, nz, offset):
    result = []
    for a, b in zip(poly, poly[1:] + poly[:1]):
        da = ny * a[0] + nz * a[1] - offset
        db = ny * b[0] + nz * b[1] - offset
        if da <= 1.0e-8:
            result.append(a)
        if (da < -1.0e-8 and db > 1.0e-8) or (da > 1.0e-8 and db < -1.0e-8):
            t = da / (da - db)
            result.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    return clean_polygon(result)


def voronoi(sites, height):
    polygons = []
    for i, a in enumerate(sites):
        poly = [(JOINT_HALF, JOINT_HALF), (PANEL_WIDTH - JOINT_HALF, JOINT_HALF),
                (PANEL_WIDTH - JOINT_HALF, height - JOINT_HALF), (JOINT_HALF, height - JOINT_HALF)]
        for j, b in enumerate(sites):
            if i != j:
                poly = clip(poly, b[0] - a[0], b[1] - a[1],
                            (b[0] ** 2 + b[1] ** 2 - a[0] ** 2 - a[1] ** 2) * 0.5)
        assert len(poly) >= 3
        polygons.append(poly)
    return polygons


def uneven_sites(rng, height):
    coarse_count = 10 if height == 240 else 5
    sites = []
    for _ in range(coarse_count):
        # Best-of-random spacing creates broad regions without a regular grid.
        candidates = [(rng.uniform(8.0, 112.0), rng.uniform(8.0, height - 8.0)) for _ in range(24)]
        point = max(candidates, key=lambda p: min((math.dist(p, q) for q in sites), default=1.0))
        sites.append(point)
    interior = sorted(sites, key=lambda p: min(p[0], PANEL_WIDTH - p[0], p[1], height - p[1]), reverse=True)
    for center in interior[:2 if height == 240 else 1]:
        angle = rng.uniform(0.0, math.tau)
        radius = rng.uniform(10.0, 20.0)
        for i in range(3):
            phi = angle + i * math.tau / 3.0 + rng.uniform(-0.18, 0.18)
            r = radius * rng.uniform(0.8, 1.2)
            sites.append((min(117.0, max(3.0, center[0] + math.cos(phi) * r)),
                          min(height - 3.0, max(3.0, center[1] + math.sin(phi) * r))))
    return sites


def choose_regions(rng, height):
    best = None
    for _ in range(96):
        polygons = voronoi(uneven_sites(rng, height), height)
        spans = [span(p) for p in polygons]
        areas = [area_centroid(p)[0] for p in polygons]
        medium_count = sum(15.0 <= d <= 38.0 for d in spans)
        target_medium = 4 if height == 240 else 2
        score = (sum(max(0.0, d - 85.0) ** 2 for d in spans)
                 + max(0, target_medium - medium_count) * 400.0
                 + sum(max(0.0, 0.18 - a / (d * d)) * 5000.0 for a, d in zip(areas, spans)))
        if best is None or score < best[0]:
            best = score, polygons
    return best[1]


def carve_chip(poly, target_span, rng):
    indices = list(range(len(poly)))
    rng.shuffle(indices)
    old_area = area_centroid(poly)[0]
    for i in indices:
        corner, previous, following = poly[i], poly[i - 1], poly[(i + 1) % len(poly)]
        la, lb = math.dist(corner, previous), math.dist(corner, following)
        wa, wb = rng.uniform(0.8, 1.2), rng.uniform(0.8, 1.2)
        va = ((previous[0] - corner[0]) / la * wa, (previous[1] - corner[1]) / la * wa)
        vb = ((following[0] - corner[0]) / lb * wb, (following[1] - corner[1]) / lb * wb)
        scale = target_span / max(wa, wb, math.dist(va, vb))
        if scale * wa > la * 0.6 or scale * wb > lb * 0.6:
            continue
        a = (corner[0] + scale * va[0], corner[1] + scale * va[1])
        b = (corner[0] + scale * vb[0], corner[1] + scale * vb[1])
        chip = [a, corner, b]
        chip_area = area_centroid(chip)[0]
        if chip_area < target_span ** 2 * 0.13 or chip_area > old_area * 0.25:
            continue
        remainder = clean_polygon(poly[:i] + [a, b] + poly[i + 1:])
        return remainder, chip
    return None


def make_layout(height, variant):
    rng = random.Random(SEED + height * 100 + variant)
    regions = choose_regions(rng, height)
    chips = []
    for _ in range(10 if height == 240 else 5):
        target = rng.uniform(5.2, 12.0)
        choices = list(range(len(regions)))
        rng.shuffle(choices)
        for index in choices:
            result = carve_chip(regions[index], target, rng)
            if result:
                regions[index], chip = result
                chips.append(chip)
                break
        else:
            raise AssertionError("Could not carve a well-shaped chip")
    pieces = [(p, "voronoi") for p in regions] + [(p, "small_chip") for p in chips]
    expected_area = (PANEL_WIDTH - 2.0 * JOINT_HALF) * (height - 2.0 * JOINT_HALF)
    assert abs(sum(area_centroid(p)[0] for p, _ in pieces) - expected_area) < 1.0e-5
    for p, kind in pieces:
        assert all(cross(p[i - 1], p[i], p[(i + 1) % len(p)]) > 1.0e-8 for i in range(len(p)))
        assert all(JOINT_HALF - 1.0e-7 <= y <= PANEL_WIDTH - JOINT_HALF + 1.0e-7
                   and JOINT_HALF - 1.0e-7 <= z <= height - JOINT_HALF + 1.0e-7 for y, z in p)
        if kind == "small_chip":
            assert len(p) == 3 and 5.0 <= span(p) <= 12.000001
    return pieces


def make_mesh(poly, kind):
    _, center = area_centroid(poly)
    cy, cz = center
    poly = [(cy + (y - cy) * SEAM_SCALE, cz + (z - cz) * SEAM_SCALE) for y, z in poly]
    n = len(poly)
    vertices = [[x, y - cy, z - cz] for x in (THICKNESS * 0.5, -THICKNESS * 0.5) for y, z in poly]
    uvs = [[y / TEXTURE_BASIS, z / TEXTURE_BASIS] for _ in range(2) for y, z in poly]
    triangles = []
    for i in range(1, n - 1):
        triangles.extend([[0, i, i + 1, 0], [n, n + i + 1, n + i, 1]])
    for i in range(n):
        j = (i + 1) % n
        triangles.extend([[i, n + i, n + j, 1], [i, n + j, j, 1]])
    mesh = dict(vertices=vertices, triangles=triangles, uvs=uvs,
                area_cm2=area_centroid(poly)[0], radius_cm=max(math.dist(p, center) for p in poly),
                span_cm=span(poly), fragment_kind=kind)
    return mesh, cy, cz


def rotate(x, y, z, face):
    return ([x, y, z], [-y, x, z], [-x, -y, z], [y, -x, z])[face]


def quantiles(values):
    values = sorted(values)
    result = {}
    for percent in (0, 10, 25, 50, 75, 90, 100):
        index = (len(values) - 1) * percent / 100.0
        lo = int(index)
        hi = min(lo + 1, len(values) - 1)
        result[str(percent)] = round(values[lo] + (values[hi] - values[lo]) * (index - lo), 3)
    return result


def main():
    meshes, layouts, tiles = [], {}, []
    for height in (240, 120):
        for variant in range(4):
            layout = []
            for poly, kind in make_layout(height, variant):
                mesh, cy, cz = make_mesh(poly, kind)
                layout.append((len(meshes), cy, cz))
                meshes.append(mesh)
            layouts[height, variant] = layout
    for face in range(4):
        for row in range(8):
            for col in range(2):
                height = 120 if row == 7 else 240
                variant = (face + row + col) % 4
                for mesh_index, cy, cz in layouts[height, variant]:
                    y, z = -120.0 + col * 120.0 + cy, row * 240.0 + cz
                    mesh = meshes[mesh_index]
                    tiles.append(dict(mesh=mesh_index, position=rotate(FACE_CENTER, y, z, face), yaw=face * 90,
                                      sample=rotate(CORE_FACE, y, z, face), bonded=(len(tiles) + row + face) % 3 == 0,
                                      area_cm2=mesh["area_cm2"], radius_cm=mesh["radius_cm"], span_cm=mesh["span_cm"],
                                      panel=[face, row, col], fragment_kind=mesh["fragment_kind"]))
    assert len(meshes) == 156 and len(tiles) == 1560
    summary = dict(mesh_variants=len(meshes), tiles=len(tiles),
                   small_triangular_chips=sum(t["fragment_kind"] == "small_chip" for t in tiles),
                   size_cm=[240, 240, 1800], area_quantiles_cm2=quantiles([t["area_cm2"] for t in tiles]),
                   span_quantiles_cm=quantiles([t["span_cm"] for t in tiles]),
                   span_counts={"5_to_12_cm": sum(5 <= t["span_cm"] <= 12 for t in tiles),
                                "15_to_35_cm": sum(15 <= t["span_cm"] <= 35 for t in tiles),
                                "40_to_80_cm": sum(40 <= t["span_cm"] <= 80 for t in tiles),
                                "above_80_cm": sum(t["span_cm"] > 80 for t in tiles)})
    source = dict(meshes=meshes, tiles=tiles,
                  materials=[MATERIAL_ROOT + "M_StoneUV02"] + [MATERIAL_ROOT + "M_StoneEdge02"] * 3,
                  metadata=dict(seed=SEED, coordinate_space="world_centimetres_actor_scale_1",
                                core_width_cm=236.4, thickness_cm=THICKNESS, front_plane_cm=120,
                                panel_joint_cm=0.5, fracture_seam_scale=SEAM_SCALE,
                                texture_basis_cm=TEXTURE_BASIS, summary=summary))
    (OUT / "cladding.json").write_text(json.dumps(source, separators=(",", ":"), allow_nan=False), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
