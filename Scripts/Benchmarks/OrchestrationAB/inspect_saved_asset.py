"""Independently inspect a saved benchmark blend and FBX in headless Blender.

Run with: blender --background --factory-startup --disable-autoexec
  --python-exit-code 1 --python inspect_saved_asset.py -- BenchA
No source asset is saved or modified. Reports are written only beneath Saved/.
"""

import argparse
import hashlib
import json
import math
import sys
import traceback
from collections import defaultdict
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[3]
BOUNDS_TOL = 0.0001  # Meters: the specification's 0.01 cm tolerance.
TRANSFORM_TOL = 1e-6
GEOMETRY_AREA_TOL = 1e-12
UV_AREA_TOL = 1e-12
UV_OVERLAP_TOL = 1e-10
UV_COORD_TOL = 1e-6
EXPECTED_BOUNDS = [[-0.60, -0.40, 0.0], [0.60, 0.40, 0.90]]


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value


def bounds(points):
    if not points:
        return None
    return [[min(p[axis] for p in points) for axis in range(3)],
            [max(p[axis] for p in points) for axis in range(3)]]


def bounds_error(actual, expected):
    if actual is None:
        return float("inf")
    return max(abs(actual[side][axis] - expected[side][axis])
               for side in range(2) for axis in range(3))


def part(name, size, center, material):
    return {"name": name, "dimensions_m": size, "center_m": center,
            "material": material,
            "bounds_m": [[center[a] - size[a] / 2 for a in range(3)],
                         [center[a] + size[a] / 2 for a in range(3)]]}


def expected_parts():
    result = [part("Body", [1.12, 0.72, 0.70], [0, 0, 0.45], "Body"),
              part("Lid", [1.20, 0.80, 0.10], [0, 0, 0.85], "Body")]
    for x in (-0.56, 0.56):
        for y in (-0.36, 0.36):
            result.append(part(f"Post_{x:+.2f}_{y:+.2f}", [0.08, 0.08, 0.72],
                               [x, y, 0.44], "Metal"))
    for y in (-0.26, 0.26):
        result.append(part(f"Foot_{y:+.2f}", [1.12, 0.12, 0.08], [0, y, 0.04], "Metal"))
    return result


def add_check(report, name, passed, actual=None, expected=None):
    check = {"name": name, "passed": bool(passed)}
    if actual is not None:
        check["actual"] = actual
    if expected is not None:
        check["expected"] = expected
    report["checks"].append(check)


def cross2(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def polygon_area(poly):
    if len(poly) < 3:
        return 0.0
    return abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(poly, poly[1:] + poly[:1]))) / 2


def triangle_intersection_area(first, second):
    """Convex polygon clipping; shared edges/vertices have zero intersection area."""
    clip = second if cross2(*second) > 0 else list(reversed(second))
    polygon = list(first)
    for a, b in zip(clip, clip[1:] + clip[:1]):
        if not polygon:
            return 0.0
        output = []
        previous = polygon[-1]
        previous_distance = cross2(a, b, previous)
        for current in polygon:
            distance = cross2(a, b, current)
            inside = distance >= -1e-14
            previous_inside = previous_distance >= -1e-14
            if inside != previous_inside:
                denominator = previous_distance - distance
                if abs(denominator) > 1e-20:
                    t = previous_distance / denominator
                    output.append([previous[d] + t * (current[d] - previous[d]) for d in range(2)])
            if inside:
                output.append(current)
            previous, previous_distance = current, distance
        polygon = output
    return polygon_area(polygon)


def uv_overlaps(triangles):
    by_material = defaultdict(list)
    for index, triangle in enumerate(triangles):
        uv = triangle["uv"]
        if triangle["area"] <= UV_AREA_TOL or not all(math.isfinite(v) for p in uv for v in p):
            continue
        box = [min(p[0] for p in uv), min(p[1] for p in uv),
               max(p[0] for p in uv), max(p[1] for p in uv)]
        by_material[triangle["material_name"]].append((box, index, uv))
    count, max_area, examples = 0, 0.0, []
    for material, items in by_material.items():
        items.sort(key=lambda item: item[0][0])
        for i, (box, index, uv) in enumerate(items):
            for other_box, other_index, other_uv in items[i + 1:]:
                if other_box[0] >= box[2]:
                    break
                if other_box[1] >= box[3] or other_box[3] <= box[1]:
                    continue
                area = triangle_intersection_area(uv, other_uv)
                if area > UV_OVERLAP_TOL:
                    count += 1
                    max_area = max(max_area, area)
                    if len(examples) < 25:
                        examples.append({"material": material, "triangles": [index, other_index], "area": area})
    return {"overlapping_pairs": count, "max_intersection_area": max_area,
            "area_tolerance": UV_OVERLAP_TOL, "examples": examples}


