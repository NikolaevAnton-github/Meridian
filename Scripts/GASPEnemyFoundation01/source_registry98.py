"""Registry-only source inspection: no asset loads, saves, or source edits."""
import collections
import json
from pathlib import Path
import unreal as u

OUT = Path('D:/devgames/MeridianSquad/Saved/CombatSlice01/GASPEnemyFoundation01/Worker')
registry = u.AssetRegistryHelpers.get_asset_registry()
registry.search_all_assets(True)
registry.scan_paths_synchronous(['/Game'], force_rescan=True)
seed = '/Game/Blueprints/SandboxCharacter_Mover_Ragdoll'
hard = u.AssetRegistryDependencyOptions(include_hard_package_references=True,
    include_soft_package_references=False, include_searchable_names=False,
    include_soft_management_references=False, include_hard_management_references=False)
soft = u.AssetRegistryDependencyOptions(include_hard_package_references=False,
    include_soft_package_references=True, include_searchable_names=False,
    include_soft_management_references=False, include_hard_management_references=False)
queue = collections.deque([seed])
seen = set()
records = []
while queue:
    package = queue.popleft()
    if package in seen:
        continue
    seen.add(package)
    assets = registry.get_assets_by_package_name(package, include_only_on_disk_assets=True)
    hard_refs = sorted(str(p) for p in registry.get_dependencies(package, hard) or [])
    soft_refs = sorted(str(p) for p in registry.get_dependencies(package, soft) or [])
    records.append(dict(package=package, assets=[dict(name=str(a.asset_name),
        asset_class=str(a.asset_class_path), tags={k:str(a.get_tag_value(k)) for k in
            ['ParentClass','NativeParentClass','GeneratedClass','Skeleton','PreviewSkeletalMesh','BlueprintType']
            if a.get_tag_value(k) is not None}) for a in assets],
        hard=hard_refs, soft=soft_refs))
    queue.extend(p for p in hard_refs + soft_refs if p.startswith('/Game/'))
missing = [r['package'] for r in records if not r['assets']]
result = dict(project=u.Paths.get_project_file_path(), engine=u.SystemLibrary.get_engine_version(),
    source='Unreal AssetRegistry, on-disk dependencies; assets not loaded', seed=seed, missing=missing, packages=records)
with (OUT / 'source-registry-full01.json').open('x', encoding='utf-8') as stream:
    json.dump(result, stream, indent=2)
u.log('MSQ98_REGISTRY_DONE packages=' + str(len(records)) + ' missing=' + str(len(missing)))
