"""File inventory and dependency checks using Python stdlib and installed psql."""
import argparse
import hashlib
import json
import os
import stat
from pathlib import Path, PurePosixPath
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / 'Saved/AssetRegistry/credentials/connection.json'
BIN = ROOT / '.tools/multica/pgsql/bin'
DATABASE = 'meridian_assets'
ROLE = 'meridian_assets_owner'
NAMESPACE = uuid.UUID('d2ab9cf1-42ef-4a53-a602-ae8b4e9385f5')


def literal(value):
    if value is None:
        return 'NULL'
    return "'" + str(value).replace("'", "''") + "'"


def stable_id(value):
    return str(uuid.uuid5(NAMESPACE, value))


def local_path(value):
    p = PurePosixPath(value)
    if not value or '\\' in value or ':' in value or p.is_absolute() or '..' in p.parts or p.as_posix() != value:
        raise ValueError('Expected a normalized project-relative path')
    target = ROOT / value
    if not target.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Path escapes project root')
    return target


def fingerprint(path):
    with path.open('rb') as stream:
        before = os.fstat(stream.fileno())
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        after = os.fstat(stream.fileno())
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError('File changed while hashing')
    return {'sha256': digest, 'size_bytes': after.st_size}


def registration_path(value):
    """Require the real directory spelling and refuse filesystem aliases."""
    target = local_path(value)
    current = ROOT
    for part in PurePosixPath(value).parts:
        with os.scandir(current) as entries:
            entry = next((e for e in entries if e.name == part), None)
        if entry is None:
            raise ValueError('Artifact path must use exact on-disk spelling: ' + value)
        info = entry.stat(follow_symlinks=False)
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError('Artifact paths must not use symlinks or reparse points: ' + value)
        current /= part
    info = target.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError('Artifact must be a regular file with exactly one hard link: ' + value)
    return target


def connection():
    config = json.loads(CONFIG.read_text(encoding='utf-8'))
    if config['database'] != DATABASE or config['user'] != ROLE or config['host'] != '127.0.0.1':
        raise ValueError('Refusing a connection outside the local asset database')
    return config


def pg_env(c):
    # libpq has independent routing inputs (e.g. PGHOSTADDR and PGSERVICE).
    # Start without ANY inherited PG parameter, then install only our settings.
    env = {key: value for key, value in os.environ.items() if not key.upper().startswith('PG')}
    env.update(PGHOST=c['host'], PGPORT=str(c['port']), PGUSER=c['user'],
               PGPASSWORD=c['password'], PGDATABASE=c['database'], PGCLIENTENCODING='UTF8',
               PGOPTIONS='-c standard_conforming_strings=on', PGCONNECT_TIMEOUT='5')
    return env