def components(mesh):
    adjacency = [set() for _ in mesh.vertices]
    for edge in mesh.edges:
        a, b = edge.vertices
        adjacency[a].add(b)
        adjacency[b].add(a)
    remaining = set(range(len(mesh.vertices)))
    groups = []
    while remaining:
        pending = [min(remaining)]
        group = set()
        while pending:
            current = pending.pop()
            if current in group:
                continue
            group.add(current)
            pending.extend(adjacency[current] - group)
        remaining.difference_update(group)
        groups.append(group)
    return groups


def bevel_evidence(points, component_bounds):
    """Measure planar face insets and a two-segment edge profile.

    These measurements inspect final geometry; a removed modifier is not proof
    that beveling occurred. The specification does not fix the bevel profile
    factor, so measure its single interior breakpoint rather than require 0.5.
    Corner-cap triangulation is intentionally unrestricted.
    """
    width = 0.01
    tolerance = BOUNDS_TOL
    face_insets, profile_matches = [], []
    for axis in range(3):
        for side in range(2):
            plane_points = [p for p in points if abs(p[axis] - component_bounds[side][axis]) < 1e-6]
            other_axes = [a for a in range(3) if a != axis]
            insets = []
            if plane_points:
                for other in other_axes:
                    insets.extend([min(p[other] for p in plane_points) - component_bounds[0][other],
                                   component_bounds[1][other] - max(p[other] for p in plane_points)])
            face_insets.append({"axis": axis, "side": side, "insets_m": insets,
                                "passed": len(insets) == 4 and all(abs(value - width) <= tolerance for value in insets)})
    for axis_a, axis_b in ((0, 1), (0, 2), (1, 2)):
        third_axis = next(axis for axis in range(3) if axis not in (axis_a, axis_b))
        for side_a in range(2):
            for side_b in range(2):
                profile = []
                for point in points:
                    if not component_bounds[0][third_axis] + width - tolerance <= point[third_axis] <= component_bounds[1][third_axis] - width + tolerance:
                        continue
                    distances = [abs(point[axis_a] - component_bounds[side_a][axis_a]),
                                 abs(point[axis_b] - component_bounds[side_b][axis_b])]
                    if max(distances) > width + tolerance:
                        continue
                    if not any(max(abs(a - b) for a, b in zip(distances, existing)) <= tolerance for existing in profile):
                        profile.append(distances)
                endpoints = [any(max(abs(a - b) for a, b in zip(sample, target)) <= tolerance
                                 for sample in profile) for target in ((0, width), (width, 0))]
                profile_matches.append({"axes": [axis_a, axis_b], "sides": [side_a, side_b],
                                        "cross_section_coordinates_m": sorted(profile),
                                        "passed": all(endpoints) and len(profile) == 3})
    return {"width_m": width, "segments": 2, "face_insets": face_insets,
            "edge_profiles": profile_matches,
            "passed": all(face["passed"] for face in face_insets)
            and all(edge["passed"] for edge in profile_matches)}


