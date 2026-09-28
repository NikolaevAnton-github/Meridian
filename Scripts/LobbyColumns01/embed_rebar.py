"""Apply the measured vendor mesh bounds to existing editor instances."""
import unreal as u

assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
columns=[a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors() if a.actor_has_tag('LobbyColumns01')]
assert len(columns)==16
for a in columns:
    m=next(m for m in a.get_components_by_class(u.StaticMeshComponent) if m.static_mesh and m.static_mesh.get_name()=='SM_ConcretePillar_Square_5m_REBAR')
    bounds=m.static_mesh.get_bounding_box()
    scale=870/(bounds.max.z-bounds.min.z)
    m.set_relative_location(u.Vector(0,0,-30-bounds.min.z*scale),False,True)
    m.set_relative_scale3d(u.Vector(2.364,2.364,scale))
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
print('Embedded reinforcement: 16 instances, -30..840 cm')
