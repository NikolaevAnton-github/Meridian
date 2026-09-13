"""Provision only the separate local asset database; never write Multica tables."""
import json
import secrets
import subprocess
from urllib.parse import unquote, urlsplit

from registry import ROOT, CONFIG, DATABASE, ROLE, pg, literal, connection


def main():
    if CONFIG.exists():
        pg('SELECT 1;', connection())
        print('Existing asset connection verified; no provisioning changes.')
        return
    source = json.loads((ROOT / '.tools/multica/local-config.json').read_text(encoding='utf-8-sig'))
    url = urlsplit(source['environment']['DATABASE_URL'])
    if url.hostname not in ('127.0.0.1', 'localhost'):
        raise ValueError('Only the existing loopback PostgreSQL instance is allowed')
    admin = dict(host='127.0.0.1', port=url.port, user=unquote(url.username),
                 password=unquote(url.password), database='postgres')
    if pg(f"SELECT count(*) FROM pg_roles WHERE rolname={literal(ROLE)};", admin) != '0' or pg(f"SELECT count(*) FROM pg_database WHERE datname={literal(DATABASE)};", admin) != '0':
        raise ValueError('Asset role/database already exists without credentials; inspect manually, do not overwrite')
    credential_dir = CONFIG.parent
    credential_dir.mkdir(parents=True, exist_ok=True)
    # Remove inherited permissions before writing any secret. Keep current user and SYSTEM.
    identity = subprocess.check_output(['whoami'], text=True).strip()
    acl = subprocess.run(['icacls', str(credential_dir), '/inheritance:r', '/grant:r',
                          identity + ':(OI)(CI)F', '*S-1-5-18:(OI)(CI)F'], capture_output=True)
    if acl.returncode:
        raise RuntimeError('Could not restrict credential directory ACL')
    config = dict(host='127.0.0.1', port=url.port, user=ROLE,
                  password=secrets.token_urlsafe(36), database=DATABASE)
    # Persist the recovery credential first; provisioning failures never reset a role.
    CONFIG.write_text(json.dumps(config, indent=2), encoding='utf-8')
    pg(f"SET log_statement='none'; SET log_min_error_statement='panic'; CREATE ROLE {ROLE} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION PASSWORD {literal(config['password'])};", admin)
    pg(f'CREATE DATABASE {DATABASE} OWNER {ROLE};', admin)
    pg(f'REVOKE ALL ON DATABASE {DATABASE} FROM PUBLIC; GRANT CONNECT ON DATABASE {DATABASE} TO {ROLE};', admin)
    pg('REVOKE CREATE ON SCHEMA public FROM PUBLIC;', config)
    print('Created isolated asset database and non-superuser owner; credentials saved privately.')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        raise SystemExit('Local setup failed; inspect provisioning state privately. No secrets emitted.')