def inspect_blend(run_id, blend_path, report, uv_path):
    bpy.ops.wm.open_mainfile(filepath=str(blend_path), load_ui=False, use_scripts=False)
    scenes = list(bpy.data.scenes)
    objects = list(bpy.data.objects)
    add_check(report, "single_dedicated_scene", len(scenes) == 1 and scenes[0].name == run_id,
              [scene.name for scene in scenes], [run_id])
    expected_object = f"SM_{run_id}_Crate"
    add_check(report, "single_mesh_object", len(objects) == 1 and objects[0].type == "MESH"
              and objects[0].name == expected_object,
              [{"name": obj.name, "type": obj.type} for obj in objects], expected_object)
    obj = bpy.data.objects.get(expected_object)
    if obj is None or obj.type != "MESH":
        raise ValueError(f"Expected saved mesh object {expected_object} is missing")
    mesh = obj.data
    mesh.calc_loop_triangles()
    points = [list(vertex.co) for vertex in mesh.vertices]
    finite = all(math.isfinite(value) for point in points for value in point)
    add_check(report, "finite_mesh_vertices", finite, len(points))
    if not finite or not points:
        raise ValueError("Cannot inspect empty/non-finite geometry")
    local_bounds = bounds(points)
    world_bounds = bounds([list(obj.matrix_world @ vertex.co) for vertex in mesh.vertices])
    report["mesh"] = {"name": obj.name, "vertices": len(mesh.vertices), "faces": len(mesh.polygons),
                      "triangles": len(mesh.loop_triangles), "local_bounds_m": local_bounds,
                      "world_bounds_m": world_bounds, "materials": [m.name if m else None for m in mesh.materials]}
    add_check(report, "source_bounds", bounds_error(world_bounds, EXPECTED_BOUNDS) <= BOUNDS_TOL,
              world_bounds, EXPECTED_BOUNDS)
    matrix_error = max(abs(matrix[row][column] - (1 if row == column else 0))
                       for matrix in (obj.matrix_world, obj.matrix_basis)
                       for row in range(4) for column in range(4))
    add_check(report, "origin_and_applied_transforms", obj.parent is None and matrix_error <= TRANSFORM_TOL,
              {"matrix_error": matrix_error, "location": list(obj.location), "scale": list(obj.scale),
               "parent": obj.parent.name if obj.parent else None}, "identity transforms, no parent")
    add_check(report, "all_modifiers_applied", len(obj.modifiers) == 0, [m.type for m in obj.modifiers], [])
    add_check(report, "triangle_budget", 0 < len(mesh.loop_triangles) <= 2000, len(mesh.loop_triangles), "1..2000")
    materials = report["mesh"]["materials"]
    expected_materials = [f"M_{run_id}_Body", f"M_{run_id}_Metal"]
    add_check(report, "exact_material_slots", len(materials) == 2 and set(materials) == set(expected_materials),
              materials, expected_materials)
    groups = components(mesh)
    add_check(report, "eight_connected_components", len(groups) == 8, len(groups), 8)
    report["components"] = []
    unmatched = expected_parts()
    for component_index, group in enumerate(groups):
        component_points = [points[index] for index in group]
        component_bounds = bounds(component_points)
        expected = min(unmatched, key=lambda item: bounds_error(component_bounds, item["bounds_m"])) if unmatched else None
        match_error = bounds_error(component_bounds, expected["bounds_m"]) if expected else None
        match_ok = expected is not None and match_error <= BOUNDS_TOL
        if match_ok:
            unmatched.remove(expected)
        polygons = [polygon for polygon in mesh.polygons if polygon.vertices[0] in group]
        triangles = [triangle for triangle in mesh.loop_triangles if triangle.vertices[0] in group]
        edge_uses = defaultdict(list)
        for polygon in polygons:
            indices = list(polygon.vertices)
            for a, b in zip(indices, indices[1:] + indices[:1]):
                edge_uses[tuple(sorted((a, b)))].append(1 if a < b else -1)
        actual_edges = [tuple(sorted(edge.vertices)) for edge in mesh.edges if edge.vertices[0] in group]
        closed = bool(polygons) and all(len(edge_uses[edge]) == 2 for edge in actual_edges)
        coherent = closed and all(sum(uses) == 0 for uses in edge_uses.values())
        center = Vector([(component_bounds[0][axis] + component_bounds[1][axis]) / 2 for axis in range(3)])
        areas, outward_distances, volume = [], [], 0.0
        for triangle in triangles:
            a, b, c = (Vector(points[index]) for index in triangle.vertices)
            normal = (b - a).cross(c - a)
            areas.append(normal.length / 2)
            outward_distances.append(normal.normalized().dot((a + b + c) / 3 - center) if normal.length else 0.0)
            volume += a.dot(b.cross(c)) / 6
        material_names = sorted({materials[p.material_index] if p.material_index < len(materials)
                                 and materials[p.material_index] else "<missing>" for p in polygons})
        expected_material = f"M_{run_id}_{expected['material']}" if expected else None
        bevel = bevel_evidence(component_points, component_bounds)
        entry = {"index": component_index, "matched_part": expected["name"] if match_ok else None,
                 "bounds_m": component_bounds, "nearest_expected_part": expected["name"] if expected else None,
                 "bounds_error_m": match_error, "vertices": len(group), "edges": len(actual_edges),
                 "faces": len(polygons), "triangles": len(triangles), "closed": closed,
                 "coherent_winding": coherent, "min_triangle_area_m2": min(areas, default=0.0),
                 "min_outward_normal_distance_m": min(outward_distances, default=0.0),
                 "signed_volume_m3": volume, "materials": material_names, "bevel": bevel}
        report["components"].append(entry)
        prefix = f"component_{component_index}"
        add_check(report, prefix + "_expected_bounds", match_ok, component_bounds,
                  expected["bounds_m"] if expected else "no unmatched expected part")
        add_check(report, prefix + "_closed_outward_nondegenerate", closed and coherent and bool(areas)
                  and min(areas) > GEOMETRY_AREA_TOL and min(outward_distances) > 1e-6
                  and all(p.area > GEOMETRY_AREA_TOL for p in polygons),
                  {key: entry[key] for key in ("closed", "coherent_winding", "min_triangle_area_m2", "min_outward_normal_distance_m")})
        add_check(report, prefix + "_material", match_ok and material_names == [expected_material],
                  material_names, [expected_material])
        add_check(report, prefix + "_bevel_geometry", bevel["passed"], bevel["passed"], "0.01 m, two-segment edge profile")
    add_check(report, "all_expected_parts_present", not unmatched, [p["name"] for p in unmatched], [])
    add_check(report, "one_uv_layer", len(mesh.uv_layers) == 1, [layer.name for layer in mesh.uv_layers], 1)
    uv_data = {"run_id": run_id, "uv_layer": mesh.uv_layers[0].name if mesh.uv_layers else None,
               "uv_origin": "bottom_left", "triangles": []}
    if mesh.uv_layers:
        layer = mesh.uv_layers[0]
        for triangle in mesh.loop_triangles:
            uv = [list(layer.data[index].uv) for index in triangle.loops]
            polygon = mesh.polygons[triangle.polygon_index]
            material_name = materials[polygon.material_index] if polygon.material_index < len(materials) else "<missing>"
            uv_data["triangles"].append({"polygon_index": triangle.polygon_index,
                                         "material_index": polygon.material_index, "material_name": material_name,
                                         "uv": uv, "area": abs(cross2(*uv)) / 2,
                                         "centroid": [sum(p[axis] for p in uv) / 3 for axis in range(2)]})
    triangles = uv_data["triangles"]
    uv_values = [value for triangle in triangles for point in triangle["uv"] for value in point]
    uv_finite = bool(uv_values) and all(math.isfinite(value) for value in uv_values)
    add_check(report, "uv_finite_in_unit_square", uv_finite and all(-UV_COORD_TOL <= value <= 1 + UV_COORD_TOL for value in uv_values),
              {"finite": uv_finite, "min": min(uv_values) if uv_finite else None, "max": max(uv_values) if uv_finite else None}, "[0,1]")
    add_check(report, "uv_nondegenerate_triangles", bool(triangles) and all(t["area"] > UV_AREA_TOL for t in triangles),
              {"minimum_area": min((t["area"] for t in triangles), default=0), "area_tolerance": UV_AREA_TOL})
    overlap = uv_overlaps(triangles)
    report["uv_overlap"] = overlap
    add_check(report, "uv_nonoverlap_within_material", overlap["overlapping_pairs"] == 0, overlap)
    uv_path.write_text(json.dumps(json_safe(uv_data), indent=2, allow_nan=False), encoding="utf-8")
    report["uv_data_path"] = str(uv_path.relative_to(ROOT))
    return len(mesh.loop_triangles), expected_materials


