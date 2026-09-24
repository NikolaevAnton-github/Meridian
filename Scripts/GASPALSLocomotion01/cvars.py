"""Complete scoped source animation console defaults before candidate freeze."""
import hashlib,json,shutil
import unreal as u
from Scripts.GASPALSLocomotion01.editor import ROOT,OUT,state,graphs

def run():
    from toolset_registry.helpers import compile_blueprint
    before=state()
    assert not before['pie'] and not before['dirty'],before
    path=ROOT/'Plugins/GASPALS/Content/Blueprints/ABP_SandboxCharacter.uasset'
    backup=OUT/'Construction/ABP_SandboxCharacter-first-authoring.uasset'
    backup.parent.mkdir(exist_ok=True)
    assert not backup.exists()
    shutil.copy2(path,backup)
    bp=u.load_asset('/GASPALS/Blueprints/ABP_SandboxCharacter')
    editor=u.BlueprintGraphEditor.get_graph_editor(u.BlueprintEditorLibrary.find_graph(bp,'Update_CVarDrivenVariables'))
    mapping={
        'DDCVar.ThreadSafeAnimationUpdate.Enable':('msq.GASPALS.ThreadSafeAnimationUpdate',True),
        'DDCVar.ExperimentalStateMachine.Enable':('msq.GASPALS.ExperimentalStateMachine',False),
        'DDCVar.ExperimentalStateMachine.Debug':('msq.GASPALS.ExperimentalStateMachineDebug',False)}
    changed=[]
    for node in editor.list_all_nodes():
        pin=node.find_input_pin('VariableName')
        if pin and pin.get_pin_value() in mapping:
            previous=pin.get_pin_value()
            pin.set_pin_value(mapping[previous][0])
            changed.append(dict(node=node.get_name(),source=previous,destination=mapping[previous][0],default=mapping[previous][1]))
    assert len(changed)==3,changed
    compile_blueprint(bp,False)
    assert not editor.list_nodes_with_errors()
    assert u.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    result=dict(before=before,changed=changed,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),after=state())
    (OUT/'scoped-source-cvars.json').write_text(json.dumps(result,indent=2))
    (OUT/'anim-graph-final.json').write_text(json.dumps(graphs(bp),indent=2))
    return result
