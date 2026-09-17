"""MSQ-54 bounded read-only body intake in factory-startup background Blender.

Run with --background --factory-startup --disable-autoexec --python this_file.
Uses the registered shoulder numerical helpers unchanged. Diagnostic curves and
cameras exist only in memory; source mesh, transforms, UVs and normals are untouched.
"""
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import shoulder_intake01 as helper
import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree
from io_scene_fbx import parse_fbx

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Saved/PlayerCharacter01/Datum16BodyIntake01/Worker"
PACKAGE = ROOT / "Assets/Source/PlayerCharacter01/AI3D/Tripo/Datum16UndersuitInput01"
SOURCE = PACKAGE / "OwnerExports/tactical+jumpsuit+3d+model.fbx"
EXPECTED = "fc6340b6f36c529f15dac48ef06dca37aa72a07134b873e9e564f0addc6fa196"


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def protected_hashes():
    files = []
    for directory in ("Assets/Source/PlayerCharacter01", "Assets/Concepts/PlayerCharacter01"):
        files.extend(p for p in (ROOT / directory).rglob("*") if p.is_file())
    files.extend(ROOT / p for p in ("Config/DefaultEngine.ini", "Scripts/PlayerCharacter01/shoulder_intake01.py"))
    return {str(p.relative_to(ROOT)): helper.sha(p) for p in files}


def main():
    assert bpy.app.background and not bpy.context.preferences.filepaths.use_scripts_auto_execute
    assert helper.sha(SOURCE) == EXPECTED and SOURCE.stat().st_size == 933904
    OUT.mkdir(parents=True, exist_ok=True)
    before = protected_hashes()
    if (OUT / "preservation-before.json").exists():
        assert before == json.loads((OUT / "preservation-before.json").read_text(encoding="utf-8")), "Preservation baseline changed"
    write("preservation-before.json", before)
    raw, version = parse_fbx.parse(str(SOURCE))
    write("fbx-metadata.json", {"version": version, "tree": helper.element(raw),
          "array_note": "Array type, length and first 12 values; exact complete arrays remain in untouched FBX."})
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    prior_materials, prior_images = set(bpy.data.materials), set(bpy.data.images)
    options = dict(filepath=str(SOURCE), use_custom_normals=True, use_image_search=False,
                   use_anim=True, global_scale=1.0, bake_space_transform=False)
    assert bpy.ops.import_scene.fbx(**options) == {"FINISHED"}
    objects = list(bpy.context.scene.objects)
    meshes = [o for o in objects if o.type == "MESH"]
    report = {
        "source": str(SOURCE.relative_to(ROOT)), "sha256": EXPECTED, "bytes": SOURCE.stat().st_size,
        "blender_version": bpy.app.version_string, "build_hash": helper.serial(bpy.app.build_hash),
        "background": bpy.app.background,
        "autoexec_enabled": bpy.context.preferences.filepaths.use_scripts_auto_execute,
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
        "meshes": [helper.inspect_mesh(o) for o in meshes],
        "materials": [{"name": m.name, "diffuse_color": list(m.diffuse_color), "use_nodes": m.use_nodes,
                       "nodes": [n.bl_idname for n in m.node_tree.nodes] if m.node_tree else []}
                      for m in bpy.data.materials if m not in prior_materials],
        "images": [{"name": im.name, "filepath": im.filepath, "source": im.source,
                    "packed": bool(im.packed_file)} for im in bpy.data.images if im not in prior_images],
        "armatures": [{"name": a.name, "bones": len(a.bones)} for a in bpy.data.armatures],
        "actions": [a.name for a in bpy.data.actions], "shape_keys": [k.name for k in bpy.data.shape_keys],
    }
    # Reused helper also computes inward chords. Retain them as diagnostic data,
    # but they are not interpreted as cloth thickness or self-intersection proof.
    points = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
    box = helper.bounds(points)
    regional = {}
    def region(co):
        z = (co.z-box["min"][2])/box["size"][2]
        if z < .145:
            return "boot_ankle_x_positive" if co.x > 0 else "boot_ankle_x_negative"
        if z < .60:
            return "trousers_hips"
        if abs(co.x) > .38*max(box["size"]):
            return "hand_cuff_x_positive" if co.x > 0 else "hand_cuff_x_negative"
        if z > .84:
            return "head_collar"
        return "torso_sleeves"
    for obj, measured in zip(meshes, report["meshes"]):
        for key in ("boundary_edges", "edges_over_two_faces", "inconsistent_winding_edges", "opposed_corner_faces"):
            counts = {}
            for index in measured[key]:
                indices = (obj.data.polygons[index] if key == "opposed_corner_faces" else obj.data.edges[index]).vertices
                co = sum((obj.matrix_world @ obj.data.vertices[i].co for i in indices), Vector()) / len(indices)
                label = region(co)
                counts[label] = counts.get(label, 0)+1
            regional[key] = counts
    report["regional_flags"] = {"counts": regional, "note": "Coarse world-space bins by edge/face center; not semantic segmentation or proof each boundary is an unintended hole."}
    kd = KDTree(len(points))
    for i, co in enumerate(points):
        kd.insert(co, i)
    kd.balance()
    residuals = sorted(kd.find(Vector((-co.x, co.y, co.z)))[2] for co in points)
    report["mirror_x_nearest_vertex_distance"] = {
        "median": residuals[len(residuals)//2], "p95": residuals[int(len(residuals)*.95)],
        "max": residuals[-1], "note": "World X=0 reflection; nearest vertex sampling, not surface correspondence or anatomical symmetry proof."}
    write("geometry.json", report)
    print("GEOMETRY_COMPLETE", json.dumps(box), flush=True)
    if "--inspect-only" not in sys.argv:
        render(meshes, box)
    after = protected_hashes()
    geometry_after = {o.name: helper.geometry_digest(o.data) for o in meshes}
    passed = before == after and all(geometry_after[m["name"]] == m["geometry_sha256"] for m in report["meshes"])
    write("preservation.json", {"passed": passed, "file_count": len(before), "before": before,
                                "after": after, "mesh_geometry_after": geometry_after})
    assert passed
    assert sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file()) < 150_000_000
    print("INTAKE_COMPLETE; preservation verified", flush=True)


