"""Native Geometry Script derivation. No source asset or original lobby is written."""
import json
import math
from pathlib import Path
import unreal as u
from ed01_editor import ROOT, OUT, LAB, state, write

PACKAGE = '/Game/Development/EnvironmentDestruction01/MSQ141Candidate01'
RECIPE = ROOT / 'Assets/Source/EnvironmentDestruction01/MSQ-141-Candidate01/cladding-recipe.json'

def material():
    path = PACKAGE + '/M_ED01_Backing'
    if u.EditorAssetLibrary.does_asset_exist(path):
        return u.load_asset(path)
    m = u.AssetToolsHelpers.get_asset_tools().create_asset('M_ED01_Backing', PACKAGE, u.Material, u.MaterialFactoryNew())
    lib = u.MaterialEditingLibrary
    color = lib.create_material_expression(m, u.MaterialExpressionConstant3Vector, -250, 0)
    color.set_editor_property('constant', u.LinearColor(.18, .17, .15, 1))
    rough = lib.create_material_expression(m, u.MaterialExpressionConstant, -250, 150)
    rough.set_editor_property('r', .92)
    lib.connect_material_property(color, '', u.MaterialProperty.MP_BASE_COLOR)
    lib.connect_material_property(rough, '', u.MaterialProperty.MP_ROUGHNESS)
    lib.recompile_material(m)
    u.EditorAssetLibrary.save_loaded_asset(m)
    return m

def append_faces(mesh, faces, material_id):
    vertices, triangles, normals, uvs = [], [], [], []
    for face in faces:
        a, b, c = face[:3]
        d, e = [b[i] - a[i] for i in range(3)], [c[i] - a[i] for i in range(3)]
        n = [d[1] * e[2] - d[2] * e[1], d[2] * e[0] - d[0] * e[2], d[0] * e[1] - d[1] * e[0]]
        length = math.sqrt(sum(v * v for v in n))
        assert length > 1e-6
        normal = u.Vector(*[v / length for v in n])
        base = len(vertices)
        dominant = max(range(3), key=lambda k: abs(n[k]))
        uv_axes = ((1, 2), (0, 2), (0, 1))[dominant]
        for p in face:
            vertices.append(u.Vector(*p)); normals.append(normal)
            uvs.append(u.Vector2D(p[uv_axes[0]] / 240, p[uv_axes[1]] / 240))
        # Geometry Script uses clockwise winding (its face normal is the negative
        # Cartesian cross product). Keep supplied outward normals and reverse indices.
        triangles.extend(u.IntVector(base, base + i + 1, base + i) for i in range(1, len(face) - 1))
    buffers = u.GeometryScriptSimpleMeshBuffers(vertices=vertices, triangles=triangles, normals=normals, uv0=uvs)
    first_triangle = mesh.get_triangle_count()
    u.GeometryScript_MeshEdits.append_buffers_to_mesh(mesh, buffers, material_id)
    geometric_normal, valid = u.GeometryScript_MeshQueries.get_triangle_face_normal(mesh, first_triangle)
    assert valid and geometric_normal.dot(normals[0]) > .999, (geometric_normal, normals[0])

def prism(poly, front=2, back=-2):
    mesh = u.DynamicMesh()
    f, b = [[x, front, z] for x, z in poly], [[x, back, z] for x, z in poly]
    append_faces(mesh, [list(reversed(f))], 0)
    sides = [[f[i], f[(i + 1) % len(f)], b[(i + 1) % len(f)], b[i]] for i in range(len(f))]
    append_faces(mesh, [b] + sides, 1)
    u.GeometryScript_MeshRepair.weld_mesh_edges(mesh, u.GeometryScriptWeldEdgesOptions())
    return mesh

def column_backing():
    # The inspected source is an eight-vertex cuboid. Build its stepped exterior
    # explicitly: all original outer planes remain, except the 4 cm shell recess.
    # The inspected cuboid needs only this exact stepped exterior; a boolean or
    # GeometryCollection solver is unnecessary for the bounded backing derivative.
    mesh = u.DynamicMesh()
    def panel(axis, value, span_a, span_b, outward, material_id=0):
        axes = [i for i in range(3) if i != axis]
        face = []
        for a, b in [(span_a[0], span_b[0]), (span_a[1], span_b[0]), (span_a[1], span_b[1]), (span_a[0], span_b[1])]:
            p = [0, 0, 0]; p[axis] = value; p[axes[0]] = a; p[axes[1]] = b; face.append(p)
        a, b, c = face[:3]
        d, e = [b[i] - a[i] for i in range(3)], [c[i] - a[i] for i in range(3)]
        cross = [d[1]*e[2]-d[2]*e[1], d[2]*e[0]-d[0]*e[2], d[0]*e[1]-d[1]*e[0]]
        if cross[axis] * outward < 0:
            face.reverse()
        append_faces(mesh, [face], material_id)
    width = (-120, 120)
    lower, upper = (-900, -660), (-660, 900)
    for depth in [lower, upper]:
        panel(1, -120, width, depth, -1)
    panel(1, 116, width, lower, 1, 1)
    panel(1, 120, width, upper, 1)
    panel(2, -660, width, (116, 120), -1, 1)
    panel(2, -900, width, (-120, 116), -1)
    panel(2, 900, width, (-120, 116), 1)
    panel(2, 900, width, (116, 120), 1)
    for x in (-120, 120):
        panel(0, x, (-120, 116), lower, x)
        panel(0, x, (-120, 116), upper, x)
        panel(0, x, (116, 120), upper, x)
    u.GeometryScript_MeshRepair.weld_mesh_edges(mesh, u.GeometryScriptWeldEdgesOptions())
    return mesh

