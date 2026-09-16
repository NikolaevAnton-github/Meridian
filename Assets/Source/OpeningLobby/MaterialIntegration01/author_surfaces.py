"""Fresh deterministic surface authoring. Inputs are this code and recipe.json only.

Run with the already installed D:/blender/5.2/python/bin/python.exe. This is a
standalone NumPy process: no bpy, Blender scene, render, external image or service.
PNG pixels are authored here, not transformed from any earlier project texture.
"""
import gc
import hashlib
import json
import math
import struct
import sys
import zlib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / 'Saved/OpeningLobby/MaterialIntegration01/WorkerFresh01'


def png(path, pixels):
    """Lossless RGB PNG, row-sub filter; no image manipulation dependency."""
    a = np.ascontiguousarray(np.clip(np.rint(pixels), 0, 255), dtype=np.uint8)
    h, w, channels = a.shape
    assert channels == 3
    encoded = np.empty((h, w * 3 + 1), dtype=np.uint8)
    encoded[:, 0] = 1
    sub = a.copy()
    sub[:, 1:] -= a[:, :-1]
    encoded[:, 1:] = sub.reshape(h, -1)
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    payload = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
    payload += chunk(b'IDAT', zlib.compress(encoded.tobytes(), 6)) + chunk(b'IEND', b'')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return dict(path=path.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(payload).hexdigest(),
                bytes=len(payload), dimensions=[w, h], min=a.min(axis=(0, 1)).tolist(),
                max=a.max(axis=(0, 1)).tolist(), mean=a.mean(axis=(0, 1)).tolist())


def lattice(n, cells, seed, xy=None):
    """Periodic smooth random scalar field, not a texture/image input."""
    cx, cy = (cells, cells) if isinstance(cells, int) else cells
    if xy is None:
        x = np.arange(n, dtype=np.float32)[None, :] / n
        y = np.arange(n, dtype=np.float32)[:, None] / n
    else:
        x, y = xy
    gx, gy = x * cx, y * cy
    ix, iy = np.floor(gx).astype(np.int32), np.floor(gy).astype(np.int32)
    fx, fy = gx - ix, gy - iy
    fx, fy = fx.astype(np.float32), fy.astype(np.float32)
    fx = fx * fx * fx * (fx * (fx * 6 - 15) + 10)
    fy = fy * fy * fy * (fy * (fy * 6 - 15) + 10)
    grid = np.random.default_rng(seed).uniform(-1, 1, (cy, cx)).astype(np.float32)
    top = grid[iy % cy, ix % cx] * (1 - fx) + grid[iy % cy, (ix + 1) % cx] * fx
    low = grid[(iy + 1) % cy, ix % cx] * (1 - fx) + grid[(iy + 1) % cy, (ix + 1) % cx] * fx
    return (top * (1 - fy) + low * fy).astype(np.float32)


def mineral(n, seed, wall=False):
    x = np.arange(n, dtype=np.float32)[None, :] / n + lattice(n, 7, seed + 1) * .022
    y = np.arange(n, dtype=np.float32)[:, None] / n + lattice(n, 9, seed + 2) * .019
    ground = lattice(n, 31 if wall else 38, seed + 3, (x, y)) * .32
    ground += lattice(n, 89 if wall else 107, seed + 4, (x, y)) * .28
    ground += lattice(n, 211, seed + 5, (x, y)) * .23
    ground += lattice(n, 493, seed + 6, (x, y)) * .14
    grains = lattice(n, 853, seed + 7)
    ground += grains * .06
    # Fine irregular intergrown light/dark grains fill the entire groundmass.
    crystal = np.maximum(lattice(n, (233, 397), seed + 8, (x, y)) - .18, 0) ** 1.4
    feldspar = lattice(n, 13, seed + 9, (x, y))
    base = np.array([58, 69, 62] if not wall else [61, 71, 65], dtype=np.float32)
    color = base + ground[..., None] * (34 if not wall else 27)
    color += feldspar[..., None] * np.array([5.2, 6.0, 4.1], dtype=np.float32)
    color += crystal[..., None] * np.array([16, 17, 14], dtype=np.float32)
    rough = (.355 if not wall else .405) + ground * .042 - crystal * .045
    height_cm = ground * .0015 + grains * .0004
    return color, rough, height_cm


