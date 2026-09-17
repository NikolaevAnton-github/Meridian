"""MSQ-54 read-only source intake; run with factory-startup background Blender.

Writes diagnostics only under Saved/PlayerCharacter01/Datum16ShoulderIntake01/Worker.
No blend save, source edit, repair, provider call, or export operation is used.
"""
import array
import collections
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from io_scene_fbx import parse_fbx

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Saved/PlayerCharacter01/Datum16ShoulderIntake01/Worker"
SOURCE = ROOT / "Assets/Source/PlayerCharacter01/AI3D/Tripo/Datum16ShoulderManual01/OwnerExports/armor+shoulder+plate+3d+model.fbx"
EXPECTED = "c1be7d5f1e82b955c9367f5335e45f1e191177bf298ba0112eb9604575d65078"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def serial(value):
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="backslashreplace")
    if isinstance(value, array.array):
        return {"type": value.typecode, "length": len(value), "head": list(value[:12])}
    return value


def element(elem):
    return {"id": serial(elem.id), "props": [serial(p) for p in elem.props],
            "children": [element(e) for e in elem.elems]}


def bounds(points):
    low = [min(p[i] for p in points) for i in range(3)]
    high = [max(p[i] for p in points) for i in range(3)]
    return {"min": low, "max": high, "size": [b-a for a,b in zip(low, high)]}


