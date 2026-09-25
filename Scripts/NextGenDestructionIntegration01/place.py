"""Place only the requested vendor specimens in the current retained lobby."""
import json
from pathlib import Path
import unreal as u

OUT = Path('D:/devgames/MeridianSquad/Saved/NextGenDestructionIntegration01/NGD-01/Candidate01')
SOURCE = '/Game/NextGenDestruction/Blueprints/DataAssets/Destructible/'
SPECS = [
    ('NGD01_ConcretePillar', 'DA_Pillar_Small_Concrete', (-840, 700, 0), 0),
    ('NGD01_WoodenChair', 'DA_Chair_Wood', (0, 700, 0), -90),
    ('NGD01_CeramicVase', 'DA_Vase', (840, 700, 0), 0),
]

def place(indices):
    editor = u.get_editor_subsystem(u.UnrealEditorSubsystem)
    world = editor.get_editor_world()
    assert world.get_path_name() == '/Game/Maps/L_OpeningLobby_PainterStone01.L_OpeningLobby_PainterStone01'
    assert not editor.get_game_world()
    actors = u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
    labels = {a.get_actor_label() for a in actors}
    record = []
    for index in indices:
        identity, source, location, yaw = SPECS[index]
        assert identity not in labels, 'Already placed: ' + identity
        data = u.load_asset(SOURCE + source)
        assert data
        actor = u.NGDTools.spawn_prop(world, data, u.Vector(*location), u.Rotator(pitch=0, yaw=yaw, roll=0), identity)
        assert actor and actor.get_component_by_class(u.NGDPropComponent)
        gc = actor.get_component_by_class(u.GeometryCollectionComponent)
        assert gc and gc.get_editor_property('rest_collection')
        row = dict(identity=identity, actor=actor.get_path_name(), data_asset=data.get_path_name(),
                   transform=str(actor.get_actor_transform()), bounds=str(actor.get_actor_bounds(False)),
                   gc=gc.get_editor_property('rest_collection').get_path_name(),
                   materials=[m.get_path_name() if m else None for m in [gc.get_material(i) for i in range(gc.get_num_materials())]],
                   collision=str(gc.get_collision_profile_name()),
                   settings={k: str(actor.get_editor_property(k)) for k in ['MinDamageRadius', 'HasKinematicPieces', 'Damage Threshold', 'Override Damage Thresholds']})
        record.append(row)
    path = OUT / ('placement-' + '-'.join(str(i) for i in indices) + '.json')
    assert not path.exists()
    path.write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(json.dumps(record))
