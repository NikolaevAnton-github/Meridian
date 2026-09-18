"""Bounded MSQ-66 inspection and shooting checks through official Epic MCP."""
import importlib
import json
import sys
import time
import traceback
from pathlib import Path

import unreal as u
import toolset_registry
from toolset_registry.registration import Registration

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/PurchasedArms06/Worker'
for folder in ['OpeningLobby', 'PurchasedArms02']:
    sys.path.insert(0, str(ROOT / 'Scripts' / folder))
from stage1_tools import state
import verify02


def write(name, value):
    path = OUT / (name + '.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    assert not path.exists(), path
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')
    return value


def action(operation, argument):
    if operation == 'reload_asset':
        current = state()
        assert not current['pie'] and not current['dirty_maps'] and not current['dirty_content'], current
        asset = u.load_asset('/Game/InfimaGames/TacticalFPSAnimations/Common/VFX/Systems/NS_TFA_MuzzleFlash')
        u.get_editor_subsystem(u.AssetEditorSubsystem).close_all_editors_for_asset(asset)
        changed, error = u.EditorLoadingAndSavingUtils.reload_packages(
            [asset.get_package()], u.ReloadPackagesInteractionMode.ASSUME_POSITIVE)
        assert changed and not str(error), (changed, str(error))
        return write('saved-package-reload', {'reloaded': changed, 'error': str(error), 'state': state()})
    if operation == 'prepare_capture':
        current = state()
        assert not current['pie'] and not current['dirty_maps'] and not current['dirty_content'], current
        asset = u.load_asset('/Game/InfimaGames/TacticalFPSAnimations/Common/VFX/Systems/NS_TFA_MuzzleFlash')
        u.get_editor_subsystem(u.AssetEditorSubsystem).close_all_editors_for_asset(asset)
        return state()
    if operation == 'close':
        current = state()
        assert not current['pie'] and not current['dirty_maps'] and not current['dirty_content'], current
        write('editor-before-close-' + argument, current)
        u.SystemLibrary.quit_editor()
        return {'close_requested': True}
    if operation == 'state':
        return write('editor-state-' + argument, state())
    if operation == 'source':
        from editor_toolset.toolsets.material import MaterialTools
        base = '/Game/InfimaGames/TacticalFPSAnimations/Common/VFX/'
        mat = u.load_asset(base + 'Materials/M_TFA_VFX_MuzzleFlash')
        graph = []
        for expression in u.MaterialEditingLibrary.get_material_expressions(mat):
            graph.append({'path': expression.get_path_name(), 'class': expression.get_class().get_name(),
                          'inputs': str(MaterialTools.get_expression_inputs(mat, expression))})
        niagara = u.load_asset(base + 'Systems/NS_TFA_MuzzleFlash')
        emitter = u.load_asset(base + 'Emitters/NE_TFA_MuzzleFlash_Flame')
        result = {'state': state(), 'material_graph': graph,
                  'niagara_methods': [n for n in dir(niagara) if not n.startswith('_')],
                  'emitter_methods': [n for n in dir(emitter) if not n.startswith('_')],
                  'niagara_classes': [n for n in dir(u) if 'Niagara' in n and any(
                      w in n for w in ['Editor', 'Input', 'Context', 'Script', 'Library'])]}
        write('source-' + argument, result)
        return result
    if operation == 'verify':
        assert verify02.RUN is None or verify02.RUN['done']
        importlib.reload(verify02)
        original_sample = verify02.sample
        def sample():
            # Reuse the established lobby driver's held-input refresh for ADS.
            # Platform mouse polling can release a one-shot synthetic press while
            # the native input driver still intends the button to remain held.
            if 'RightMouseButton' in verify02.RUN['held']:
                verify02.RUN['pawn'].probe_key('RightMouseButton', 1, True)
            row = original_sample()
            row['capture_wall_monotonic'] = time.monotonic()
            return row
        verify02.sample = sample
        verify02.OUT = OUT
        return verify02.start(argument)
    if operation == 'verify_status':
        result = verify02.status()
        if result['done'] and verify02.RUN and not result['error']:
            aimed = [r for r in verify02.RUN['rows'] if 6.1 <= r['t'] <= 7.1]
            if not aimed or not all(r['aim_requested'] and abs(r['view_fov'] - 78) < .1 for r in aimed):
                result['error'] = 'ADS input was not held throughout the intended aimed burst; take is not acceptance evidence.'
        return result
    if operation == 'performance':
        obj = u.get_default_object(u.load_class(None, '/Script/UnrealEd.EditorPerformanceSettings'))
        path = OUT / 'performance-before.json'
        if not path.exists():
            write('performance-before', {'throttle': obj.get_editor_property('bThrottleCPUWhenNotForeground')})
        value = json.loads(path.read_text())['throttle'] if argument == 'restore' else False
        obj.set_editor_property('bThrottleCPUWhenNotForeground', value)
        return {'throttle': value}
    raise ValueError(operation)


@u.uclass()
class PurchasedArms06Tools(u.ToolsetDefinition):
    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, argument: str) -> str:
        try:
            return json.dumps(action(operation, argument))
        except Exception:
            return json.dumps({'error': traceback.format_exc()})


registration = Registration([PurchasedArms06Tools])
registration.register()
