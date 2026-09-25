"""Build a separate, tolerance-bounded core collider without changing render geometry."""
import json
from pathlib import Path
import unreal as u

CORE = '/Game/ReinforcedColumn01/SM_RC01_SupportedColumn'
PROXY = '/Game/ReinforcedColumn01/SM_RC01_CoreCollision'


def build(report_path):
    ed = u.get_editor_subsystem(u.UnrealEditorSubsystem)
    assert not ed.get_game_world(), 'Stop PIE before collision authoring'
    assert not u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
    report_path = Path(report_path)
    assert not report_path.exists(), report_path
    core = u.load_asset(CORE)
    before = json.loads(u.NGDColumnAuthoring.inspect_mesh(core))
    mesh = u.DynamicMesh()
    _, outcome = u.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(
        core, mesh, u.GeometryScriptCopyMeshFromAssetOptions(apply_build_settings=False),
        u.GeometryScriptMeshReadLOD(lod_type=u.GeometryScriptLODType.SOURCE_MODEL))
    assert outcome == u.GeometryScriptOutcomePins.SUCCESS
    u.GeometryScript_MeshRepair.weld_mesh_edges(mesh, u.GeometryScriptWeldEdgesOptions(tolerance=.001))
    source_closed = mesh.get_is_closed_mesh()
    source_bounds = str(mesh.get_mesh_bounding_box())
    # Half a centimetre limits geometric error on the 240 x 240 x 1800 cm core.
    options = u.GeometryScriptSimplifyMeshOptions(
        method=u.GeometryScriptRemoveMeshSimplificationType.STANDARD_QEM,
        allow_seam_collapse=True, allow_seam_smoothing=True, allow_seam_splits=True)
    u.GeometryScript_MeshSimplification.apply_simplify_to_tolerance(mesh, .5, options)
    triangles = mesh.get_triangle_count()
    assert 0 < triangles < before['source_triangles'] / 4, triangles
    assert not source_closed or mesh.get_is_closed_mesh()
    proxy = u.load_asset(PROXY) if u.EditorAssetLibrary.does_asset_exist(PROXY) else None
    if proxy:
        _, outcome = u.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(
            mesh, proxy, u.GeometryScriptCopyMeshToAssetOptions(), u.GeometryScriptMeshWriteLOD())
    else:
        proxy, outcome = u.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(
            mesh, PROXY, u.GeometryScriptCreateNewStaticMeshAssetOptions(
                enable_nanite=False, enable_collision=True,
                collision_mode=u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE))
    assert outcome == u.GeometryScriptOutcomePins.SUCCESS
    core.set_editor_property('complex_collision_mesh', proxy)
    collection = u.load_asset('/Game/ReinforcedColumn01/GC_RC01_BondedConcrete')
    collection.set_editor_property('slow_moving_as_sleeping', True)
    collection.set_editor_property('slow_moving_velocity_threshold', 10.)
    assert json.loads(u.NGDColumnAuthoring.inspect_mesh(core)) == before
    for asset in [proxy, core, collection]:
        assert u.EditorAssetLibrary.save_loaded_asset(asset)
    report = dict(source=CORE, proxy=PROXY, tolerance_cm=.5, render_before=before,
                  proxy_triangles=triangles, source_closed=source_closed,
                  proxy_closed=mesh.get_is_closed_mesh(), source_bounds=source_bounds,
                  proxy_bounds=str(mesh.get_mesh_bounding_box()))
    report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))
