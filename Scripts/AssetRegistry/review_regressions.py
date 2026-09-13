"""Controller-review regressions: no remote connections; only owned Saved fixtures."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid
from unittest.mock import patch

import registry as r

OUT = r.ROOT / 'Saved/AssetRegistry/Acceptance'


def snapshot():
    return {table: r.query(f'SELECT * FROM asset_registry.{table} ORDER BY 1,2')
            for table in ('assets', 'artifacts', 'dependencies')}


def environment_check(directory):
    poisoned = {key: 'must-not-inherit' for key in (
        'PGHOSTADDR', 'PGSERVICE', 'PGSERVICEFILE', 'PGSYSCONFDIR', 'PGPASSFILE',
        'PGOPTIONS', 'PGDATABASE', 'PGHOST', 'PGPORT', 'PGUSER', 'PGPASSWORD',
        'PGSSLMODE', 'PGSSLROOTCERT', 'PGTARGETSESSIONATTRS', 'PGLOADBALANCEHOSTS')}
    config = dict(host='127.0.0.1', port=15432, user=r.ROLE, database=r.DATABASE, password='fixture-only')
    expected = {'PGHOST', 'PGPORT', 'PGUSER', 'PGPASSWORD', 'PGDATABASE',
                'PGCLIENTENCODING', 'PGOPTIONS', 'PGCONNECT_TIMEOUT'}
    observed = []

    def fake_run(args, **kwargs):
        env = kwargs['env']
        assert {key for key in env if key.upper().startswith('PG')} == expected
        assert env['PGHOST'] == '127.0.0.1' and env['PGPORT'] == '15432'
        assert env['PGUSER'] == r.ROLE and env['PGDATABASE'] == r.DATABASE
        assert env['PGOPTIONS'] == '-c standard_conforming_strings=on'
        assert env['PGPASSWORD'] == 'fixture-only'
        observed.append(Path(args[0]).name)
        return subprocess.CompletedProcess(args, 0, stdout='1', stderr='')

    with patch.dict(os.environ, poisoned), patch.object(r, 'connection', return_value=config):
        # A real Python child checks environment propagation; no PostgreSQL client runs.
        child = subprocess.run([sys.executable, '-c',
                                'import os,json; print(json.dumps(sorted(k for k in os.environ if k.upper().startswith("PG"))))'],
                               env=r.pg_env(config), text=True, capture_output=True, check=True)
        assert set(json.loads(child.stdout)) == expected
        with patch.object(r.subprocess, 'run', side_effect=fake_run), patch.object(r, 'fingerprint', return_value={}):
            r.pg('SELECT 1;')
            r.backup(directory / 'mock.dump')
    assert observed == ['psql.exe', 'pg_dump.exe']
    return {'clients': observed, 'poisoned_parameters': sorted(poisoned), 'remote_connections': 0}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    before = snapshot()
    result = {'migration_repeat': r.migrate() == r.migrate()}
    name = 'Review-' + uuid.uuid4().hex
    directory = r.ROOT / 'Saved/AssetRegistry/fixtures' / name
    real = directory / 'RealDirectory'
    real.mkdir(parents=True)
    source = real / 'Source.txt'
    other = real / 'Output.txt'
    evidence = real / 'Evidence.txt'
    hardlink = real / 'HardAlias.txt'
    junction = directory / 'InternalAlias'
    files = (source, other, evidence)
    for path in files:
        path.write_text('fixture\n', encoding='utf-8')
    rel = lambda p: p.relative_to(r.ROOT).as_posix()
    special = "role ' $$ $check$ $migration$ ; -- literal data"
    ev = [{'source': rel(evidence), 'note': special}]
    manifest = {'asset': name, 'artifacts': [dict(path=rel(p), role=special, evidence=ev, **r.fingerprint(p)) for p in (source, other)],
                'dependencies': [dict(upstream=rel(source), downstream=rel(other), kind=special, status='verified', evidence=ev)]}
    rejected = []

    def reject_alias(path):
        candidate = copy.deepcopy(manifest)
        candidate['artifacts'][0]['path'] = path
        candidate['dependencies'][0]['upstream'] = path
        saved = snapshot()
        try:
            r.register(candidate)
        except ValueError:
            pass
        else:
            raise AssertionError('Alias was registered: ' + path)
        assert snapshot() == saved
        rejected.append(path)

    try:
        result['environment'] = environment_check(directory)
        r.register(manifest)
        registered = r.inspect(name)
        r.register(manifest)
        assert r.inspect(name) == registered
        assert all(a['role'] == special and a['evidence'][0]['note'] == special for a in registered['artifacts'])
        assert registered['dependencies'][0]['kind'] == special
        result['sql_delimiters_and_quotes_roundtrip'] = True
        reject_alias(rel(source).replace('Source.txt', 'source.TXT'))
        reject_alias(rel(source).replace('RealDirectory', 'realdirectory'))
        reject_alias(rel(source) + '.')
        os.link(source, hardlink)
        try:
            reject_alias(rel(hardlink))
            reject_alias(rel(source))
        finally:
            hardlink.unlink()
        created = subprocess.run(['cmd.exe', '/c', 'mklink', '/J', str(junction), str(real)], capture_output=True)
        assert created.returncode == 0, 'Could not create local junction fixture'
        try:
            assert (junction / source.name).samefile(source)
            reject_alias(rel(junction / source.name))
        finally:
            os.rmdir(junction)
        assert source.is_file()
        # The database also prevents case-only duplication after canonical spelling changes.
        try:
            r.pg('BEGIN; INSERT INTO asset_registry.artifacts SELECT ' + r.literal(str(uuid.uuid4())) +
                 ',asset_id,upper(path),role,sha256,size_bytes,unreal_package,evidence FROM asset_registry.artifacts WHERE path=' +
                 r.literal(rel(source)) + '; COMMIT;')
        except RuntimeError:
            result['case_unique_index_rejected_duplicate'] = True
        else:
            raise AssertionError('Case duplicate bypassed database index')
        assert r.inspect(name) == registered
        result['rejected_aliases'] = rejected
    finally:
        aid = r.literal(r.stable_id('asset:' + name))
        r.pg(f'BEGIN; DELETE FROM asset_registry.dependencies WHERE upstream IN (SELECT id FROM asset_registry.artifacts WHERE asset_id={aid}); DELETE FROM asset_registry.artifacts WHERE asset_id={aid}; DELETE FROM asset_registry.assets WHERE id={aid}; COMMIT;')
        for path in files:
            assert path.resolve().is_relative_to(directory.resolve())
            path.unlink()
        real.rmdir()
        directory.rmdir()
    assert snapshot() == before
    result['existing_registry_rows_unchanged'] = True
    protected = subprocess.run([sys.executable, str(r.ROOT / 'Saved/AgentSetup/NextStage/registry_baseline.py'), '--check'], capture_output=True, text=True)
    assert protected.returncode == 0, 'Protected baseline check failed'
    result['protected'] = json.loads((OUT / 'protected-result.json').read_text())
    result['passed'] = True
    (OUT / 'review-regressions.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
