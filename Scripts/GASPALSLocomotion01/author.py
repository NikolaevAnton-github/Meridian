"""MSQ-121 source-preserving child defaults and one additive tactical lean node."""
from pathlib import Path
import hashlib,json,shutil
import unreal as u
from Scripts.GASPALSLocomotion01.editor import ROOT,OUT,graphs

CHAR='/GASPALS/Blueprints/CBP_SandboxCharacter'
ANIM='/GASPALS/Blueprints/ABP_SandboxCharacter'
DEST='/Game/Development/GASPALSLocomotion01/Candidate01/BP_GASPALSEnemy_Candidate01'

def connect(a,b):
    assert a and b and a.try_create_connection(b),(str(a),str(b))

def run():
    from toolset_registry.helpers import compile_blueprint
    assert not u.EditorLevelLibrary.get_pie_worlds(False)
    before=ROOT/'Assets/Source/GASPALSLocomotion01/Before'
    before.mkdir(exist_ok=True)
    source_file=ROOT/'Plugins/GASPALS/Content/Blueprints/ABP_SandboxCharacter.uasset'
    backup=before/'ABP_SandboxCharacter.uasset'
    assert not backup.exists(),'Authoring baseline is immutable; use a new correction script/revision'
    shutil.copy2(source_file,backup)
    bp=u.load_asset(ANIM)
    original=graphs(bp)
    (OUT/'anim-graph-before.json').write_text(json.dumps(original,indent=2))
    u.BlueprintEditorLibrary.reparent_blueprint(bp,u.GASPALSLocomotionAnimInstance.static_class())
    compile_blueprint(bp,False)
    ed=u.BlueprintGraphEditor.get_graph_editor(u.BlueprintEditorLibrary.find_graph(bp,'AnimGraph'))
    root=next(n for n in ed.list_all_nodes() if n.get_name()=='AnimGraphNode_Root_0')
    result=root.find_input_pin('Result')
    inputs=result.list_connected_pins()
    assert len(inputs)==1
    upstream=inputs[0]
    created=[]
    def create(kind):
        node=ed.create_node_from_name(kind,u.Vector2D(9000+len(created)*300,0),[])
        assert node,kind
        created.append(node)
        return node
    to_component=create('Animation|ConvertSpaces|LocalToComponent')
    rotate=create('Animation|SkeletalControls|Transform(Modify)Bone')
    to_local=create('Animation|ConvertSpaces|ComponentToLocal')
    data=rotate.get_editor_property('node')
    bone=u.BoneReference()
    bone.set_editor_property('bone_name','spine_01')
    data.set_editor_property('bone_to_modify',bone)
    data.set_editor_property('rotation_mode',u.BoneModificationMode.BMM_ADDITIVE)
    data.set_editor_property('rotation_space',u.BoneControlSpace.BCS_COMPONENT_SPACE)
    rotate.set_editor_property('node',data)
    rotation=ed.add_get_member_variable_node('MSQLeanRotation')
    connect(rotation.find_output_pin('MSQLeanRotation'),rotate.find_input_pin('Rotation'))
    result.break_pin_links()
    connect(upstream,to_component.find_input_pin('LocalPose'))
    connect(to_component.find_output_pin('ComponentPose'),rotate.find_input_pin('ComponentPose'))
    connect(rotate.find_output_pin('Pose'),to_local.find_input_pin('ComponentPose'))
    connect(to_local.find_output_pin('Pose'),result)
    ed.add_comment_to_nodes('MSQ-121: existing tactical torso lean after the complete source pose. Zero during source ragdoll/get-up.',created+[rotation])
    cv=u.BlueprintGraphEditor.get_graph_editor(u.BlueprintEditorLibrary.find_graph(bp,'Update_CVarDrivenVariables'))
    radius=next(n for n in cv.list_all_nodes() if n.get_name()=='K2Node_CallFunction_0')
    pin=radius.find_input_pin('VariableName')
    assert pin.get_pin_value()=='DDCvar.OffsetRootBone.TranslationRadius'
    pin.set_pin_value('msq.GASPALS.OffsetRootTranslationRadius')
    compile_blueprint(bp,False)
    assert u.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    factory=u.BlueprintFactory()
    factory.set_editor_property('parent_class',u.EditorAssetLibrary.load_blueprint_class(CHAR))
    assert not u.EditorAssetLibrary.does_asset_exist(DEST)
    child=u.AssetToolsHelpers.get_asset_tools().create_asset(DEST.rsplit('/',1)[1],DEST.rsplit('/',1)[0],u.Blueprint,factory)
    assert child
    cdo=u.get_default_object(child.generated_class())
    for name,label in [('OverlayBase','MASCULINE'),('OverlayPose','RIFLE')]:
        enum_type=type(cdo.get_editor_property(name))
        value=getattr(enum_type,label)
        cdo.set_editor_property(name,value)
    cdo.set_editor_property('auto_possess_ai',u.AutoPossessAI.DISABLED)
    cdo.set_editor_property('auto_possess_player',u.AutoReceiveInput.DISABLED)
    compile_blueprint(child,False)
    assert u.EditorAssetLibrary.save_loaded_asset(child,only_if_is_dirty=False)
    result=dict(character=child.get_path_name(),parent=CHAR,anim=ANIM,
        anim_parent=u.BlueprintEditorLibrary.get_blueprint_parent_class(bp).get_path_name(),
        source_anim_sha256=hashlib.sha256(backup.read_bytes()).hexdigest(),
        derived_anim_sha256=hashlib.sha256(source_file.read_bytes()).hexdigest(),
        defaults=json.loads(u.GASPALSLocomotionLibrary.inspect_properties(cdo)))
    (OUT/'asset-authoring01.json').write_text(json.dumps(result,indent=2))
    (OUT/'anim-graph-after.json').write_text(json.dumps(graphs(bp),indent=2))
    return {k:v for k,v in result.items() if k!='defaults'}
