# Local asset registry

The registry inventories accepted files without regenerating them. PostgreSQL
17.11 runs in the existing portable installation on loopback port 15432.
`meridian_assets` is a separate database, owned by the non-superuser login
`meridian_assets_owner`. It contains no task records. Multica still owns tasks.
Python 3.11.8 and installed PostgreSQL command-line tools are sufficient; no pip
packages, DCC connection, extra service, or paid API is used.

## Setup and commands

Run from the project root in PowerShell:

```powershell
$registryPython = 'D:/UE_5.8/Engine/Binaries/ThirdParty/Python3/Win64/python.exe'
& $registryPython Scripts/AssetRegistry/setup_local.py
& $registryPython Scripts/AssetRegistry/registry.py migrate
& $registryPython Scripts/AssetRegistry/registry.py migrate
& $registryPython Scripts/AssetRegistry/registry.py register Scripts/AssetRegistry/manifests/PipelineProbe.json
& $registryPython Scripts/AssetRegistry/registry.py register Scripts/AssetRegistry/manifests/BenchA.json
& $registryPython Scripts/AssetRegistry/registry.py register Scripts/AssetRegistry/manifests/BenchB.json
& $registryPython Scripts/AssetRegistry/registry.py list
& $registryPython Scripts/AssetRegistry/registry.py inspect PipelineProbe
& $registryPython Scripts/AssetRegistry/registry.py validate PipelineProbe
```

Inspect returns sources, FBX, exported maps, Unreal package paths, SHA-256 and
size, and relationship evidence. Edges point from input to dependent output:
for example Blender source -> FBX -> Painter source -> PNG -> Unreal texture ->
material -> mesh. Meshes also depend directly on imported FBX. PipelineProbe's
superseded green material remains in the inventory without an active binding.

Commands emit JSON. Exit 0 means success; validate exits 1 for changed/missing
artifacts or stale/missing evidence; invalid input or database errors exit 2.
Database errors deliberately omit SQL payloads, which could contain secrets.
Normal commands refuse credentials targeting another host, database or role.
Both psql and pg_dump receive an environment with all inherited `PG*` variables
removed before the explicit local connection settings are installed. In
particular, `PGHOSTADDR`, `PGSERVICE`, `PGSERVICEFILE` and `PGSYSCONFDIR` cannot
redirect these subprocesses through the caller's environment.

## Credentials and isolation

One-time setup reads the existing ignored `.tools/multica/local-config.json`
privately, connects to the `postgres` maintenance database, creates only the
asset role/database, and revokes public access to the new database. It does not
write Multica tables, schemas or database ACLs. The asset owner has no superuser,
create-database, create-role or replication permissions, and receives no role
memberships. It owns this small database so the same local credential can apply
its migrations. This is a local administrative CLI, not a multiuser service.

The generated password is in
`Saved/AssetRegistry/credentials/connection.json`, excluded from Git. Its parent
directory's Windows ACL grants only the current user and SYSTEM access. The
password is passed through the subprocess environment, never command arguments
or logs. Do not copy this file into reports. An existing successful setup is
reused. If provisioning was interrupted, inspect the new role/database and this
credential privately; setup refuses to replace an existing role or database.

## Registration and evidence semantics

Versioned manifests in `Scripts/AssetRegistry/manifests` are reviewed inventory
inputs, not generated verification reports. A new manifest has `asset`,
`artifacts`, and `dependencies`, using the same fields as the seed manifests.
Artifact paths must be normalized project-relative paths; escaping symlinks,
absolute paths and traversal are rejected. Expected hashes and sizes are
mandatory and checked before any database writes. UUIDv5 IDs derive from the
asset name or project-relative path in a fixed project namespace. A rename is a
new logical identity; rename/history tooling is outside this version.

Registration requires the exact directory-entry spelling of every path component
and rejects symbolic links, junctions/reparse points, short-name and trailing-dot
aliases, and files with multiple hard links. This intentionally rejects aliases
rather than silently assigning another ID or selecting a preferred hard-link
name. Migration `002_windows_path_identity.sql` adds a unique index on
`lower(path)` without changing existing UUIDs, paths, hashes or evidence. It
also prevents case-only duplicates after an on-disk spelling change. All 48
initial artifacts have one hard link and retain their original identities.