def render(meshes, box):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    shading = scene.display.shading
    shading.light, shading.studio_light, shading.color_type = "STUDIO", "paint.sl", "OBJECT"
    shading.background_type = "WORLD"
    scene.world.color = (0.18, 0.18, 0.18)
    shading.show_shadows = shading.show_cavity = shading.show_specular_highlight = True
    shading.cavity_type = "BOTH"
    scene.display.render_aa = "16"
    for o in meshes:
        o.color = (.55, .55, .55, 1)
    center = (Vector(box["min"]) + Vector(box["max"])) / 2
    span = max(box["size"])
    cam_data = bpy.data.cameras.new("DiagnosticCamera")
    cam = bpy.data.objects.new("DiagnosticCamera", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam_data.type, cam_data.clip_start, cam_data.clip_end = "ORTHO", span*.001, span*12
    edges = bpy.data.curves.new("DiagnosticEdges", "CURVE")
    edges.dimensions, edges.resolution_u, edges.bevel_resolution = "3D", 1, 0
    for o in meshes:
        for edge in o.data.edges:
            spline = edges.splines.new("POLY")
            spline.points.add(1)
            for point, vi in zip(spline.points, edge.vertices):
                point.co = (*(o.matrix_world @ o.data.vertices[vi].co), 1)
    edge_obj = bpy.data.objects.new("DiagnosticEdges", edges)
    scene.collection.objects.link(edge_obj)
    edge_obj.color = (.015, .015, .015, 1)
    # Imported body is X-wide, Z-up; camera names describe actual source axes.
    views = [("minus_y", center, (0,-1,0), span*1.1),
             ("plus_y", center, (0,1,0), span*1.1),
             ("plus_x", center, (1,0,0), span*1.1),
             ("minus_x", center, (-1,0,0), span*1.1),
             ("oblique_front", center, (1,-1,.3), span*1.1),
             ("oblique_back", center, (-1,1,.3), span*1.1)]
    # Hand and joint regions are specified as fractions of measured source span;
    # these camera positions do not normalize, fit or change the source model.
    points = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
    for side, sign in (("x_positive", 1), ("x_negative", -1)):
        hand = [p for p in points if sign*p.x > span*.395]
        hb = helper.bounds(hand)
        hc = (Vector(hb["min"]) + Vector(hb["max"])) / 2
        for label, direction in (("above", (0,-.2,1)), ("below", (0,-.2,-1)), ("oblique", (sign,-1,.65))):
            views.append((f"hand_{side}_{label}", hc, direction, span*.19))
    z0, height = box["min"][2], box["size"][2]
    for name, x, z, scale in (("shoulders", 0, .755, .50), ("elbow_x_positive", .31, .76, .20),
                               ("elbow_x_negative", -.31, .76, .20), ("hips_crotch", 0, .49, .39),
                               ("knees", 0, .29, .40), ("ankles", 0, .09, .40)):
        target = Vector((x*span, center.y, z0+height*z))
        for label, direction in (("front", (0,-1,.1)), ("back", (0,1,.1))):
            views.append((name+"_"+label, target, direction, span*scale))
    records = []
    for name, target, direction, scale in views:
        direction = Vector(direction).normalized()
        cam.location = target + direction*span*3
        cam.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
        cam_data.ortho_scale = scale
        edges.bevel_depth = scale*.00042
        for wire in (False, True):
            edge_obj.hide_render = not wire
            scene.render.filepath = str(OUT / (name + ("_wire.png" if wire else "_gray.png")))
            bpy.ops.render.render(write_still=True)
        records.append({"name": name, "target": list(target), "direction_from_target": list(direction),
                        "ortho_scale": scale, "edge_radius": edges.bevel_depth})
    write("views.json", {"resolution": [1200,1200], "cameras": records,
                         "wire": "Temporary exact polygon-edge curves; visible surface overlay, not x-ray; no source edits."})


if __name__ == "__main__":
    main()
