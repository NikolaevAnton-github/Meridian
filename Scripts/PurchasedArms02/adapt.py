"""Adapt staged vendor copies; immutable originals and rollback bytes stay separate."""
import hashlib
import json
import shutil
from pathlib import Path
import unreal as u
from editor_toolset.toolsets.blueprint import BlueprintTools as BP
from stage1_tools import state

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/PurchasedArms02/Worker'
BASE = '/Game/InfimaGames/TacticalFPSAnimations/'

def preserve(package):
    src = ROOT / ('Content/' + package.removeprefix('/Game/') + '.uasset')
    dst = OUT / 'Rollback' / src.relative_to(ROOT)
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

def disconnect(node):
    info = BP.get_node_infos([node])[0]
    for p in info.output_pins:
        for q in p.connected_pins:
            BP.break_pins(p.pin_id, q)

def delete_bypass(node):
    info = BP.get_node_infos([node])[0]
    incoming = [q for p in info.input_pins if p.type_id == 'Exec' for q in p.connected_pins]
    outgoing = [q for p in info.output_pins if p.type_id == 'Exec' for q in p.connected_pins]
    BP.delete_node(node)
    if len(outgoing) == 1:
        for src in incoming:
            BP.connect_pins(src, outgoing[0])

def run():
    initial = state()
    assert not initial['pie'] and not initial['dirty_maps'], initial
    character_path = BASE + 'Common/Core/Characters/BP_TFA_BaseCharacter'
    preserve(character_path)
    character = u.load_asset(character_path)
    blank = {'InitialSetup','SpawnUI','UpdateCameraPerspective','ThirdPersonCameraZoom',
        'ThirdPersonCameraUpdate','ThirdPersonCameraLook','SimulateVelocity','SetCapsuleHalfHeight',
        'ToggleCameraPerspective','EnableFirstPersonPerspective','EnableThirdPersonPerspective',
        'EnableGunCameraPerspective','EnableBodycamPerspective','ConsoleCommands'}
    disabled_inputs = ['ToggleTutorialText','ToggleCameraPerspective','ToggleCameraAnimation',
        'QuitGame','ToggleUI','Zoom','FreezeTime','Look','Jump']
    removed = []
    for graph in BP.list_graphs(character):
        editor = u.BlueprintGraphEditor.get_graph_editor(graph)
        if graph.get_name() in blank:
            editor.remove_nodes([n for n in editor.list_all_nodes() if not n.get_class().get_name().startswith('K2Node_Function')])
        else:
            for node in list(editor.list_all_nodes()):
                title = str(node.get_node_title())
                if title in ['Event BeginPlay', 'Event Tick'] or any('IA_TFA_' + s in title for s in disabled_inputs):
                    disconnect(node)
                info = BP.get_node_infos([node])[0]
                if any('WBP_TFA_' in p.value or 'WBP TFA' in p.type_id or 'WBPTFA' in info.type_id
                    or 'WidgetBP' in p.name or 'WidgetBodycamOverlay' in p.name
                    for p in [*info.input_pins, *info.output_pins]):
                    removed.append(node.get_path_name())
                    delete_bypass(node)
    for name in ['WidgetBP','WidgetBodycamOverlay']:
        BP.remove_variable(character, name)
    BP.set_parent(character, u.OpeningLobbyCharacter.static_class())
    BP.compile_blueprint(character)
    data_path = BASE + 'Weapons/AssaultRifle/Demo/Data/DA_TFA_AssaultRifle'
    preserve(data_path)
    data = u.load_asset(data_path)
    data.set_editor_property('FP_Mesh', u.load_asset(BASE + 'Common/Characters/Mannequins/Meshes/SKM_FP_Manny_Simple'))
    config = u.load_asset(BASE + 'Common/Core/Configs/BP_TFA_BaseConfig')
    cleared = []
    for name in BP.list_variables(config):
        if name.startswith('TP_'):
            value = data.get_editor_property(name)
            if isinstance(value, u.Array):
                data.set_editor_property(name, [])
            else:
                data.set_editor_property(name, None)
            cleared.append(name)
    cdo = u.get_default_object(character.generated_class())
    # CharacterMovement restores these class defaults when uncrouching.
    cdo.capsule_component.set_editor_property('capsule_radius', 34.)
    cdo.capsule_component.set_editor_property('capsule_half_height', 88.)
    cdo.set_editor_property('WeaponConfig', data)
    cdo.set_editor_property('DefaultFOV', 90)
    cdo.set_editor_property('AimedFOV', 90)
    cdo.mesh.set_skeletal_mesh_asset(data.get_editor_property('FP_Mesh'))
    u.EditorAssetLibrary.save_loaded_asset(character)
    u.EditorAssetLibrary.save_loaded_asset(data)
    # Reuse the source graph evaluation and slot pipeline; native code only records evaluated frames.
    for path in ['Common/Core/Characters/ABP_TFA_FP_BaseCharacter',
        'Weapons/AssaultRifle/Meshes/ABP_TFA_AR', 'Weapons/AssaultRifle/Meshes/ABP_TFA_AR_Magazine']:
        preserve(BASE + path)
        bp = u.load_asset(BASE + path)
        BP.set_parent(bp, u.PurchasedArmsAnimInstance.static_class())
        BP.compile_blueprint(bp)
        u.EditorAssetLibrary.save_loaded_asset(bp)
    mapping_path = BASE + 'Common/Core/Inputs/IMC_TFA_Default'
    preserve(mapping_path)
    mapping = u.load_asset(mapping_path)
    for suffix in [*disabled_inputs, 'Prone']:
        mapping.unmap_all_keys_from_action(u.load_asset(BASE + 'Common/Core/Inputs/IA_TFA_' + suffix))
    u.EditorAssetLibrary.save_loaded_asset(mapping, only_if_is_dirty=False)
    result = dict(initial=initial, removed_ui_nodes=removed, cleared_tp_config=cleared,
        native_parent=str(BP.get_parent(character)), state=state())
    (OUT / 'adaptation01.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result