def pg(sql, config=None):
    env = pg_env(config or connection())
    result = subprocess.run([str(BIN / 'psql.exe'), '-X', '-qAt', '-v', 'ON_ERROR_STOP=1'],
                            input=sql, text=True, encoding='utf-8', capture_output=True, env=env,
                            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if result.returncode:
        # SQL errors can echo literals; never expose credentials or SQL payloads.
        raise RuntimeError('PostgreSQL operation failed (diagnostic output suppressed)')
    return result.stdout.strip()


def backup(target):
    target = target.resolve()
    if not target.is_relative_to((ROOT / 'Saved/AssetRegistry').resolve()) or target.exists():
        raise ValueError('Backup must be a new file under Saved/AssetRegistry')
    target.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run([str(BIN / 'pg_dump.exe'), '-Fc', '--no-owner', '--no-privileges', '-f', str(target)],
                            env=pg_env(connection()), capture_output=True,
                            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if result.returncode:
        raise RuntimeError('Asset database backup failed')
    return {'backup': target.relative_to(ROOT).as_posix(), **fingerprint(target)}


def query(sql):
    return json.loads(pg('SELECT coalesce(json_agg(q),\'[]\'::json) FROM (' + sql + ') q;'))


def migrate():
    statements = ['BEGIN;', 'SELECT pg_advisory_xact_lock(714301);',
                  'CREATE TABLE IF NOT EXISTS public.asset_registry_migrations (version text PRIMARY KEY, sha256 text NOT NULL);']
    for path in sorted((Path(__file__).parent / 'migrations').glob('*.sql')):
        source = path.read_text(encoding='utf-8')
        sha = hashlib.sha256(source.encode()).hexdigest()
        statements.append(f"""DO $migration$
BEGIN
 IF EXISTS (SELECT 1 FROM public.asset_registry_migrations WHERE version={literal(path.name)} AND sha256 <> {literal(sha)}) THEN
  RAISE EXCEPTION 'Applied migration checksum mismatch';
 END IF;
 IF NOT EXISTS (SELECT 1 FROM public.asset_registry_migrations WHERE version={literal(path.name)}) THEN
  {source}
  INSERT INTO public.asset_registry_migrations VALUES ({literal(path.name)}, {literal(sha)});
 END IF;
END $migration$;""")
    statements.append('COMMIT;')
    pg('\n'.join(statements))
    return {'migrations': query('SELECT * FROM public.asset_registry_migrations ORDER BY version')}


def evidence_record(item):
    if not isinstance(item, dict) or not item.get('note') or not item.get('source'):
        raise ValueError('Evidence requires source and note')
    result = dict(item)
    path = local_path(item['source'])
    result['source_state'] = 'present' if path.is_file() else 'missing'
    result['source_sha256'] = fingerprint(path)['sha256'] if path.is_file() else None
    return result


def register(manifest):
    asset = manifest['asset']
    aid = stable_id('asset:' + asset)
    rows = []
    by_path = {}
    for item in manifest['artifacts']:
        path = item['path']
        target = registration_path(path)
        observed = fingerprint(target)
        # Expected accepted hashes are mandatory: registration is not acceptance.
        if observed != {key: item[key] for key in ('sha256', 'size_bytes')}:
            raise ValueError('Artifact differs from manifest: ' + path)
        package = item.get('unreal_package')
        if package and (not path.startswith('Content/') or package != '/Game/' + path[len('Content/'):].rsplit('.', 1)[0]):
            raise ValueError('Unreal package does not match file path')
        ev = [evidence_record(e) for e in item['evidence']]
        if not ev:
            raise ValueError('Artifact needs evidence, including limitations')
        fid = stable_id('file:' + path)
        if path in by_path:
            raise ValueError('Duplicate artifact path')
        by_path[path] = fid
        rows.append((fid, aid, path, item['role'], observed['sha256'], observed['size_bytes'], package, json.dumps(ev)))
    edges = []
    for edge in manifest['dependencies']:
        ev = [evidence_record(e) for e in edge['evidence']]
        if not ev or (edge['status'] == 'verified' and any(e['source_state'] != 'present' for e in ev)):
            raise ValueError('Verified relationship requires present evidence')
        edges.append((by_path[edge['upstream']], by_path[edge['downstream']], edge['kind'], edge['status'], json.dumps(ev)))
    sql = ['BEGIN;', 'SELECT pg_advisory_xact_lock(714301);',
           'CREATE TEMP TABLE registration_assertion (valid boolean NOT NULL CHECK(valid)) ON COMMIT DROP;',
           f'INSERT INTO asset_registry.assets VALUES ({literal(aid)}, {literal(asset)}) ON CONFLICT DO NOTHING;']
    for row in rows:
        # Exact repeats are no-ops; different accepted bytes require explicit review.
        sql.append('INSERT INTO asset_registry.artifacts VALUES (' + ','.join(map(literal, row)) + ') ON CONFLICT DO NOTHING;')
        sql.append(f"INSERT INTO registration_assertion SELECT EXISTS (SELECT 1 FROM asset_registry.artifacts WHERE id={literal(row[0])} AND asset_id={literal(aid)} AND sha256={literal(row[4])} AND size_bytes={literal(row[5])} AND role={literal(row[3])} AND unreal_package IS NOT DISTINCT FROM {literal(row[6])} AND evidence={literal(row[7])}::jsonb);")
    for row in edges:
        sql.append('INSERT INTO asset_registry.dependencies VALUES (' + ','.join(map(literal, row)) + ') ON CONFLICT DO NOTHING;')
        sql.append(f"INSERT INTO registration_assertion SELECT EXISTS (SELECT 1 FROM asset_registry.dependencies WHERE upstream={literal(row[0])} AND downstream={literal(row[1])} AND kind={literal(row[2])} AND status={literal(row[3])} AND evidence={literal(row[4])}::jsonb);")
    pg('\n'.join(sql + ['COMMIT;']))
    return {'asset': asset, 'id': aid, 'artifacts': len(rows), 'dependencies': len(edges)}


def inspect(asset):
    assets = query('SELECT * FROM asset_registry.assets WHERE name=' + literal(asset))
    if not assets:
        raise ValueError('Unknown asset: ' + asset)
    return {'asset': assets[0], 'artifacts': query('SELECT * FROM asset_registry.artifacts WHERE asset_id=' + literal(assets[0]['id']) + ' ORDER BY path'),
            'dependencies': query('SELECT d.*, u.path AS upstream_path, v.path AS downstream_path FROM asset_registry.dependencies d JOIN asset_registry.artifacts u ON u.id=d.upstream JOIN asset_registry.artifacts v ON v.id=d.downstream WHERE u.asset_id=' + literal(assets[0]['id']) + ' OR v.asset_id=' + literal(assets[0]['id']) + ' ORDER BY u.path,v.path,d.kind')}


def validate(asset):
    record = inspect(asset)
    artifacts = {a['id']: a for a in query('SELECT * FROM asset_registry.artifacts')}
    edges = query('SELECT * FROM asset_registry.dependencies ORDER BY upstream,downstream,kind')
    changes, evidence_changes = [], []
    for a in record['artifacts']:
        path = local_path(a['path'])
        try:
            actual = fingerprint(path)
            state = 'ok' if actual == {k: a[k] for k in ('sha256', 'size_bytes')} else 'changed'
        except FileNotFoundError:
            actual, state = None, 'missing'
        if state != 'ok':
            changes.append({'path': a['path'], 'id': a['id'], 'state': state, 'actual': actual})
    for obj in record['artifacts'] + record['dependencies']:
        for ev in obj['evidence']:
            p = local_path(ev['source'])
            current = fingerprint(p)['sha256'] if p.is_file() else None
            if current != ev['source_sha256'] or current is None:
                evidence_changes.append({'source': ev['source'], 'state': 'missing' if current is None else 'changed'})
    chains = []
    for change in changes:
        stack = [(change['id'], [change['id']], [], False)]
        while stack:
            current, trail, links, uncertain = stack.pop()
            for edge in edges:
                if edge['upstream'] != current or edge['downstream'] in trail:
                    continue
                evidence_stale = any(not local_path(e['source']).is_file() or fingerprint(local_path(e['source']))['sha256'] != e['source_sha256'] for e in edge['evidence'])
                doubt = uncertain or edge['status'] != 'verified' or evidence_stale
                next_trail = trail + [edge['downstream']]
                next_links = links + [{'kind': edge['kind'], 'status': edge['status'], 'evidence_stale': evidence_stale}]
                chains.append({'paths': [artifacts[i]['path'] for i in next_trail], 'uncertain': doubt, 'edges': next_links})
                stack.append((edge['downstream'], next_trail, next_links, doubt))
    return {'asset': asset, 'passed': not changes and not evidence_changes, 'changes': changes,
            'affected_chains': chains, 'evidence_changes': evidence_changes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('migrate')
    sub.add_parser('list')
    sub.add_parser('backup').add_argument('target', type=Path)
    reg = sub.add_parser('register')
    reg.add_argument('manifest', type=Path)
    for command in ('inspect', 'validate'):
        sub.add_parser(command).add_argument('asset')
    args = parser.parse_args()
    if args.command == 'migrate':
        result = migrate()
    elif args.command == 'list':
        result = query('SELECT * FROM asset_registry.assets ORDER BY name')
    elif args.command == 'backup':
        result = backup(args.target)
    elif args.command == 'register':
        result = register(json.loads(args.manifest.read_text(encoding='utf-8')))
    elif args.command == 'inspect':
        result = inspect(args.asset)
    else:
        result = validate(args.asset)
    print(json.dumps(result, indent=2))
    return 1 if isinstance(result, dict) and result.get('passed') is False else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(2)