def inspect_fbx(fbx_path, source_triangles, expected_materials, report):
    # Reset this private background process, not the user's running Blender.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # This bundled add-on exists in the installed Blender 5.2 distribution.
    # Enable it only in this ephemeral process; do not save user preferences.
    bpy.ops.preferences.addon_enable(module="io_scene_fbx")
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.scale_length = 1.0
    result = bpy.ops.import_scene.fbx(filepath=str(fbx_path), global_scale=1.0,
                                    use_custom_normals=True, use_image_search=False,
                                    bake_space_transform=False)
    add_check(report, "fbx_import_finished", "FINISHED" in result, sorted(result))
    meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    add_check(report, "fbx_single_mesh", len(meshes) == 1 and len(bpy.data.objects) == 1,
              [{"name": obj.name, "type": obj.type} for obj in bpy.data.objects], "one mesh")
    world_points, raw_points, triangle_count, slots, non_triangles = [], [], 0, [], 0
    transforms = []
    for obj in meshes:
        obj.data.calc_loop_triangles()
        world_points.extend(list(obj.matrix_world @ vertex.co) for vertex in obj.data.vertices)
        raw_points.extend(list(vertex.co) for vertex in obj.data.vertices)
        triangle_count += len(obj.data.loop_triangles)
        non_triangles += sum(len(p.vertices) != 3 for p in obj.data.polygons)
        slots.extend(material.name if material else None for material in obj.data.materials)
        transforms.append({"name": obj.name, "matrix_world": [list(row) for row in obj.matrix_world]})
    actual_bounds = bounds(world_points)
    report["fbx"] = {"raw_mesh_bounds": bounds(raw_points), "world_bounds_m": actual_bounds,
                     "scene_unit_scale": bpy.context.scene.unit_settings.scale_length,
                     "object_transforms": transforms, "triangles": triangle_count,
                     "nontriangle_polygons": non_triangles, "materials": slots}
    add_check(report, "fbx_world_bounds_meters", bounds_error(actual_bounds, EXPECTED_BOUNDS) <= BOUNDS_TOL,
              actual_bounds, EXPECTED_BOUNDS)
    add_check(report, "fbx_triangle_count_matches_saved_source", triangle_count == source_triangles,
              triangle_count, source_triangles)
    add_check(report, "fbx_triangulated_polygons", non_triangles == 0, non_triangles, 0)
    add_check(report, "fbx_material_slots", len(slots) == 2 and set(slots) == set(expected_materials), slots, expected_materials)


