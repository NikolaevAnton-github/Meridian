"""Integration checks against the local asset DB; mutate only owned Saved fixtures."""
import json
from pathlib import Path
import subprocess
import sys
import uuid

from registry import ROOT, pg, query, migrate, register, inspect, validate, fingerprint, literal, stable_id, backup, BIN

OUT = ROOT / 'Saved/AssetRegistry/Acceptance'


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    result = {}
    result['migration_repeat'] = migrate() == migrate()
    counts = []
    for attempt in range(2):
        registered = []
        for name in ('PipelineProbe', 'BenchA', 'BenchB'):
            manifest = json.loads((Path(__file__).parent / 'manifests' / (name + '.json')).read_text())
            registered.append(register(manifest))
            if attempt == 1:
                save(name + '-inspect.json', inspect(name))
                checked = validate(name)
                save(name + '-validate.json', checked)
                assert checked['passed'], checked
        counts.append(query('SELECT (SELECT count(*) FROM asset_registry.assets) AS assets, (SELECT count(*) FROM asset_registry.artifacts) AS artifacts, (SELECT count(*) FROM asset_registry.dependencies) AS dependencies'))
    result['idempotent'] = counts[0] == counts[1]
    result['inventory'] = counts[1]
    result['registered'] = registered
    name = 'Fixture-' + uuid.uuid4().hex
    directory = ROOT / 'Saved/AssetRegistry/fixtures' / name
    directory.mkdir(parents=True)
    paths = [(directory / (label + '.txt')).relative_to(ROOT).as_posix() for label in ('source', 'export', 'package', 'evidence')]
    for path in paths:
        (ROOT / path).write_text('accepted fixture\n', encoding='utf-8')
    ev = [{'source': paths[3], 'note': "Controlled fixture: quotes ' and dollar tags $check$ are data, not SQL."}]
    manifest = {'asset': name, 'artifacts': [{'path': path, 'role': 'test_fixture', **fingerprint(ROOT / path), 'evidence': ev} for path in paths[:3]],
                'dependencies': [{'upstream': paths[i], 'downstream': paths[i+1], 'kind': 'fixture', 'status': status, 'evidence': ev} for i, status in enumerate(('verified', 'unverified'))]}
    try:
        register(manifest)
        assert validate(name)['passed']
        (ROOT / paths[0]).write_text('changed fixture\n', encoding='utf-8')
        changed = validate(name)
        assert changed['changes'][0]['state'] == 'changed'
        assert any(len(c['paths']) == 2 and not c['uncertain'] for c in changed['affected_chains'])
        assert any(len(c['paths']) == 3 and c['uncertain'] for c in changed['affected_chains'])
        save('fixture-changed.json', changed)
        # An explicit new fingerprint must not silently replace registered accepted bytes.
        manifest['artifacts'][0].update(fingerprint(ROOT / paths[0]))
        rejected = False
        try:
            register(manifest)
        except RuntimeError:
            rejected = True
        assert rejected
        result['baseline_overwrite_rejected'] = True
        (ROOT / paths[0]).unlink()
        missing = validate(name)
        assert missing['changes'][0]['state'] == 'missing'
        assert len(missing['affected_chains']) == 2
        save('fixture-missing.json', missing)
        (ROOT / paths[3]).write_text('changed evidence\n', encoding='utf-8')
        stale = validate(name)
        assert stale['evidence_changes'] and all(c['uncertain'] for c in stale['affected_chains'])
        save('fixture-stale-evidence.json', stale)
        result['changed_missing_uncertainty'] = True
    finally:
        aid = literal(stable_id('asset:' + name))
        pg(f'BEGIN; DELETE FROM asset_registry.dependencies WHERE upstream IN (SELECT id FROM asset_registry.artifacts WHERE asset_id={aid}) OR downstream IN (SELECT id FROM asset_registry.artifacts WHERE asset_id={aid}); DELETE FROM asset_registry.artifacts WHERE asset_id={aid}; DELETE FROM asset_registry.assets WHERE id={aid}; COMMIT;')
        # Delete only individually named test files inside this invocation's directory.
        for path in paths:
            target = ROOT / path
            assert target.resolve().is_relative_to(directory.resolve())
            target.unlink(missing_ok=True)
        directory.rmdir()
    result['role'] = query('SELECT current_database() AS database, current_user AS role, rolsuper, rolcreatedb, rolcreaterole, rolreplication FROM pg_roles WHERE rolname=current_user')
    assert not any(result['role'][0][key] for key in ('rolsuper', 'rolcreatedb', 'rolcreaterole', 'rolreplication'))
    snapshot = ROOT / 'Saved/AssetRegistry/backups' / ('acceptance-' + uuid.uuid4().hex[:8] + '.dump')
    result['backup'] = backup(snapshot)
    listing = subprocess.run([str(BIN / 'pg_restore.exe'), '--list', str(snapshot)], capture_output=True, text=True)
    assert listing.returncode == 0 and 'asset_registry' in listing.stdout
    (OUT / 'backup-contents.txt').write_text(listing.stdout, encoding='utf-8')
    protected = subprocess.run([sys.executable, str(ROOT / 'Saved/AgentSetup/NextStage/registry_baseline.py'), '--check'], capture_output=True, text=True)
    (OUT / 'protected-check.log').write_text(protected.stdout + protected.stderr, encoding='utf-8')
    assert protected.returncode == 0
    result['protected'] = json.loads((OUT / 'protected-result.json').read_text())
    result['passed'] = result['migration_repeat'] and result['idempotent']
    save('results.json', result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
