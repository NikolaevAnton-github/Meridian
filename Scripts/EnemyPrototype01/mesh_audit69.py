"""Measure the exported reuse source and a disposable forearm cap feasibility trial."""
import bpy
import bmesh
import json
import sys
from collections import Counter
from pathlib import Path
from mathutils import Vector

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT / 'Saved/CombatSlice01/EnemyPrototype01/Worker'
source = ROOT / 'Assets/Source/EnemyPrototype01/SKM_Manny_Simple_Export02.fbx'
bpy.ops.import_scene.fbx(filepath=str(source), use_anim=False)
rows = []
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH': continue
    if obj.name == 'Cube': continue
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    counts = Counter()
    for v in obj.data.vertices:
        if v.groups:
            group = max(v.groups, key=lambda g:g.weight)
            counts[obj.vertex_groups[group.group].name] += 1
    boundary = sum(e.is_boundary for e in bm.edges)
    nonmanifold = sum(not e.is_manifold for e in bm.edges)
    coords = [obj.matrix_world @ v.co for v in obj.data.vertices]
    rows.append(dict(name=obj.name, vertices=len(bm.verts), faces=len(bm.faces), boundary_edges=boundary,
                     nonmanifold_edges=nonmanifold, weighted_vertices_by_dominant_bone=dict(counts),
                     bounds_m=[[min(v[i] for v in coords) for i in range(3)], [max(v[i] for v in coords) for i in range(3)]]))
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.0001)
    rows[-1]['welded_boundary_edges'] = sum(e.is_boundary for e in bm.edges)
    rows[-1]['welded_nonmanifold_edges'] = sum(not e.is_manifold for e in bm.edges)
    bm.free()
armature = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
mesh = next(o for o in bpy.context.scene.objects if o.type == 'MESH' and o.name != 'Cube')
arm = armature.data.bones['lowerarm_l']
hand = armature.data.bones['hand_l']
start = mesh.matrix_world.inverted() @ armature.matrix_world @ arm.head_local
end = mesh.matrix_world.inverted() @ armature.matrix_world @ hand.head_local
normal = (end-start).normalized()
plane = start.lerp(end, .22)
bm = bmesh.new()
bm.from_mesh(mesh.data)
# Isolate the actual source skin influenced by the forearm/hand chain. This is
# a disposable topology diagnostic, not an accepted damage mesh or art edit.
allowed = {'lowerarm_l', 'lowerarm_twist_01_l', 'lowerarm_twist_02_l', 'hand_l'}
allowed.update(b.name for b in armature.data.bones if any(t in b.name for t in ['thumb','index','middle','ring','pinky']) and b.name.endswith('_l'))
keep = set()
for v in mesh.data.vertices:
    if any(mesh.vertex_groups[g.group].name in allowed and g.weight >= .1 for g in v.groups): keep.add(v.index)
bm.verts.ensure_lookup_table()
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.index not in keep], context='VERTS')
bmesh.ops.bisect_plane(bm, geom=list(bm.verts)+list(bm.edges)+list(bm.faces), dist=.00001,
                      plane_co=plane, plane_no=normal, clear_inner=True, clear_outer=False)
before = sum(e.is_boundary for e in bm.edges)
fill = bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=0)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
trial = dict(vertices=len(bm.verts), faces=len(bm.faces), open_edges_before=before,
             cap_faces=len(fill.get('faces', [])), boundary_edges_after=sum(e.is_boundary for e in bm.edges),
             nonmanifold_edges_after=sum(not e.is_manifold for e in bm.edges),
             volume_m3=abs(bm.calc_volume(signed=True) * mesh.matrix_world.to_3x3().determinant()))
bm.free()
result = dict(blender=bpy.app.version_string, source=str(source), meshes=rows, bones=len(armature.data.bones),
              forearm_trial=trial, limitation='Disposable topology calculation only. No saved severed asset, cap UV/material, skinning-transition or separated rigid-body runtime acceptance.')
path = OUT / 'mesh-topology-audit02.json'
assert not path.exists()
path.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
