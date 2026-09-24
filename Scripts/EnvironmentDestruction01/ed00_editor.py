"""MSQ-140 bounded editor evidence; no shared assets or settings are saved."""
import hashlib
import json
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import unreal as u

ROOT = Path("D:/devgames/MeridianSquad")
OUT = ROOT / "Saved/EnvironmentDestruction01/ED-00/MSQ-140-Candidate01"
SOURCE = "/Game/Maps/L_OpeningLobby_PainterStone01"
TARGET = "/Game/Maps/L_OpeningLobby_DestructionLab01"


def write(name, data):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / (name + ".json")
    assert not path.exists(), "Evidence already exists: " + str(path)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    return data


def world():
    return u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()


def dirty():
    return {
        "maps": sorted(p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_map_packages()),
        "content": sorted(p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_content_packages()),
    }


def guard(expected):
    assert Path(u.Paths.convert_relative_path_to_full(u.Paths.get_project_file_path())).resolve() == ROOT / "MeridianSquad.uproject"
    assert world().get_package().get_path_name() == expected
    assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world() is None
    assert dirty() == {"maps": [], "content": []}, dirty()


def xyz(value):
    return [value.x, value.y, value.z]


def rotation(value):
    return [value.pitch, value.yaw, value.roll]


def prop(obj, name):
    try:
        value = obj.get_editor_property(name)
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        return str(value)
    except Exception as exc:
        return {"unavailable": str(exc)}


def actors():
    rows = []
    for actor in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
        components = []
        for component in actor.get_components_by_class(u.StaticMeshComponent):
            mesh = component.static_mesh
            components.append({
                "name": component.get_name(),
                "package": component.get_package().get_path_name(),
                "external": component.is_package_external(),
                "mesh": mesh.get_path_name() if mesh else None,
                "materials": [m.get_path_name() if m else None for m in component.get_materials()],
                "relative_location": xyz(component.relative_location),
                "relative_rotation": rotation(component.relative_rotation),
                "relative_scale": xyz(component.relative_scale3d),
                "collision": str(component.get_collision_enabled()),
                "collision_profile": str(component.get_collision_profile_name()),
                "simulate_physics": component.is_simulating_physics(),
                "mobility": str(component.mobility),
            })
        origin, extent = actor.get_actor_bounds(False)
        rows.append({
            "name": actor.get_name(), "label": actor.get_actor_label(),
            "class": actor.get_class().get_path_name(), "path": actor.get_path_name(),
            "package": actor.get_package().get_path_name(), "external": actor.is_package_external(),
            "level": actor.get_level().get_path_name(),
            "location": xyz(actor.get_actor_location()), "rotation": rotation(actor.get_actor_rotation()),
            "scale": xyz(actor.get_actor_scale3d()), "bounds_origin_cm": xyz(origin),
            "bounds_size_cm": [v * 2 for v in xyz(extent)], "meshes": components,
        })
    return sorted(rows, key=lambda a: a["name"])


def dependency_graph(package):
    registry = u.AssetRegistryHelpers.get_asset_registry()
    options = u.AssetRegistryDependencyOptions(include_hard_package_references=True, include_soft_package_references=True)
    pending, graph = [package], {}
    while pending:
        current = pending.pop()
        if current in graph or current.startswith("/Script/"):
            continue
        assert len(graph) < 5000, "Unexpected dependency expansion"
        refs = sorted(str(p) for p in registry.get_dependencies(current, options))
        graph[current] = refs
        pending.extend(p for p in refs if p.startswith("/Game/") and p not in graph)
    return graph


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def fingerprint(graph):
    paths = {ROOT / "AGENTS.md", ROOT / "Config/DefaultEngine.ini", ROOT / "MeridianSquad.uproject"}
    missing = []
    for package in graph:
        if not package.startswith("/Game/"):
            continue
        stem = ROOT / "Content" / package.removeprefix("/Game/")
        found = [Path(str(stem) + ext) for ext in (".umap", ".uasset", ".ubulk", ".uexp") if Path(str(stem) + ext).exists()]
        paths.update(found)
        if not found:
            missing.append(package)
    return {"files": {str(p.relative_to(ROOT)).replace("\\", "/"): {"bytes": p.stat().st_size, "sha256": digest(p)} for p in sorted(paths)}, "missing_game_packages": missing}


def snapshot(name, expected):
    guard(expected)
    row = actors()
    graph = dependency_graph(expected)
    settings = world().get_world_settings()
    data = {
        "utc": datetime.now(timezone.utc).isoformat(), "map": expected,
        "engine": u.SystemLibrary.get_engine_version(), "dirty": dirty(),
        "actors": row, "actor_classes": dict(Counter(a["class"] for a in row)),
        "world_partition": prop(settings, "world_partition"),
        "streaming_levels": prop(world(), "streaming_levels"),
        "world_settings": {k: prop(settings, k) for k in ("default_game_mode", "world_to_meters", "enable_world_bounds_checks", "kill_z", "global_gravity_z", "world_gravity_z")},
        "dependency_graph": graph, "fingerprints": fingerprint(graph),
    }
    write(name, data)
    return {"evidence": str(OUT / (name + ".json")), "actors": len(row), "packages": len(graph), "file_count": len(data["fingerprints"]["files"]), "missing": data["fingerprints"]["missing_game_packages"], "world_partition": data["world_partition"], "streaming_levels": data["streaming_levels"]}


