import json
from pathlib import Path
import unreal as u

OUT=Path('D:/devgames/MeridianSquad/Saved/DemoTiledColumn01/Correction02')
DEST='/Game/Experiments/DemoTiledColumn01/Correction02/'
MAP='/Game/Maps/L_OpeningLobby_PainterStone01'
editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert editor.get_editor_world().get_path_name().split('.')[0]==MAP
assert not editor.get_game_world()
assert not u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
old=[a for a in actors.get_all_level_actors() if a.get_actor_label()=='EXP_DemoTiledColumn01']
assert len(old)==1
old=old[0]
assert old.get_editor_property('DataAsset').get_path_name()=='/Game/Experiments/DemoTiledColumn01/DA_DemoTiledColumn01.DA_DemoTiledColumn01'

assert not u.EditorAssetLibrary.does_asset_exist(DEST+'M_StoneUV02')
material=u.AssetToolsHelpers.get_asset_tools().create_asset('M_StoneUV02',DEST.rstrip('/'),u.Material,u.MaterialFactoryNew())
lib=u.MaterialEditingLibrary
def tex(name,sampler):
    node=lib.create_material_expression(material,u.MaterialExpressionTextureSample)
    node.set_editor_property('texture',u.load_asset('/Game/OpeningLobby/PainterStone01/Textures/T_PainterStone01_'+name))
    node.set_editor_property('sampler_type',sampler)
    return node
base=tex('BaseColor',u.MaterialSamplerType.SAMPLERTYPE_COLOR)
normal=tex('Normal',u.MaterialSamplerType.SAMPLERTYPE_NORMAL)
orm=tex('ORM',u.MaterialSamplerType.SAMPLERTYPE_MASKS)
lib.connect_material_property(base,'RGB',u.MaterialProperty.MP_BASE_COLOR)
lib.connect_material_property(normal,'RGB',u.MaterialProperty.MP_NORMAL)
lib.connect_material_property(orm,'R',u.MaterialProperty.MP_AMBIENT_OCCLUSION)
lib.connect_material_property(orm,'G',u.MaterialProperty.MP_ROUGHNESS)
lib.connect_material_property(orm,'B',u.MaterialProperty.MP_METALLIC)
lib.set_material_usage(material,u.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES)
lib.recompile_material(material)
assert u.EditorAssetLibrary.save_loaded_asset(material)
result=json.loads(u.NGDColumnAuthoring.build_demo_column_cladding(str(OUT/'cladding.json')))
assert 'error' not in result,result
(OUT/'created.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
assert u.EditorAssetLibrary.save_directory(DEST,only_if_is_dirty=True,recursive=True)
data=u.EditorAssetLibrary.duplicate_asset('/Game/NextGenDestruction/Blueprints/DataAssets/Destructible/DA_Pillar_Large_Concrete_Square',DEST+'DA_DemoTiledColumn02')
assert data
assert u.EditorAssetLibrary.save_loaded_asset(data)
actor=u.NGDTools.spawn_prop(editor.get_editor_world(),data,old.get_actor_location(),old.get_actor_rotation(),'EXP_DemoTiledColumn01_Correction02')
assert actor
actor.set_actor_scale3d(u.Vector(2.364,2.364,3.6))
actor.set_folder_path('Experiments/DemoTiledColumn01')
actor.tags=list(actor.tags)+['DemoTiledColumn01_Correction02']
assert actors.destroy_actor(old)
actor.set_actor_label('EXP_DemoTiledColumn01')
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
actors.set_selected_level_actors([actor])
editor.set_level_viewport_camera_info(u.Vector(700,-850,260),u.Rotator(8,130,0))
result.update(actor=actor.get_path_name(),label=actor.get_actor_label(),data_asset=data.get_path_name(),
    size_cm=[240,240,1800],runtime_tested=False)
(OUT/'placed.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
