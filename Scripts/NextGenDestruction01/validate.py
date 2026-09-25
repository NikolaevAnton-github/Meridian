"""Load, compile and resave the purchased toolkit in the current UE editor only."""
import json
from pathlib import Path
import unreal as u

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT / 'Saved/NextGenDestruction01'
PACKAGE = '/Game/NextGenDestruction'

assert Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())).resolve() == ROOT.resolve()
assert u.SystemLibrary.get_engine_version().startswith('5.8.')
editor = u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert not editor.get_game_world(), 'Stop PIE before package conversion.'
dirty = list(u.EditorLoadingAndSavingUtils.get_dirty_map_packages()) + list(u.EditorLoadingAndSavingUtils.get_dirty_content_packages())
assert not dirty, 'Save or discard existing editor changes before conversion: ' + ', '.join(p.get_path_name() for p in dirty)
registry = u.AssetRegistryHelpers.get_asset_registry()
registry.scan_paths_synchronous([PACKAGE], force_rescan=True)
assets = registry.get_assets_by_path(PACKAGE, recursive=True)
# The vendor 5.4 package retains five soft self-references from its old folder.
# Resolve them through Unreal's serializer rather than modifying binary files.
repairs = {
    'Blueprints/Actors/BP_DemoDisplay': 'Demo/Blueprints/BP_DemoDisplay',
    'Blueprints/Actors/BP_DestructionField': 'Blueprints/Actors/BP_DestructionField',
    'Blueprints/Actors/BP_Pickup_Rifle': 'Blueprints/Actors/BP_Pickup_Rifle',
    'Blueprints/Actors/BP_WeaponBase': 'Blueprints/Actors/BP_WeaponBase',
    'Blueprints/DataAssets/Destructible/PDA_ChaosBreakable': 'Blueprints/DataAssets/Destructible/PDA_ChaosBreakable',
}
redirects = {}
packages = []
for old, new in repairs.items():
    name = old.rsplit('/', 1)[1]
    redirects[u.SoftObjectPath('/Game/ChaosSetup/' + old + '.' + name)] = u.SoftObjectPath(PACKAGE + '/' + new + '.' + name)
    packages.append(u.load_asset(PACKAGE + '/' + new).get_outermost())
u.AssetToolsHelpers.get_asset_tools().rename_referencing_soft_object_paths(packages, redirects)
report = {'engine': u.SystemLibrary.get_engine_version(), 'assets': len(assets),
          'classes': {}, 'blueprints': [], 'maps': [], 'failed_loads': [],
          'missing_dependencies': [], 'external_dependencies': [], 'save_failures': []}
options = u.AssetRegistryDependencyOptions(include_soft_package_references=True, include_hard_package_references=True)
dependencies = set()
map_paths = []
for data in assets:
    package = str(data.package_name)
    cls = str(data.asset_class_path.asset_name)
    report['classes'][cls] = report['classes'].get(cls, 0) + 1
    dependencies.update(str(x) for x in registry.get_dependencies(data.package_name, options))
    if cls == 'World':
        map_paths.append(package)
        continue
    try:
        obj = data.get_asset()
        if not obj:
            report['failed_loads'].append(package)
            continue
        if isinstance(obj, u.Blueprint):
            u.BlueprintEditorLibrary.compile_blueprint(obj)
            report['blueprints'].append({'path': package, 'status': str(obj.get_editor_property('status'))})
        if not u.EditorAssetLibrary.save_loaded_asset(obj, only_if_is_dirty=False):
            report['save_failures'].append(package)
    except Exception as exc:
        report['failed_loads'].append({'path': package, 'error': str(exc)})
    (OUT/'conversion-progress.json').write_text(json.dumps(report, indent=2))

registry.scan_paths_synchronous([PACKAGE], force_rescan=True)
dependencies = {str(dep) for data in assets for dep in registry.get_dependencies(data.package_name, options)}
for dep in sorted(dependencies):
    if dep.startswith(('/Script/', '/Temp/')):
        continue
    if not dep.startswith(PACKAGE + '/'):
        report['external_dependencies'].append(dep)
    if not registry.get_assets_by_package_name(dep):
        report['missing_dependencies'].append(dep)

for package in sorted(map_paths):
    world = u.EditorLoadingAndSavingUtils.load_map(package)
    if not world:
        report['failed_loads'].append(package)
        continue
    settings = world.get_world_settings()
    mode = settings.get_editor_property('default_game_mode')
    actors = u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
    report['maps'].append({'path': package, 'actors': len(actors),
                           'game_mode': mode.get_path_name() if mode else None})
    if not u.EditorLoadingAndSavingUtils.save_map(world, package):
        report['save_failures'].append(package)

report['passed'] = not (report['failed_loads'] or report['missing_dependencies'] or report['save_failures']) and all('ERROR' not in row['status'].upper() for row in report['blueprints'])
(OUT/'conversion.json').write_text(json.dumps(report, indent=2))
u.EditorLoadingAndSavingUtils.load_map(PACKAGE + '/Maps/DemoMap')
u.log('NEXT_GEN_DESTRUCTION_CONVERSION ' + json.dumps({k:v for k,v in report.items() if k in ('engine','assets','classes','passed','failed_loads','missing_dependencies','save_failures')}))