def stamp_line(target, a, b, width, strength=1.):
    """Antialiased fracture segment on a periodic domain; no closed contour noise."""
    n = target.shape[0]
    ax, ay = a
    bx, by = b
    radius = width * 2.7 + 1.5
    xs = np.arange(math.floor(min(ax, bx) - radius), math.ceil(max(ax, bx) + radius) + 1)
    ys = np.arange(math.floor(min(ay, by) - radius), math.ceil(max(ay, by) + radius) + 1)
    xx, yy = xs[None, :] + .5, ys[:, None] + .5
    dx, dy = bx - ax, by - ay
    t = np.clip(((xx - ax) * dx + (yy - ay) * dy) / max(dx * dx + dy * dy, 1e-8), 0, 1)
    distance = np.sqrt((xx - ax - t * dx) ** 2 + (yy - ay - t * dy) ** 2)
    value = strength * (.83 * np.clip(width + .6 - distance, 0, 1) +
                        .17 * np.exp(-(distance / max(width * 2.1, .8)) ** 2))
    index = np.ix_(ys % n, xs % n)
    target[index] = np.maximum(target[index], value)


def fractures(n, seed):
    rng = np.random.default_rng(seed)
    mask = np.zeros((n, n), dtype=np.float32)
    skeleton = []
    # Through-going irregular calcite seams with attached tapering side branches.
    for main in range(9):
        offset = float(rng.random())
        slope = int(rng.choice([-1, 0, 1]))
        points = np.linspace(0, 1, 780, dtype=np.float32)
        xx = offset + slope * points
        phases = rng.uniform(0, math.tau, 5)
        for freq, amp, phase in zip([1, 3, 9, 23, 61], [.10, .047, .012, .0033, .001], phases):
            xx += amp * np.sin(points * math.tau * freq + phase)
        widths = (.9 + .7 * np.sin(points * math.tau * 4 + phases[0]) ** 2) * (n / 4096)
        for i in range(len(points) - 1):
            stamp_line(mask, (xx[i] * n, points[i] * n), (xx[i + 1] * n, points[i + 1] * n), float(widths[i]), .85)
        for branch in range(8):
            i = int(rng.integers(50, 720))
            origin = np.array([xx[i], points[i]], dtype=np.float32)
            length = float(rng.uniform(.045, .22))
            angle = float(rng.uniform(-2.7, 2.7))
            direction = np.array([math.cos(angle), math.sin(angle)], dtype=np.float32)
            side = np.array([-direction[1], direction[0]], dtype=np.float32)
            phase = float(rng.uniform(0, math.tau))
            previous = origin
            for step in range(1, 101):
                t = step / 100
                bend = math.sin(t * 11 + phase) * .007 * math.sin(math.pi * t)
                bend += math.sin(t * 59 + phase) * .001
                current = origin + direction * length * t + side * bend
                stamp_line(mask, previous * n, current * n, max(.3, (1 - t) * 1.1) * n / 4096, .62 * (1 - .45 * t))
                previous = current
            skeleton.append(dict(main=main, origin=origin.tolist(), length=length, angle=angle))
    return mask, skeleton


def floor(n, seed):
    x = np.arange(n, dtype=np.float32)[None, :] / n + lattice(n, 5, seed + 1) * .05
    y = np.arange(n, dtype=np.float32)[:, None] / n + lattice(n, 7, seed + 2) * .04
    mass = lattice(n, (15, 23), seed + 3, (x, y)) * .45
    mass += lattice(n, (41, 57), seed + 4, (x, y)) * .29
    mass += lattice(n, (109, 167), seed + 5, (x, y)) * .17
    mass += lattice(n, 379, seed + 6) * .09
    del x, y
    vein, skeleton = fractures(n, seed + 70)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'floor-fracture-skeleton.json').write_text(json.dumps(skeleton, indent=2))
    crystal = np.maximum(lattice(n, (191, 277), seed + 7) - .15, 0)
    vein *= .82 + lattice(n, 197, seed + 8) * .18
    color = np.array([65, 82, 70], dtype=np.float32) + mass[..., None] * np.array([36, 37, 31], dtype=np.float32)
    color += vein[..., None] * np.array([67, 66, 60], dtype=np.float32)
    color += crystal[..., None] * 7
    rough = .215 + mass * .017 - vein * .014 + crystal * .011
    height_cm = mass * .0006 + crystal * .00015 + vein * .00025
    return color, rough, height_cm


def strip(n, seed):
    # Fine dark aggregate with a few broken light inclusions; no large marble vein.
    grain = lattice(n, 551, seed)
    fleck = np.maximum(lattice(n, (337, 479), seed + 1) - .42, 0) ** 1.35
    body = lattice(n, 51, seed + 2)
    color = np.array([24, 31, 29], dtype=np.float32) + grain[..., None] * 4 + body[..., None] * 2
    color += fleck[..., None] * np.array([26, 29, 28], dtype=np.float32)
    rough = .235 + grain * .018 + fleck * .013
    return color, rough, grain * .0005


