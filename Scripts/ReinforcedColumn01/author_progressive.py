"""MSQ-156 asset authoring and bounded map update, with no PIE or gameplay."""
import json
from pathlib import Path
import unreal as u
import progressive_audit as audit

ROOT=audit.ROOT
DEST='/Game/ReinforcedColumn01/'
LOBBY='/Game/Maps/L_OpeningLobby_PainterStone01'

def build(evidence='asset-build03.json',source='Assets/Source/ReinforcedColumn01/ReinforcedColumn02-Candidate01/column03.json'):
    ed=u.get_editor_subsystem(u.UnrealEditorSubsystem)
    assert Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())).resolve()==ROOT
    assert not ed.get_game_world()
    assert ed.get_editor_world().get_path_name()==LOBBY+'.L_OpeningLobby_PainterStone01'
    assert not u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
    assert not u.EditorLoadingAndSavingUtils.get_dirty_content_packages()
    assert not (audit.OUT/evidence).exists()
    # Never change collection topology while the prior component is registered.
    u.EditorLoadingAndSavingUtils.new_blank_map(False)
    result=json.loads(u.NGDColumnAuthoring.build_column(str(ROOT/source)))
    audit.write(evidence,result)
    assert 'error' not in result
    assert result['geometries']==764 and result['anchored_count']==120
    assert result['level_counts']=={'0':1,'1':120,'2':764}, result['level_counts']
    assert not result['leaves_without_convex']
    data=u.load_asset(DEST+'DA_RC01_Column')
    data.set_editor_property('DamageRadius',.14)
    assert u.EditorAssetLibrary.save_directory(DEST,only_if_is_dirty=True,recursive=True)
    print(json.dumps({k:v for k,v in result.items() if k not in ['geometry','hierarchy']}))

def integrate(evidence='integration03.json'):
    ed=u.get_editor_subsystem(u.UnrealEditorSubsystem)
    assert not ed.get_game_world()
    assert ed.get_editor_world().get_path_name()==LOBBY+'.L_OpeningLobby_PainterStone01'
    actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
    target=next(a for a in actors if a.get_name()=='StaticMeshActor_35')
    prop=next(a for a in actors if a.get_actor_label()=='RC01_ReinforcedColumn')
    assert target.get_actor_label()=='FB01_newNcolumnNN12p6NN2p4'
    assert target.static_mesh_component.static_mesh==u.load_asset(DEST+'SM_RC01_SupportedColumn')
    assert prop.get_component_by_class(u.NGDPropComponent)
    # MinDamageRadius is computed by the vendor construction script from the
    # editable DataAsset; it is deliberately read-only on actor instances.
    assert abs(prop.get_editor_property('MinDamageRadius')-.14)<1e-5
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
    audit.write(evidence,dict(target=target.get_path_name(),target_transform=str(target.get_actor_transform()),
        prop=prop.get_path_name(),prop_transform=str(prop.get_actor_transform()),radius=prop.get_editor_property('MinDamageRadius'),
        data=str(prop.get_editor_property('DataAsset')),has_kinematic_pieces=prop.get_editor_property('HasKinematicPieces'),
        material_overrides=[str(m) for m in target.static_mesh_component.get_editor_property('override_materials')]))
    print('Updated the same column actor; map saved. No gameplay invoked.')
