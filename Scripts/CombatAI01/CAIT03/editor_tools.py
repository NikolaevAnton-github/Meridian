"""Guarded read-only pose wiring and native reload through official Epic MCP."""
from pathlib import Path
import json, unreal as u, toolset_registry
from toolset_registry.registration import Registration
ROOT=Path('D:/devgames/MeridianSquad')
OUT=ROOT/'Saved/CombatAI01/CAI-T03/Worker/Candidate01'
def state():
    project=Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
    assert project.resolve()==ROOT.resolve()
    world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
    return dict(project=str(project),engine=u.SystemLibrary.get_engine_version(),map=world.get_path_name() if world else None,
        pie=[w.get_path_name() for w in u.EditorLevelLibrary.get_pie_worlds(False)],
        dirty=[p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_content_packages()]+[p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_map_packages()])
@u.uclass()
class MobileLeanTools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def inspect(operation: str) -> str:
        current=state()
        assert operation in ('before','close','after')
        assert current['map']=='/Game/Maps/L_OpeningLobby_PainterStone01.L_OpeningLobby_PainterStone01'
        assert not current['pie'] and not current['dirty'],current
        if operation!='close':
            bp=u.load_asset('/GASPEnemyFoundation01/Blueprints/SandboxCharacter_Mover_ABP')
            ed=u.BlueprintGraphEditor.get_graph_editor(u.BlueprintEditorLibrary.find_graph(bp,'AnimGraph'))
            current['parent']=u.BlueprintEditorLibrary.get_blueprint_parent_class(bp).get_path_name()
            current['errors']=str(ed.list_nodes_with_errors())
            nodes=list(ed.list_all_nodes())
            # Export current graph without compilation, package mutation or playback.
            current['nodes']=[dict(name=n.get_name(),text=n.export_text()) for n in nodes if hasattr(n,'export_text')]
            current['node_names']=[n.get_name() for n in nodes]
            for n in nodes:
                if n.get_class().get_name()=='AnimGraphNode_ModifyBone':
                    data=n.get_editor_property('node')
                    current.setdefault('modify_bones',[]).append(dict(name=n.get_name(),bone=str(data.get_editor_property('bone_to_modify').get_editor_property('bone_name')),
                        mode=str(data.get_editor_property('rotation_mode')),space=str(data.get_editor_property('rotation_space')),
                        rotation_sources=[str(p) for p in n.find_input_pin('Rotation').list_connected_pins()],
                        pose_outputs=[str(p) for p in n.find_output_pin('Pose').list_connected_pins()]))
            if operation=='after':
                from Scripts.CombatAI01.CAIT03.pose_checks import check_pose
                current['native_pose_checks']=check_pose()
        with (OUT/('editor-'+operation+'.json')).open('x',encoding='utf-8') as f: json.dump(current,f,indent=2)
        if operation=='close': u.SystemLibrary.quit_editor()
        return json.dumps({k:v for k,v in current.items() if k not in ('nodes','node_names')})
registration=Registration([MobileLeanTools]); registration.register()
