"""Clearly identified editor authoring previews, never firing evidence."""
import json
import unreal as u
import progressive_audit as audit

def preview_actors():
    # EditorActorSubsystem.get_all_level_actors excludes transient actors.
    # Inspect the editor world's actor list so previous preview stages cannot
    # remain visible underneath the next deliberately exposed state.
    world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
    return [a for a in u.GameplayStatics.get_all_actors_of_class(world,u.Actor)
            if a.get_actor_label() in ['RC02_AUTHORING_PREVIEW_NOT_FIRING','RC02_AUTHORING_LIGHT_ONLY']]

def remove_previews():
    for actor in preview_actors():
        actor.destroy_actor()
    assert not preview_actors(), 'Temporary preview actors must be removed.'

def restore():
    actors=u.get_editor_subsystem(u.EditorActorSubsystem)
    remove_previews()
    prop=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='RC01_ReinforcedColumn')
    gc=prop.get_component_by_class(u.GeometryCollectionComponent)
    gc.set_visibility(True)
    gc.set_cast_shadow(True)
    u.get_editor_subsystem(u.LevelEditorSubsystem).editor_set_game_view(False)
    import importlib.util,re
    spec=importlib.util.spec_from_file_location('ngd_inspect',audit.ROOT/'Scripts/NextGenDestructionIntegration01/inspect_scene.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    old=json.loads((audit.OUT/'editor-before.json').read_text())['actors']
    stable=lambda row:re.sub(r'0x[0-9A-Fa-f]+','PTR',json.dumps(row,sort_keys=True))
    assert stable(old)==stable(module.actors()), 'Do not save unexpected scene changes.'
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
    print('Preview actors removed, original GC visibility/shadow restored; all 144 scene actors match before-state.')

def setup(state,view='front',revision='final08',evidence_prefix=''):
    ed=u.get_editor_subsystem(u.UnrealEditorSubsystem)
    assert not ed.get_game_world()
    assert ed.get_editor_world().get_path_name()=='/Game/Maps/L_OpeningLobby_PainterStone01.L_OpeningLobby_PainterStone01'
    actors=u.get_editor_subsystem(u.EditorActorSubsystem)
    prop=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='RC01_ReinforcedColumn')
    gc=prop.get_component_by_class(u.GeometryCollectionComponent)
    remove_previews()
    gc.set_visibility(state=='Intact')
    gc.set_cast_shadow(state=='Intact')
    preview=None
    preview_geometry=None
    if state!='Intact':
        assert state in ['Shallow','Deep']
        preview=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(-1260,-240,0),u.Rotator(),transient=True)
        preview.set_actor_label('RC02_AUTHORING_PREVIEW_NOT_FIRING')
        preview_mesh=u.load_asset('/Game/ReinforcedColumn01/SM_RC02_Preview_'+state)
        preview.static_mesh_component.set_static_mesh(preview_mesh)
        preview_geometry=json.loads(u.NGDColumnAuthoring.inspect_mesh(preview_mesh))
        preview.static_mesh_component.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
    actors.clear_actor_selection_set()
    if view=='front':
        camera=u.Vector(-1550,100,175);rotation=u.Rotator(pitch=-4.5,yaw=-47,roll=0)
    else:
        camera=u.Vector(-1270,90,160);rotation=u.Rotator(pitch=-2.5,yaw=-88,roll=0)
    ed.set_level_viewport_camera_info(camera,rotation)
    light=actors.spawn_actor_from_class(u.PointLight,u.Vector(-1260,20,155),u.Rotator(),transient=True)
    light.set_actor_label('RC02_AUTHORING_LIGHT_ONLY')
    component=light.get_component_by_class(u.PointLightComponent)
    component.set_mobility(u.ComponentMobility.MOVABLE)
    component.set_attenuation_radius(1100)
    component.set_intensity(1800)
    component.set_source_radius(35)
    u.get_editor_subsystem(u.LevelEditorSubsystem).editor_set_game_view(True)
    active_previews=preview_actors()
    assert len(active_previews)==(1 if state=='Intact' else 2)
    audit.write(evidence_prefix+'authoring-preview-'+state.lower()+'-'+view+'-'+revision+'.json',dict(type='Non-gameplay authoring preview; selected source pieces deliberately omitted, not firing evidence.',
                state=state,camera=str(camera),rotation=str(rotation),temporary_actor=str(preview),preview_geometry=preview_geometry,
                temporary_inspection_light=dict(location=[-1260,20,155],intensity=1800,source_radius_cm=35,casts_shadows=True),hidden_intact_shadow_disabled=state!='Intact',
                preview_actor_count=len(active_previews),game_world=False))
    print('Ready: '+state+' authoring preview, no gameplay.')