def save_mesh(dm, name, materials, core=False):
    path = PACKAGE + '/' + name
    assert not u.EditorAssetLibrary.does_asset_exist(path), path
    options = u.GeometryScriptCreateNewStaticMeshAssetOptions(enable_collision=True, enable_nanite=False,
        enable_recompute_normals=False, enable_recompute_tangents=True,
        collision_mode=u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE if core else u.CollisionTraceFlag.CTF_USE_SIMPLE_AND_COMPLEX)
    asset, outcome = u.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(dm, path, options)
    assert asset and outcome == u.GeometryScriptOutcomePins.SUCCESS, str(outcome)
    asset.set_editor_property('static_materials', [u.StaticMaterial(material_interface=m) for m in materials])
    if not core:
        collision = u.GeometryScriptCollisionFromMeshOptions(method=u.GeometryScriptCollisionGenerationMethod.CONVEX_HULLS,
            max_shape_count=1, max_convex_hulls_per_mesh=1, simplify_hulls=False, min_thickness=0,
            auto_detect_boxes=False, auto_detect_spheres=False, auto_detect_capsules=False)
        u.GeometryScript_Collision.set_static_mesh_collision_from_mesh(dm, asset, collision)
    u.EditorAssetLibrary.save_loaded_asset(asset)
    return asset

def author():
    current = state()
    assert current['map'] == LAB and not current['pie'] and all(p.startswith(PACKAGE) for p in current['dirty']), current
    data = json.loads(RECIPE.read_text())
    face = u.load_asset('/Game/OpeningLobby/MaterialsComplete01/SlabLayout01/MI_Slabs_035')
    backing = material()
    paths = []
    core_path = PACKAGE + '/SM_ED01_ColumnBacking04'
    if not u.EditorAssetLibrary.does_asset_exist(core_path):
        save_mesh(column_backing(), 'SM_ED01_ColumnBacking04', [face, backing], core=True)
    paths.append(core_path)
    for p in data['pieces']:
        name = 'SM_ED01_Cell03_%02d' % p['id']
        path = PACKAGE + '/' + name
        if not u.EditorAssetLibrary.does_asset_exist(path):
            cx, cz = p['centroid_xz_cm']
            mesh = prism([[x - cx, z - cz] for x, z in p['polygon_xz_cm']])
            save_mesh(mesh, name, [face, backing])
        paths.append(path)
    return write('assets-authored04', {'recipe': str(RECIPE.relative_to(ROOT)), 'assets': paths, 'dirty': state()['dirty']})

def place():
    current = state()
    assert current['map'] == LAB and not current['pie'] and not current['dirty'], current
    subsystem = u.get_editor_subsystem(u.EditorActorSubsystem)
    actors = subsystem.get_all_level_actors()
    existing = [a for a in actors if isinstance(a, u.DestructibleCladding)]
    assert len(existing) <= 1
    column = next(a for a in actors if a.get_name() == 'StaticMeshActor_35')
    assert column.static_mesh_component.static_mesh.get_path_name() in (
        '/Game/OpeningLobby/FunctionalBuild01/Meshes/SM_FB01_TallColumn.SM_FB01_TallColumn',
        PACKAGE + '/SM_ED01_ColumnBacking.SM_ED01_ColumnBacking',
        PACKAGE + '/SM_ED01_ColumnBacking02.SM_ED01_ColumnBacking02',
        PACKAGE + '/SM_ED01_ColumnBacking03.SM_ED01_ColumnBacking03')
    data = json.loads(RECIPE.read_text())
    shell = existing[0] if existing else subsystem.spawn_actor_from_class(u.DestructibleCladding, u.Vector(-1260, -240, 0))
    shell.set_actor_label('ED01_Column035_LowerNorthCladding')
    shell.set_folder_path('EnvironmentDestruction01/ED01')
    shell.set_editor_property('piece_meshes', [u.load_asset(PACKAGE + '/SM_ED01_Cell03_%02d' % p['id']) for p in data['pieces']])
    shell.set_editor_property('piece_transforms', [u.Transform(location=u.Vector(p['centroid_xz_cm'][0], 118, p['centroid_xz_cm'][1])) for p in data['pieces']])
    shell.set_editor_property('piece_mass_kg', [p['mass_kg'] for p in data['pieces']])
    assert shell.build_specimen()
    column.static_mesh_component.set_static_mesh(u.load_asset(PACKAGE + '/SM_ED01_ColumnBacking04'))
    # Clear the original instance override to retain both authored material slots.
    column.static_mesh_component.set_editor_property('override_materials', [])
    assert u.EditorLoadingAndSavingUtils.save_packages([column.get_package()], True)
    return write('placed04', {'source_actor': column.get_path_name(), 'shell_actor': shell.get_path_name(),
                            'state': json.loads(shell.get_cladding_state()), 'editor': state()})
