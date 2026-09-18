"""Restore the supplied aimed FOV in the adapted character's active camera path."""
import json
import unreal as u
from adapt import BASE, OUT
from editor_toolset.toolsets.blueprint import BlueprintTools as BP
from stage1_tools import state

def run():
    assert not state()['pie'] and not state()['dirty_maps']
    bp = u.load_asset(BASE+'Common/Core/Characters/BP_TFA_BaseCharacter')
    cdo = u.get_default_object(bp.generated_class())
    cdo.set_editor_property('AimedFOV', 78.)
    u.EditorAssetLibrary.save_loaded_asset(bp)
    result = {'default_fov':cdo.get_editor_property('DefaultFOV'), 'aimed_fov':cdo.get_editor_property('AimedFOV')}
    (OUT/'camera-refinement.json').write_text(json.dumps(result,indent=2))
    return result
