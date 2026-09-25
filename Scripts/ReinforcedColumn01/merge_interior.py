"""Merge adjacent internal pieces while retaining exact visible revision-04 surfaces.

Only shared internal triangles are removed. Surface chips, core, reinforcement,
normals, UVs and all exposed fracture triangles retain their source values.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'Assets/Source/ReinforcedColumn01/ReinforcedColumn02-Candidate01'


def triangle_key(mesh, triangle):
    return tuple(sorted(tuple(mesh['vertices'][i]) for i in triangle[:3]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', type=int, default=480)
    parser.add_argument('--revision', default='05')
    args = parser.parse_args()
    assert args.revision.isdigit()
    output = SOURCE / ('column' + args.revision + '.json')
    design_path = SOURCE / ('design' + args.revision + '.json')
    assert not output.exists() and not design_path.exists()
    source = json.loads((SOURCE / 'column04.json').read_text())
    design = json.loads((SOURCE / 'design04.json').read_text())
    pieces = source['pieces']
    meta = design['piece_meta']
    groups = {i: {i} for i in range(len(pieces))}
    parent = list(range(len(pieces)))
    candidates = []
    for cluster in source['clusters']:
        members = [i for i in cluster if i < len(pieces) and meta[i]['layer'] > 0]
        faces = {}
        shared = collections.Counter()
        for i in members:
            for triangle in pieces[i]['triangles']:
                key = triangle_key(pieces[i], triangle)
                other = faces.pop(key, None)
                if other is None:
                    faces[key] = i
                else:
                    assert other != i
                    shared[tuple(sorted((i, other)))] += 1
        candidates.extend((-count, a, b) for (a, b), count in shared.items())
    # Prefer broad shared interfaces. Limit unions to three source pieces and
    # their original local support group so the new bodies remain local.
    def root(i):
        while parent[i] != i:
            i = parent[i]
        return i
    for _, a, b in sorted(candidates):
        a, b = root(a), root(b)
        if len(groups) <= args.target:
            break
        if a == b or len(groups[a]) + len(groups[b]) > 3:
            continue
        parent[b] = a
        groups[a].update(groups.pop(b))
    assert len(groups) == args.target, (len(groups), args.target)
    ordered = sorted(groups.values(), key=min)
    remap = {old: new for new, members in enumerate(ordered) for old in members}
    merged = []
    removed_triangles = 0
    for members in ordered:
        if len(members) == 1:
            merged.append(pieces[next(iter(members))])
            continue
        faces = {}
        for i in sorted(members):
            for triangle in pieces[i]['triangles']:
                key = triangle_key(pieces[i], triangle)
                if key in faces:
                    del faces[key]
                    removed_triangles += 2
                else:
                    faces[key] = (i, triangle)
        mesh = dict(vertices=[], normals=[], uvs=[], triangles=[])
        vertex_map = {}
        for i, triangle in faces.values():
            indices = []
            for v in triangle[:3]:
                if (i, v) not in vertex_map:
                    vertex_map[i, v] = len(mesh['vertices'])
                    for field in ['vertices', 'normals', 'uvs']:
                        mesh[field].append(pieces[i][field][v])
                indices.append(vertex_map[i, v])
            mesh['triangles'].append(indices + [triangle[3]])
        merged.append(mesh)
    for i, row in enumerate(meta):
        if row['layer'] == 0:
            assert ordered[remap[i]] == {i}
            assert merged[remap[i]] == pieces[i]
    source['clusters'] = [sorted({remap[i] if i < len(pieces) else len(merged) + i - len(pieces) for i in cluster}) for cluster in source['clusters']]
    for preview in source['previews']:
        old_removed = set(preview['removed'])
        preview['removed'] = [i for i, members in enumerate(ordered) if members <= old_removed]
        preview['pieces'] = [i for i in range(len(merged)) if i not in set(preview['removed'])]
    source['pieces'] = merged
    source['preserve_static_meshes'] = True
    design.update(dynamic_bodies=len(merged), fragment_triangles=sum(len(m['triangles']) for m in merged),
        source_revision='04', original_dynamic_bodies=len(pieces), removed_internal_triangles=removed_triangles,
        surface_pieces_preserved=sum(row['layer'] == 0 for row in meta),
        merge_groups=[sorted(g) for g in ordered],
        piece_meta=[dict(meta[min(g)], original_piece_ids=sorted(g)) for g in ordered],
        previews=[{k:v for k,v in p.items() if k != 'pieces'} for p in source['previews']],
        source_sha256=hashlib.sha256((SOURCE/'column04.json').read_bytes()).hexdigest())
    output.write_text(json.dumps(source,separators=(',',':')))
    design_path.write_text(json.dumps(design,indent=2))
    print(json.dumps(dict(dynamic_bodies=len(merged),surface_pieces_preserved=design['surface_pieces_preserved'],
        merged_groups=sum(len(g)>1 for g in ordered), removed_internal_triangles=removed_triangles,
        fragment_triangles=design['fragment_triangles'], bytes=output.stat().st_size)))


if __name__ == '__main__':
    main()
