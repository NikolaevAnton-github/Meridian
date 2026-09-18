"""Correct the Blueprint default used by CharacterMovement's clearance/uncrouch."""
import hashlib
import json
import shutil
import unreal as u
from adapt import ROOT,OUT,BASE
from editor_toolset.toolsets.blueprint import BlueprintTools as BP
from stage1_tools import state

def run():
    assert not state()['pie'] and not state()['dirty_maps']
    package=BASE+'Common/Core/Characters/BP_TFA_BaseCharacter'
    source=ROOT/('Content/'+package.removeprefix('/Game/')+'.uasset')
    saved=OUT/'Correction01/Before/BP_TFA_BaseCharacter.uasset'
    assert not saved.exists()
    saved.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,saved)
    bp=u.load_asset(package)
    def dimensions():
        c=u.get_default_object(bp.generated_class()).capsule_component
        return [c.get_unscaled_capsule_radius(),c.get_unscaled_capsule_half_height()]
    before=dimensions()
    c=u.get_default_object(bp.generated_class()).capsule_component
    c.set_editor_property('capsule_radius',34.)
    c.set_editor_property('capsule_half_height',88.)
    BP.compile_blueprint(bp)
    after=dimensions()
    assert after==[34.,88.],after
    assert u.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    result={'before':before,'after_compile':after,'after_save':dimensions(),
        'before_sha256':hashlib.sha256(saved.read_bytes()).hexdigest(),'after_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
    (OUT/'Correction01/capsule-default.json').write_text(json.dumps(result,indent=2))
    return result