def ceiling(n, seed):
    # Quiet fine honed mineral finish, intentionally without veining.
    dust = lattice(n, 617, seed)
    clouds = lattice(n, 23, seed + 1)
    pores = np.maximum(-dust - .5, 0)
    color = np.array([77, 84, 79], dtype=np.float32) + dust[..., None] * 1.6 + clouds[..., None] * 2.0 - pores[..., None] * 3
    return color, .67 + dust * .017 + pores * .05, dust * .0008


def metal(n, seed, door=False):
    # Long, fine machining strokes, not mineral noise reused as a metal surface.
    brushes = lattice(n, (821, 7), seed)
    crossgrain = lattice(n, (697, 47), seed + 1)
    finish = lattice(n, (13, 37), seed + 2)
    base = [86, 98, 94] if door else [47, 56, 53]
    color = np.array(base, dtype=np.float32) + brushes[..., None] * 1.9 + finish[..., None] * 1.4
    rough = (.335 if door else .385) + brushes * .045 + crossgrain * .016 + finish * .009
    return color, rough, brushes * .00035 + crossgrain * .00012


def build(role, record):
    n, seed = record['size'], record['seed']
    method = record['method']
    if method == 'dense_mineral':
        color, rough, h = mineral(n, seed, role == 'Wall')
    elif method == 'branching_calcite':
        color, rough, h = floor(n, seed)
    elif method == 'fine_black_aggregate':
        color, rough, h = strip(n, seed)
    elif method == 'quiet_honed_finish':
        color, rough, h = ceiling(n, seed)
    else:
        color, rough, h = metal(n, seed, role == 'Door')
    directory = HERE / 'Textures'
    results = {'BaseColor': png(directory / f'T_MI01_{role}_BaseColor.png', color)}
    # A source-sheet thumbnail is evidence only, never an Unreal material input.
    step = max(1, n // 1024)
    png(OUT / 'SourceSheets' / f'{role}-basecolor.png', color[::step, ::step])
    del color
    orm = np.empty((n, n, 3), dtype=np.float32)
    orm[..., 0], orm[..., 1], orm[..., 2] = 255, np.clip(rough, .08, .85) * 255, record['metallic'] * 255
    results['ORM'] = png(directory / f'T_MI01_{role}_ORM.png', orm)
    del orm, rough
    cm_per_pixel = record['projection_cm'] / n
    du = (np.roll(h, -1, axis=1) - np.roll(h, 1, axis=1)) / (2 * cm_per_pixel)
    dv = (np.roll(h, -1, axis=0) - np.roll(h, 1, axis=0)) / (2 * cm_per_pixel)
    length = np.sqrt(1 + du * du + dv * dv)
    normal = np.stack((-du / length, -dv / length, 1 / length), axis=-1)
    results['Normal'] = png(directory / f'T_MI01_{role}_Normal.png', (normal * .5 + .5) * 255)
    report = dict(role=role, recipe=record, exports=results,
                  relief_range_mm=[float(h.min() * 10), float(h.max() * 10)],
                  normal_convention='DirectX, +G along projected +V; RG encodes negative height slopes; flip_green_channel=false',
                  max_normal_slope=float(np.sqrt(du * du + dv * dv).max()),
                  authoring_inputs=['Assets/Source/OpeningLobby/MaterialIntegration01/author_surfaces.py',
                                    'Assets/Source/OpeningLobby/MaterialIntegration01/recipe.json'],
                  images_read=[], dcc_contribution=False)
    del h, du, dv, length, normal
    gc.collect()
    return report


def main():
    recipe = json.loads((HERE / 'recipe.json').read_text())
    assert not (HERE / 'provenance.json').exists(), 'Fresh authoring is immutable once completed; use an explicitly named trial for revisions.'
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    for role, values in recipe['roles'].items():
        record = build(role, values)
        records.append(record)
        print(json.dumps(dict(role=role, exports_bytes=sum(e['bytes'] for e in record['exports'].values()))), flush=True)
    provenance = dict(authoring='New local procedural recipes, no image/old material inputs',
                      python=sys.version, numpy=np.__version__, roles=records,
                      recipe_sha256=hashlib.sha256((HERE / 'recipe.json').read_bytes()).hexdigest(),
                      generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (HERE / 'provenance.json').write_text(json.dumps(provenance, indent=2))


if __name__ == '__main__':
    main()
