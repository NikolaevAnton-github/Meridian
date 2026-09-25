"""Saved asset and unrelated scene preservation checks for MSQ-156."""
import hashlib
import importlib.util
import json
import re
import unreal as u
import progressive_audit as audit

ROOT=audit.ROOT
OUT=audit.OUT

def verify(name,source_path='Assets/Source/ReinforcedColumn01/ReinforcedColumn02-Candidate01/column03.json'):
    assert not (OUT/(name+'.json')).exists()
    ed=u.get_editor_subsystem(u.UnrealEditorSubsystem)
    assert not ed.get_game_world()
    assert ed.get_editor_world().get_path_name()=='/Game/Maps/L_OpeningLobby_PainterStone01.L_OpeningLobby_PainterStone01'
    spec=importlib.util.spec_from_file_location('ngd_inspect',ROOT/'Scripts/NextGenDestructionIntegration01/inspect_scene.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    rows=module.actors()
    before=json.loads((OUT/'editor-before.json').read_text())['actors']
    old={r['name']:r for r in before};now={r['name']:r for r in rows}
    stable=lambda row:re.sub(r'0x[0-9A-Fa-f]+','PTR',json.dumps(row,sort_keys=True))
    changed=[key for key in old if key in now and stable(old[key])!=stable(now[key])]
    assert old.keys()==now.keys()
    assert not changed, changed
    hashes=json.loads((OUT/'protected-hashes.json').read_text())
    altered=[p for p,h in hashes.items() if audit.digest(ROOT/p)!=h]
    assert not altered, altered
    gc=u.load_asset('/Game/ReinforcedColumn01/GC_RC01_BondedConcrete')
    data=json.loads(u.NGDColumnAuthoring.inspect_collection(gc))
    assert data['level_counts']=={'0':1,'1':120,'2':764}
    assert data['anchored_count']==120 and data['initial_states']=={'2':241,'4':644}
    assert not data['leaves_without_convex']
    settings=dict(clustering=gc.get_editor_property('enable_clustering'),connection_type=str(gc.get_editor_property('cluster_connection_type')),
                  thresholds=list(gc.get_editor_property('damage_threshold')),
                  shapes=str(gc.get_editor_property('size_specific_data')),materials=[str(m) for m in gc.get_editor_property('materials')])
    meshes={}
    source=json.loads((ROOT/source_path).read_text())
    expected=dict(SM_RC01_SupportedColumn=len(source['core']['triangles']),SM_RC01_Rebar=len(source['steel']['triangles']))
    for preview in source['previews']:
        expected[preview['name']]=sum(len(source['pieces'][i]['triangles']) for i in preview['pieces'])
    sm=u.get_editor_subsystem(u.StaticMeshEditorSubsystem)
    for asset in ['SM_RC01_SupportedColumn','SM_RC01_Rebar','SM_RC02_Preview_Shallow','SM_RC02_Preview_Deep']:
        obj=u.load_asset('/Game/ReinforcedColumn01/'+asset)
        build=sm.get_lod_build_settings(obj,0)
        assert not build.recompute_normals and not build.recompute_tangents
        assert build.use_full_precision_u_vs and build.use_high_precision_tangent_basis
        assert len(obj.get_editor_property('static_materials'))==4
        geometry=json.loads(u.NGDColumnAuthoring.inspect_mesh(obj))
        assert geometry['source_triangles']==expected[asset], (asset,geometry,expected[asset])
        assert geometry['invalid_normals']==0 and geometry['invalid_tangents']==0, (asset,geometry)
        body=obj.get_editor_property('body_setup')
        assert body.get_editor_property('collision_trace_flag')==u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE
        meshes[asset]=dict(build=str(build),bounds=str(obj.get_bounding_box()),collision=str(body.get_editor_property('collision_trace_flag')),geometry=geometry)
    prop=next(a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors() if a.get_actor_label()=='RC01_ReinforcedColumn')
    assert abs(prop.get_editor_property('MinDamageRadius')-.14)<1e-5
    assert prop.get_component_by_class(u.NGDPropComponent)
    component=prop.get_component_by_class(u.GeometryCollectionComponent)
    assert component.is_visible() and component.get_editor_property('cast_shadow')
    temporary=[a.get_actor_label() for a in u.GameplayStatics.get_all_actors_of_class(ed.get_editor_world(),u.Actor)
               if a.get_actor_label() in ['RC02_AUTHORING_PREVIEW_NOT_FIRING','RC02_AUTHORING_LIGHT_ONLY']]
    assert not temporary, temporary
    dirty=[x.get_path_name() for x in list(u.EditorLoadingAndSavingUtils.get_dirty_map_packages())+list(u.EditorLoadingAndSavingUtils.get_dirty_content_packages())]
    assert not dirty, dirty
    record=dict(actors=rows,actor_count=len(rows),actor_changes=changed,protected_files=len(hashes),protected_changes=altered,
                collection=data,settings=settings,static_meshes=meshes,radius=prop.get_editor_property('MinDamageRadius'),
                dirty=dirty,temporary_preview_actors=temporary,collection_visible=True,collection_casts_shadow=True,gameplay_tested=False)
    audit.write(name+'.json',record)
    print(json.dumps(dict(actor_count=len(rows),actor_changes=changed,protected_files=len(hashes),protected_changes=altered,
                         dirty=dirty,collision_leaves=764,gameplay_tested=False)))