def geometry_digest(mesh):
    data = {"vertices": [list(v.co) for v in mesh.vertices],
            "edges": [list(e.vertices) for e in mesh.edges],
            "polygons": [list(p.vertices) for p in mesh.polygons]}
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def inspect_mesh(obj):
    mesh = obj.data
    mesh.calc_loop_triangles()
    coords = [v.co.copy() for v in mesh.vertices]
    world = [obj.matrix_world @ co for co in coords]
    span = max(bounds(coords)["size"])
    eps = span * 1e-7
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    adjacency = [set() for _ in coords]
    for e in mesh.edges:
        a,b = e.vertices
        adjacency[a].add(b)
        adjacency[b].add(a)
    remaining = set(range(len(coords)))
    components = []
    while remaining:
        todo = [min(remaining)]
        remaining.remove(todo[0])
        connected = []
        while todo:
            index = todo.pop()
            connected.append(index)
            for neighbor in sorted(adjacency[index]):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    todo.append(neighbor)
        members = set(connected)
        faces = [p for p in mesh.polygons if p.vertices[0] in members]
        component_edges = [e for e in bm.edges if e.verts[0].index in members]
        components.append({"vertices": len(connected), "faces": len(faces),
                           "boundary_edges": sum(e.is_boundary for e in component_edges),
                           "bounds_local": bounds([coords[i] for i in connected])})
    boundary_remaining = {e.index for e in bm.edges if e.is_boundary}
    boundary_groups = []
    while boundary_remaining:
        todo = [min(boundary_remaining)]
        boundary_remaining.remove(todo[0])
        group = []
        while todo:
            ei = todo.pop()
            group.append(ei)
            for v in bm.edges[ei].verts:
                for edge in v.link_edges:
                    if edge.index in boundary_remaining:
                        boundary_remaining.remove(edge.index)
                        todo.append(edge.index)
        verts = {v.index for ei in group for v in bm.edges[ei].verts}
        degree = collections.Counter(v.index for ei in group for v in bm.edges[ei].verts)
        boundary_groups.append({"edges": sorted(group), "vertex_count": len(verts),
                                "closed_cycle": all(d == 2 for d in degree.values()),
                                "bounds_local": bounds([coords[i] for i in verts])})
    kd = KDTree(len(coords))
    for i, co in enumerate(coords):
        kd.insert(co, i)
    kd.balance()
    near_pairs = [(i,j) for i,co in enumerate(coords)
                  for _,j,d in kd.find_range(co, eps) if j > i]
    exact_counts = collections.Counter(tuple(co) for co in coords)
    face_counts = collections.Counter(tuple(sorted(p.vertices)) for p in mesh.polygons)
    position_faces = collections.Counter(tuple(sorted(tuple(coords[v]) for v in p.vertices))
                                        for p in mesh.polygons)
    winding = []
    for e in bm.edges:
        if len(e.link_faces) == 2 and not e.is_contiguous:
            winding.append(e.index)
    normals = [n.vector.copy() for n in mesh.corner_normals]
    corner_dots = [normals[li].dot(p.normal) for p in mesh.polygons for li in p.loop_indices]
    bvh = BVHTree.FromPolygons(coords, [list(t.vertices) for t in mesh.loop_triangles], all_triangles=True)
    # Finite samples: first hit along inward triangle normal. This is a
    # local chord measurement, not proof of wall thickness or self-intersection.
    chords = []
    misses = []
    for ti, tri in enumerate(mesh.loop_triangles):
        center = sum((coords[i] for i in tri.vertices), Vector()) / 3
        normal = tri.normal.copy()
        loc, hit_normal, hit_index, distance = bvh.ray_cast(center - normal * eps * 10, -normal, span*3)
        if loc is None:
            misses.append(ti)
        else:
            chords.append({"triangle": ti, "polygon": tri.polygon_index,
                           "hit_triangle": hit_index,
                           "same_polygon_hit": mesh.loop_triangles[hit_index].polygon_index == tri.polygon_index,
                           "distance": distance + eps*10,
                           "opposed_normal_dot": normal.dot(hit_normal)})
    distances = sorted(c["distance"] for c in chords)
    result = {
        "name": obj.name, "mesh": mesh.name, "geometry_sha256": geometry_digest(mesh),
        "vertices": len(mesh.vertices), "edges": len(mesh.edges), "faces": len(mesh.polygons),
        "triangles": sum(len(p.vertices)==3 for p in mesh.polygons),
        "quads": sum(len(p.vertices)==4 for p in mesh.polygons),
        "ngons": sum(len(p.vertices)>4 for p in mesh.polygons),
        "triangulated_count": len(mesh.loop_triangles), "components": components,
        "bounds_local": bounds(coords), "bounds_world": bounds(world),
        "boundary_edges": [e.index for e in bm.edges if e.is_boundary],
        "boundary_groups": boundary_groups,
        "wire_edges": [e.index for e in bm.edges if e.is_wire],
        "non_manifold_edges_including_boundary": [e.index for e in bm.edges if not e.is_manifold],
        "edges_over_two_faces": [e.index for e in bm.edges if len(e.link_faces)>2],
        "non_manifold_vertices": [v.index for v in bm.verts if not v.is_manifold],
        "inconsistent_winding_edges": winding,
        "duplicate_exact_vertex_excess": sum(n-1 for n in exact_counts.values()),
        "near_duplicate_vertex_pairs": near_pairs,
        "duplicate_index_face_excess": sum(n-1 for n in face_counts.values()),
        "duplicate_position_face_excess": sum(n-1 for n in position_faces.values()),
        "epsilon_local": eps,
        "degenerate_edges": [e.index for e in bm.edges if e.calc_length() <= eps],
        "degenerate_faces": [p.index for p in mesh.polygons if p.area <= eps*eps],
        "degenerate_loop_triangles": [i for i,t in enumerate(mesh.loop_triangles) if t.area <= eps*eps],
        "repeated_vertex_faces": [p.index for p in mesh.polygons if len(set(p.vertices)) != len(p.vertices)],
        "signed_volume_local": bm.calc_volume(signed=True),
        "surface_area_local": sum(p.area for p in mesh.polygons),
        "euler_characteristic": len(mesh.vertices)-len(mesh.edges)+len(mesh.polygons),
        "has_custom_normals": mesh.has_custom_normals,
        "smooth_faces": sum(p.use_smooth for p in mesh.polygons),
        "normal_lengths_min_max": [min(n.length for n in normals),max(n.length for n in normals)],
        "corner_face_dot_min_max": [min(corner_dots),max(corner_dots)],
        "opposed_corner_normals": sum(d < 0 for d in corner_dots),
        "opposed_corner_faces": [p.index for p in mesh.polygons if any(normals[li].dot(p.normal)<0 for li in p.loop_indices)],
        "uv_layers": [{"name": uv.name, "loops": len(uv.data),
                       "min": [min(d.uv[i] for d in uv.data) for i in range(2)],
                       "max": [max(d.uv[i] for d in uv.data) for i in range(2)]}
                      for uv in mesh.uv_layers],
        "attributes": [{"name": a.name, "domain": a.domain, "type": a.data_type} for a in mesh.attributes],
        "material_slots": [m.name if m else None for m in mesh.materials],
        "material_polygon_counts": dict(collections.Counter(p.material_index for p in mesh.polygons)),
        "inward_ray_chords": {"samples": len(mesh.loop_triangles), "hits": len(chords), "misses": misses,
            "same_polygon_hit_count": sum(c["same_polygon_hit"] for c in chords),
            "min_median_max": [distances[0],distances[len(distances)//2],distances[-1]] if distances else [],
            "opposed_hit_normal_count": sum(c["opposed_normal_dot"] < -0.5 for c in chords),
            "limitation": "Triangle-centroid first-hit inward-normal chord; bevels, concavity and oblique hits bias length. Same-polygon hits are flagged. Not guaranteed thickness.",
            "values": chords},
    }
    bm.free()
    return result


def main():
    assert bpy.app.background, "Background mode is required"
    assert sha(SOURCE) == EXPECTED and SOURCE.stat().st_size == 134960
    OUT.mkdir(parents=True, exist_ok=True)
    # Capture preservation identities before any DCC operation.
    protected = list((ROOT / "Assets/Source/PlayerCharacter01/AI3D/Tripo/Datum16ShoulderManual01").rglob("*"))
    protected += [ROOT / "Assets/Concepts/PlayerCharacter01/Concept02/16.png", ROOT / "Config/DefaultEngine.ini"]
    before = {str(p.relative_to(ROOT)): sha(p) for p in protected if p.is_file()}
    raw, version = parse_fbx.parse(str(SOURCE))
    write("fbx-metadata.json", {"version": version, "tree": element(raw)})
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    prior_materials = set(bpy.data.materials)
    prior_images = set(bpy.data.images)
    options = dict(filepath=str(SOURCE), use_custom_normals=True, use_image_search=False,
                   use_anim=True, global_scale=1.0, bake_space_transform=False)
    outcome = bpy.ops.import_scene.fbx(**options)
    assert outcome == {"FINISHED"}
    objects = list(bpy.context.scene.objects)
    meshes = [o for o in objects if o.type == "MESH"]
    report = {
        "source": str(SOURCE.relative_to(ROOT)), "sha256": EXPECTED, "bytes": SOURCE.stat().st_size,
        "blender_version": bpy.app.version_string, "build_hash": serial(bpy.app.build_hash),
        "background": bpy.app.background, "autoexec_enabled": bpy.context.preferences.filepaths.use_scripts_auto_execute,
        "import_operator": "bpy.ops.import_scene.fbx", "import_options": options,
        "fbx_version": version,
        "scene_units": {"system": bpy.context.scene.unit_settings.system,
                        "scale_length": bpy.context.scene.unit_settings.scale_length},
        "objects": [{"name": o.name, "type": o.type, "parent": o.parent.name if o.parent else None,
                     "location": list(o.location), "rotation_euler": list(o.rotation_euler), "scale": list(o.scale),
                     "matrix_world": [list(row) for row in o.matrix_world],
                     "determinant": o.matrix_world.determinant(),
                     "modifiers": [m.type for m in o.modifiers], "vertex_groups": [g.name for g in o.vertex_groups],
                     "animation_data": bool(o.animation_data)} for o in objects],
        "meshes": [inspect_mesh(o) for o in meshes],
        "materials": [{"name": m.name, "diffuse_color": list(m.diffuse_color), "use_nodes": m.use_nodes,
                       "nodes": [n.bl_idname for n in m.node_tree.nodes] if m.node_tree else []}
                      for m in bpy.data.materials if m not in prior_materials],
        "images": [{"name": im.name, "filepath": im.filepath, "source": im.source,
                    "packed": bool(im.packed_file)} for im in bpy.data.images if im not in prior_images],
        "armatures": [{"name": a.name, "bones": len(a.bones)} for a in bpy.data.armatures],
        "actions": [a.name for a in bpy.data.actions],
        "shape_keys": [k.name for k in bpy.data.shape_keys],
    }
    write("geometry.json", report)
    all_points = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
    box = bounds(all_points)
    center = (Vector(box["min"]) + Vector(box["max"])) / 2
    diameter = Vector(box["size"]).length
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.display.shading.light = "STUDIO"
    scene.display.shading.studio_light = "paint.sl"
    scene.display.shading.color_type = "OBJECT"
    scene.display.shading.background_type = "WORLD"
    scene.world.color = (0.18, 0.18, 0.18)
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "BOTH"
    scene.display.shading.show_specular_highlight = True
    scene.display.render_aa = "32"
    for o in meshes:
        o.color = (0.55, 0.55, 0.55, 1)
    cam_data = bpy.data.cameras.new("DiagnosticCamera")
    cam = bpy.data.objects.new("DiagnosticCamera", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = diameter * 1.08
    cam_data.clip_start = diameter * 0.01
    cam_data.clip_end = diameter * 10
    # Temporary curves trace source polygon edges exactly, without triangulation
    # or source-mesh edits. They exist only for wire evidence and are never saved.
    edge_data = bpy.data.curves.new("DiagnosticEdges", "CURVE")
    edge_data.dimensions = "3D"
    edge_data.resolution_u = 1
    edge_data.bevel_depth = diameter * 0.00055
    edge_data.bevel_resolution = 0
    for o in meshes:
        for edge in o.data.edges:
            spline = edge_data.splines.new("POLY")
            spline.points.add(1)
            for point, vi in zip(spline.points, edge.vertices):
                co = o.matrix_world @ o.data.vertices[vi].co
                point.co = (*co, 1)
    edge_obj = bpy.data.objects.new("DiagnosticEdges", edge_data)
    scene.collection.objects.link(edge_obj)
    edge_obj.color = (0.015, 0.015, 0.015, 1)
    views = {"plus_x": (1,0,0), "minus_x": (-1,0,0), "plus_y": (0,1,0),
             "minus_y": (0,-1,0), "plus_z": (0,0,1), "minus_z": (0,0,-1),
             "oblique_a": (1,-1,0.65), "oblique_b": (-1,1,0.65)}
    cameras = []
    for name, direction in views.items():
        direction = Vector(direction).normalized()
        cam.location = center + direction * diameter * 3
        cam.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
        for wire in (False, True):
            edge_obj.hide_render = not wire
            filename = name + ("_wire.png" if wire else "_gray.png")
            scene.render.filepath = str(OUT / filename)
            bpy.ops.render.render(write_still=True)
        cameras.append({"name": name, "direction_from_center": list(direction),
                        "location": list(cam.location), "rotation_euler": list(cam.rotation_euler)})
    write("views.json", {"center": list(center), "ortho_scale": cam_data.ortho_scale,
                         "resolution": [1000,1000], "cameras": cameras,
                         "wire": "Temporary exact-edge curves, radius diagonal*0.00055; visible-surface overlay, not x-ray. No source edge changes."})
    after = {p: sha(ROOT / p) for p in before}
    geometry_after = {o.name: geometry_digest(o.data) for o in meshes}
    preserved = before == after and all(geometry_after[m["name"]] == m["geometry_sha256"] for m in report["meshes"])
    write("preservation.json", {"passed": preserved, "before": before, "after": after,
                                "mesh_geometry_after": geometry_after})
    assert preserved
    files = [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha(p)}
             for p in sorted(OUT.iterdir()) if p.is_file() and p.name != "evidence-manifest.json" and p.suffix != ".log"]
    write("evidence-manifest.json", {"files": files,
          "exclusions": "Manifest itself and logs (the current process log may still be growing).",
          "total_listed_bytes": sum(f["bytes"] for f in files)})
    assert sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file()) < 100_000_000
    print("INTAKE_COMPLETE", len(meshes), "mesh(es); preservation verified", flush=True)


if __name__ == "__main__":
    main()