def main():
    arguments = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id", choices=("BenchA", "BenchB"))
    args = parser.parse_args(arguments)
    output = ROOT / "Saved/AgentSetup/OrchestrationAB/Independent" / args.run_id
    output.mkdir(parents=True, exist_ok=True)
    report_path = output / "mesh-verification.json"
    source = ROOT / "Assets/Source/SmokeTest/OrchestrationAB" / args.run_id / "Crate.blend"
    fbx = ROOT / "Saved/Exports/SmokeTest/OrchestrationAB" / args.run_id / f"SM_{args.run_id}_Crate.fbx"
    report = {"run_id": args.run_id, "blender_version": bpy.app.version_string,
              "bounds_tolerance_m": BOUNDS_TOL, "checks": [], "files": {}}
    before = {}
    try:
        for name, path in (("blend", source), ("fbx", fbx)):
            if not path.is_file():
                raise FileNotFoundError(f"Missing actual saved {name}: {path}")
            before[name] = sha256(path)
            report["files"][name] = {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size,
                                       "sha256_before": before[name]}
        triangle_count, materials = inspect_blend(args.run_id, source, report, output / "uv-data.json")
        inspect_fbx(fbx, triangle_count, materials, report)
    except Exception as error:
        report["fatal_error"] = {"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()}
    finally:
        for name, path in (("blend", source), ("fbx", fbx)):
            if name in before:
                after = sha256(path) if path.is_file() else None
                report["files"][name]["sha256_after"] = after
                add_check(report, name + "_unchanged_by_inspection", after == before[name], after, before[name])
        report["passed"] = bool(report["checks"]) and not report.get("fatal_error") and all(check["passed"] for check in report["checks"])
        report["failed_checks"] = [check["name"] for check in report["checks"] if not check["passed"]]
        report_path.write_text(json.dumps(json_safe(report), indent=2, allow_nan=False), encoding="utf-8")
        print("INDEPENDENT_ASSET_CHECK=" + json.dumps({"run_id": args.run_id, "passed": report["passed"],
              "failed_checks": report["failed_checks"], "fatal_error": report.get("fatal_error", {}).get("message"),
              "report": str(report_path.relative_to(ROOT))}))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
