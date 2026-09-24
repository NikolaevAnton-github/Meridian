"""Only the final graph/native seams changed since the passing asset checks."""
import json
import unreal as u
from Scripts.GASPALSLocomotion01.editor import OUT,state,defaults,graphs

def run():
    from toolset_registry.helpers import compile_blueprint
    before=state()
    assert not before['pie'] and not before['dirty'],before
    bp=u.load_asset('/GASPALS/Blueprints/ABP_SandboxCharacter')
    if 'UP_TO_DATE' not in str(bp.get_editor_property('status')):
        compile_blueprint(bp,False)
    errors=[]
    for g in u.BlueprintEditorLibrary.list_graphs(bp):
        errors.extend(u.BlueprintGraphEditor.get_graph_editor(g).list_nodes_with_errors())
    assert not errors,errors
    child=u.load_asset('/Game/Development/GASPALSLocomotion01/Candidate01/BP_GASPALSEnemy_Candidate01')
    cdo=u.get_default_object(child.generated_class())
    assert cdo.mesh.anim_class==bp.generated_class()
    values={}
    for name,expected in [('msq.GASPALS.OffsetRootTranslationRadius',30),
        ('msq.GASPALS.ThreadSafeAnimationUpdate',1),('msq.GASPALS.ExperimentalStateMachine',0),
        ('msq.GASPALS.ExperimentalStateMachineDebug',0)]:
        values[name]=u.SystemLibrary.get_console_variable_float_value(name)
        assert values[name]==expected,(name,values[name])
    fixture=u.get_default_object(u.GASPALSLocomotionFixture.static_class())
    legacy_path=defaults(fixture)['FoundationPhysicsTick'].split("'")[1]
    legacy=u.find_object(None,legacy_path)
    assert legacy,legacy_path
    tick=legacy.get_editor_property('primary_component_tick')
    assert not tick.get_editor_property('start_with_tick_enabled')
    result=dict(before=before,anim_compile_status=str(bp.get_editor_property('status')),errors=errors,
        source_console_values=values,legacy_physics_tick=defaults(legacy),
        child_parent=u.BlueprintEditorLibrary.get_blueprint_parent_class(child).get_path_name(),
        native_parent=u.BlueprintEditorLibrary.get_blueprint_parent_class(bp).get_path_name(),after=state())
    assert not result['after']['dirty'],result['after']
    (OUT/'final-asset-check.json').write_text(json.dumps(result,indent=2))
    return dict(passed=True,console_values=values,legacy_physics_tick_disabled=True,after=result['after'])
