"""MSQ-118 read-only static geometry audit; reuses the guarded CAI-01 lifecycle.

Import in the live editor only to register tools. Call operations through Epic MCP.
No Play, simulation, asset graph access, package save or gameplay probes.
"""
import json
from pathlib import Path
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration
from Scripts.CombatAI01.CAI01 import editor_tools as lifecycle

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT / 'Saved/CombatAI01/CAI-T01/Worker/Candidate01'
lifecycle.OUT = OUT  # Never write the prerequisite's frozen evidence.


@u.uclass()
class TacticalTools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def geometry() -> str:
        before = lifecycle.state()
        assert not before['pie'] and not before['dirty'], before
        assert before['map'] == '/Game/Maps/L_OpeningLobby_PainterStone01.L_OpeningLobby_PainterStone01'
        rows = []
        for actor in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
            component = actor.get_component_by_class(u.StaticMeshComponent)
            if not component:
                continue
            origin, extent = actor.get_actor_bounds(True)
            rows.append(dict(label=actor.get_actor_label(), path=actor.get_path_name(),
                origin=[origin.x, origin.y, origin.z], extent=[extent.x, extent.y, extent.z],
                collision=str(component.get_collision_enabled()), object_type=str(component.get_collision_object_type()),
                pawn_response=str(component.get_collision_response_to_channel(u.CollisionChannel.ECC_PAWN)),
                visibility_response=str(component.get_collision_response_to_channel(u.CollisionChannel.ECC_VISIBILITY))))
        after = lifecycle.state()
        assert before == after, (before, after)
        result = dict(before=before, actors=rows, after=after,
            scope='Read-only retained editor geometry inventory; no tactical runtime execution or position validation')
        with (OUT / 'editor-geometry.json').open('x', encoding='utf-8') as stream:
            json.dump(result, stream, indent=2)
        return json.dumps(dict(actors=len(rows), state=after))


registration = Registration([TacticalTools])
registration.register()