Exact repeated registrations add no assets, artifacts or edges. Registrations
are atomic and serialized with the migration lock. Conflicting existing hashes,
roles, packages or evidence fail rather than silently accepting changed files.
Additional artifacts/edges can be registered; omitted entries are not deleted.
There is no automatic rebaseline or evidence-promotion command: a new accepted
revision needs a reviewed future migration/workflow. Direct database edits are
not part of routine usage.

Each artifact and relationship has evidence `source` and `note`; registration
stores evidence presence and SHA-256. Relationship status is explicit:

- `verified`: an existing report explicitly supports the relationship.
- `declared`: a documented workflow or supplied declaration supports it, but
  exact derivation has not been independently verified.
- `unverified`: candidate mapping, including filename/channel correspondence.

Present evidence is required for verified edges. The CLI records the author's
claim; it does not interpret arbitrary reports or certify their truth. Missing
reports for declared/unverified edges are retained honestly and fail validation.
Evidence changes also fail validation, and downgrade affected chains to uncertain.

`build_seed.py` is the reproducible, read-only importer used to prepare the three
initial manifests from saved reports. It must not be used to accept changed
files automatically. Benchmark hashes match the public acceptance manifest.
PipelineProbe's original mesh hash predates the Painter material reassignment:
its current fingerprint is only an inventory baseline, supported by the later
save report. Its FBX report has no historical hash. These limits are recorded in
the manifest. Filename-derived texture imports remain unverified. SPP derivation
is declared because the saved proprietary project was not independently parsed.

## Validation and acceptance

Validation is read-only: it compares current file bytes with registered hashes
and follows all reachable dependency paths, preserving uncertainty whenever a
path includes an unverified/declared edge or stale evidence. Cycles terminate by
not revisiting a node on the same path. Results identify potentially stale
outputs; they never rebuild files or claim those outputs are actually different.
The graph traversal is intended for this small inventory, not a large graph.
There is no continuous watcher, DCC parser, revision history, or atomic filesystem
snapshot; avoid concurrent asset editing during registration/validation.

```powershell
& $registryPython Scripts/AssetRegistry/acceptance.py
& $registryPython Scripts/AssetRegistry/review_regressions.py
```

The integration check applies migrations twice, registers each seed twice,
inspects and validates each asset, then changes and removes tiny files created
under `Saved/AssetRegistry/fixtures`. It checks mixed-certainty downstream paths,
stale evidence and rejection of baseline replacement, and cleans only its own
test files/rows. It reuses the controller's existing
`Saved/AgentSetup/NextStage/registry_baseline.py --check` to verify protected
asset/config hashes and the Multica schema. That controller baseline must exist
to run the full acceptance script; ordinary CLI commands do not need it.
Full JSON evidence and logs belong under `Saved/AssetRegistry/Acceptance`.
The review regressions exercise dollar delimiters and quotes in role, evidence
and relationship values; intercept psql/pg_dump environments under poisoned
libpq variables without running either client against a remote server; and
reject capitalization, trailing-dot, hard-link and internal-junction aliases
using temporary Saved fixtures. They compare every pre-existing registry row
before and after the test and reuse the protected-file/schema validator.

## Backup and restore

```powershell
& $registryPython Scripts/AssetRegistry/registry.py backup Saved/AssetRegistry/backups/assets-20260913.dump
& '.tools/multica/pgsql/bin/pg_restore.exe' --list Saved/AssetRegistry/backups/assets-20260913.dump
```

Backup refuses to overwrite a file and permits only ignored `Saved/AssetRegistry`
destinations. It uses a custom-format pg_dump of the asset database only, with no
owner/ACL restoration commands. It includes migration history, inventory and
stored evidence fingerprints, but no role passwords or binary assets. The first
acceptance backup was 14,804 bytes; its exact path/hash is in `Acceptance/results.json`.

For disaster recovery, provision an empty `meridian_assets` database with
`setup_local.py`, then run installed `pg_restore --exit-on-error --no-owner
--no-privileges --dbname=meridian_assets <dump>` with the asset connection fields
loaded privately into libpq environment variables (the Python helper
`registry.pg_env(registry.connection())` provides them). Do not run migrations
before a full restore, and do not restore into Multica. Verify `list`, `inspect`
and `validate` afterward. A restored inventory cannot reconstruct missing asset
files or evidence: back up Git/LFS and required Saved reports separately.
Archive listing was tested; a full disaster restore has not been exercised.
Same-disk dumps are not off-device backups. Retain a bounded number manually.
