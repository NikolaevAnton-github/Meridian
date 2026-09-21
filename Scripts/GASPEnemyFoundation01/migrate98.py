"""Use Epic's package migration/remapping for the verified seed dependency closure."""
import hashlib
import json
from pathlib import Path
import unreal as u

ROOT = Path('D:/devgames/MeridianSquad')
SOURCE = Path('D:/devgames/GameAnimationSample')
OUT = ROOT / 'Saved/CombatSlice01/GASPEnemyFoundation01/Worker'
DEST = ROOT / 'Plugins/GASPEnemyFoundation01/Content'
DEST.mkdir(parents=True, exist_ok=True)
assert not list(DEST.rglob('*.uasset')), 'Never overwrite an earlier migration attempt'
assert Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())).resolve() == SOURCE.resolve()
assert not u.EditorLoadingAndSavingUtils.get_dirty_content_packages(), 'Source has dirty content: do not autosave'
assert not u.EditorLoadingAndSavingUtils.get_dirty_map_packages(), 'Source has a dirty map: do not autosave'
registry = u.AssetRegistryHelpers.get_asset_registry()
registry.search_all_assets(True)
audit = json.loads((OUT / 'source-registry-full01.json').read_text())
assert not audit['missing']
packages = [r['package'] for r in audit['packages']]
assert all(p.startswith('/Game/') for p in packages)
assert not any('asset_name: "World"' in a['asset_class'] for r in audit['packages'] for a in r['assets']), 'Sample maps are outside this migration'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


protected = list((SOURCE / 'Content').rglob('*')) + list((SOURCE / 'Config').rglob('*'))
protected += [SOURCE / 'GameAnimationSample.uproject']
source_hashes = {p.relative_to(SOURCE).as_posix():digest(p) for p in protected if p.is_file()}
with (OUT / 'source-preservation-before01.json').open('x', encoding='utf-8') as stream:
    json.dump(source_hashes, stream, indent=2)
expected = []
for package in packages:
    relative = package.removeprefix('/Game/') + '.uasset'
    source = SOURCE / 'Content' / relative
    assert source.is_file(), source
    expected.append(dict(source_package=package, derived_package='/GASPEnemyFoundation01/' + package.removeprefix('/Game/'),
        source=str(source), source_sha256=source_hashes['Content/' + relative], source_bytes=source.stat().st_size,
        derived=(DEST / relative).relative_to(ROOT).as_posix()))
with (OUT / 'migration-plan01.json').open('x', encoding='utf-8') as stream:
    json.dump(expected, stream, indent=2)
u.log('MSQ98_MIGRATION_BEGIN packages=' + str(len(packages)))
options = u.MigrationOptions(prompt=False, ignore_dependencies=True, asset_conflict=u.AssetMigrationConflict.SKIP)
u.AssetToolsHelpers.get_asset_tools().migrate_packages(packages, str(DEST), options)
changed_sources = [rel for rel, before in source_hashes.items() if digest(SOURCE / rel) != before]
missing = []
for item in expected:
    path = ROOT / item['derived']
    if path.is_file():
        item.update(derived_sha256=digest(path), derived_bytes=path.stat().st_size)
    else:
        missing.append(item['source_package'])
with (OUT / 'migration-result01.json').open('x', encoding='utf-8') as stream:
    json.dump(dict(changed_sources=changed_sources, missing=missing, assets=expected), stream, indent=2)
assert not changed_sources, changed_sources
assert not missing, missing
u.log('MSQ98_MIGRATION_DONE packages=' + str(len(expected)))
