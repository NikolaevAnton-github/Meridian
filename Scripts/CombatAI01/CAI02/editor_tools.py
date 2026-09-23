"""MSQ-104 read-only sensory wiring/geometry and guarded editor lifecycle.

Registered once, then invoked through official Epic MCP. Never starts gameplay.
"""
import json
from pathlib import Path
import unreal as u
import toolset_registry
from toolset_registry.registration import Registration
from Scripts.CombatAI01.CAI00.editor_tools import state
from Scripts.CombatAI01.CAI01 import editor_tools as lifecycle

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT / 'Saved/CombatAI01/CAI-02/Worker/Candidate01'
lifecycle.OUT = OUT


def graphs(bp):
    result = []
    for graph in u.BlueprintEditorLibrary.list_graphs(bp):
        nodes = []
        for node in u.BlueprintGraphEditor.get_graph_editor(graph).list_all_nodes():
            nodes.append(dict(name=node.get_name(), title=node.get_node_title(),
                pins=[dict(name=str(p.get_pin_name()), type=str(p.get_pin_type_display_string()),
                    value=p.get_pin_value(), links=[c.get_owning_node().get_name()+':'+str(c.get_pin_name())
                        for c in p.list_connected_pins()]) for p in node.list_all_pins()]))
        result.append(dict(name=graph.get_name(), nodes=nodes))
    return result


@u.uclass()
class SensesTools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str) -> str:
        current = state()
        assert not current['pie'] and not current['dirty'], current
        assert current['map'] == '/Game/Maps/L_OpeningLobby_PainterStone01.L_OpeningLobby_PainterStone01'
        OUT.mkdir(parents=True, exist_ok=True)
        result = dict(before=current)
        if operation == 'geometry':
            rows = []
            for actor in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
                part = actor.get_component_by_class(u.StaticMeshComponent)
                if not part:
                    continue
                origin, extent = actor.get_actor_bounds(True)
                rows.append(dict(label=actor.get_actor_label(), origin=[origin.x,origin.y,origin.z],
                    extent=[extent.x,extent.y,extent.z], object_type=str(part.get_collision_object_type()),
                    pawn_response=str(part.get_collision_response_to_channel(u.CollisionChannel.ECC_PAWN)),
                    visibility_response=str(part.get_collision_response_to_channel(u.CollisionChannel.ECC_VISIBILITY))))
            result['actors'] = rows
        elif operation in ('audio','audio_player'):
            paths = ['/GASPEnemyFoundation01/Blueprints/SandboxCharacter_Mover',
                '/GASPEnemyFoundation01/Blueprints/SandboxCharacter_Mover_ABP',
                '/GASPEnemyFoundation01/Blueprints/AnimNotifies/BP_AnimNotify_FoleyEvent',
                '/Game/InfimaGames/TacticalFPSAnimations/Common/Core/Characters/BP_TFA_BaseCharacter',
                '/Game/InfimaGames/TacticalFPSAnimations/Common/Core/Characters/ABP_TFA_FP_BaseCharacter']
            registry = u.AssetRegistryHelpers.get_asset_registry()
            assets = registry.get_assets_by_path('/Game', recursive=True) + registry.get_assets_by_path('/GASPEnemyFoundation01', recursive=True)
            result['audio_assets'] = [str(a.package_name) for a in assets if str(a.asset_class_path.asset_name) in ('SoundWave','SoundCue','MetaSoundSource') and any(t in str(a.package_name).lower() for t in ['step','land','foley'])]
            # Include the actual game pawn and all local foley implementation Blueprints.
            paths += [str(a.package_name) for a in assets if str(a.asset_class_path.asset_name) == 'Blueprint' and any(t in str(a.package_name) for t in ['BP_OpeningLobby','BP_TFA_FP','Foley','Notify'])]
            if operation == 'audio_player':
                paths = [p for p in paths if p.startswith('/Game/')]
            result['blueprints'] = []
            for path in sorted(set(paths)):
                if not u.EditorAssetLibrary.does_asset_exist(path):
                    continue
                bp = u.load_asset(path)
                result['blueprints'].append(dict(path=path, graphs=graphs(bp)))
        elif operation == 'player_notifies':
            rows = []
            for asset in u.AssetRegistryHelpers.get_asset_registry().get_assets_by_path('/Game/InfimaGames', recursive=True):
                if str(asset.asset_class_path.asset_name) not in ('AnimSequence','AnimMontage'):
                    continue
                anim = asset.get_asset()
                events = []
                for event in u.AnimationLibrary.get_animation_notify_events(anim):
                    notify = event.get_editor_property('notify')
                    sound = notify.get_editor_property('sound') if isinstance(notify, u.AnimNotify_PlaySound) else None
                    events.append(dict(name=str(event.get_editor_property('notify_name')), type=notify.get_class().get_path_name() if notify else None,
                        sound=sound.get_path_name() if sound else None, path=notify.get_path_name() if notify else None))
                if events:
                    rows.append(dict(path=str(asset.package_name), events=events))
            result['animations'] = rows
        elif operation == 'asset_wiring':
            rows=[]
            for path in ['/Game/InfimaGames/TacticalFPSAnimations/Common/Core/Characters/ABP_TFA_FP_BaseCharacter',
                '/GASPEnemyFoundation01/Blueprints/SandboxCharacter_Mover_ABP']:
                bp=u.load_asset(path)
                cls=bp.generated_class()
                cdo=u.get_default_object(cls)
                rows.append(dict(path=path, generated_class=cls.get_path_name(),
                    purchased_arms_host=isinstance(cdo,u.PurchasedArmsAnimInstance),
                    gasp_rifle_host=isinstance(cdo,u.GASPALSRifleAnimInstance),
                    uses_native_footstep_filter=isinstance(cdo,u.CombatLocomotionAnimInstance)))
            result['blueprints']=rows
            assert all(row['uses_native_footstep_filter'] for row in rows),rows
        elif operation not in ('before','after','close','close_diagnostic'):
            raise ValueError(operation)
        result['after'] = state()
        assert result['after'] == current, result['after']
        with (OUT / ('editor-'+operation+'.json')).open('x', encoding='utf-8') as stream:
            json.dump(result, stream, indent=2)
        if operation in ('close','close_diagnostic'):
            u.SystemLibrary.quit_editor()
        return json.dumps(dict(file='editor-'+operation+'.json', state=current))


registration = Registration([SensesTools])
registration.register()