def copy_map():
    guard(SOURCE)
    assert (OUT / "source-before.json").exists()
    assert not u.EditorAssetLibrary.does_asset_exist(TARGET)
    assert not (ROOT / "Content/Maps/L_OpeningLobby_DestructionLab01.umap").exists()
    before = json.loads((OUT / "source-before.json").read_text(encoding="utf-8"))
    assert all(not a["external"] and a["package"] == SOURCE for a in before["actors"])
    assert before["world_partition"] is None
    levels = [x.get_path_name() for x in u.EditorLevelUtils.get_levels(world())]
    assert levels == [SOURCE + ".L_OpeningLobby_PainterStone01:PersistentLevel"], levels
    assert [p for p in before["fingerprints"]["files"] if p.endswith(".umap")] == ["Content/Maps/L_OpeningLobby_PainterStone01.umap"]
    assert fingerprint(before["dependency_graph"]) == before["fingerprints"], "Source changed after preflight"
    # Native SaveMap -> FEditorFileUtils::SaveWorld -> DuplicateSingleObject for
    # an existing on-disk map; the engine owns world/object GUID remapping.
    saved = u.EditorLoadingAndSavingUtils.save_map(world(), TARGET)
    return write("copy-operation", {"saved": saved, "method": "EditorLoadingAndSavingUtils.save_map / native FEditorFileUtils SaveAs", "map_after": world().get_package().get_path_name(), "dirty_after": dirty()})


def verify():
    guard(TARGET)
    before = json.loads((OUT / "source-before.json").read_text(encoding="utf-8"))
    after = json.loads((OUT / "lab-loaded.json").read_text(encoding="utf-8"))
    normalize = lambda value: json.loads(json.dumps(value).replace(TARGET.rsplit("/", 1)[1], SOURCE.rsplit("/", 1)[1]))
    preserved = fingerprint(before["dependency_graph"]) == before["fingerprints"]
    equal = normalize(after["actors"]) == before["actors"]
    dependencies = normalize(after["dependency_graph"]) == before["dependency_graph"]
    owns_all = all(a["package"] == TARGET and not a["external"] and all(c["package"] == TARGET and not c["external"] for c in a["meshes"]) for a in after["actors"])
    result = {"source_and_shared_fingerprints_unchanged": preserved, "actor_component_transform_mesh_material_collision_equal": equal, "dependencies_equal_after_world_path_remap": dependencies, "all_actor_and_component_packages_owned_by_lab": owns_all, "source_world_not_referenced": all(SOURCE not in refs for refs in after["dependency_graph"].values()), "dirty": dirty(), "source_file_count": len(before["fingerprints"]["files"])}
    write("ownership-preservation02", result)
    assert preserved and equal and dependencies and owns_all, result
    return result


def prepare_runtime():
    game = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    assert game and "L_OpeningLobby_DestructionLab01" in game.get_path_name()
    pc = u.GameplayStatics.get_player_controller(game, 0)
    pawn = u.GameplayStatics.get_player_pawn(game, 0)
    pc.set_ignore_move_input(True)
    pc.set_ignore_look_input(True)
    pawn.get_component_by_class(u.CharacterMovementComponent).stop_movement_immediately()
    pawn.set_actor_location(u.Vector(1900, 0, 90.15), False, True)
    pc.set_control_rotation(u.Rotator(pitch=0, yaw=180, roll=0))
    return write("runtime-fixed-pose", {"world": game.get_path_name(), "location": xyz(pawn.get_actor_location()), "rotation": rotation(pc.get_control_rotation()), "input_ignored_for_bounded_test": True, "viewport": pc.get_viewport_size(), "world_seconds": u.GameplayStatics.get_time_seconds(game)})


def start_profile(name):
    assert name in ("baseline-stationary", "baseline-route")
    game = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    assert game and "L_OpeningLobby_DestructionLab01" in game.get_path_name()
    assert not (OUT / (name + ".csv")).exists()
    gpu_before = u.SystemLibrary.get_console_variable_int_value("r.GPUCsvStatsEnabled")
    write(name + "-start", {"utc": datetime.now(timezone.utc).isoformat(), "wall_clock": time.perf_counter(), "world_seconds": u.GameplayStatics.get_time_seconds(game), "gpu_csv_before": gpu_before, "capture_path": str(OUT / (name + ".csv")), "quality_cvars_changed": [], "profiling_only_override": {"r.GPUCsvStatsEnabled": 1}})
    u.SystemLibrary.execute_console_command(game, "r.GPUCsvStatsEnabled 1")
    u.SystemLibrary.execute_console_command(game, "csvprofile STARTFILE=../../EnvironmentDestruction01/ED-00/MSQ-140-Candidate01/" + name + ".csv")
    u.SystemLibrary.execute_console_command(game, "csvprofile START")
    return {"started": name}


def stop_profile(name):
    game = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    context = game or world()
    u.SystemLibrary.execute_console_command(context, "csvprofile STOP")
    start = json.loads((OUT / (name + "-start.json")).read_text())
    u.SystemLibrary.execute_console_command(context, "r.GPUCsvStatsEnabled " + str(start["gpu_csv_before"]))
    return write(name + "-stop", {"utc": datetime.now(timezone.utc).isoformat(), "wall_seconds": time.perf_counter() - start["wall_clock"], "world_seconds": u.GameplayStatics.get_time_seconds(game) if game else None, "gpu_csv_restored": u.SystemLibrary.get_console_variable_int_value("r.GPUCsvStatsEnabled")})
