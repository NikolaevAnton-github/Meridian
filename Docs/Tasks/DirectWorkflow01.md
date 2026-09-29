# DirectWorkflow01: direct implementation, optional task board

Date: 2026-09-29. Authority: [owner request](../Approvals/DirectWorkflow01-OwnerRequest01.json).

Codex performs project work directly. The owner performs final testing and
acceptance. Earlier mandatory Multica, executor/controller/reviewer and runtime
context workflows are retired project-wide; historical task scope/evidence remains.

## Scope

- Stop the project Multica daemon without interrupting active work.
- Keep the existing Multica installation and records only for optional board use.
  Remove runtime launch actions and retain board API/web/database administration.
- Remove project worker profiles, daemon patches/build/smoke helpers, automatic
  context Git hook, benchmark worker launcher and live-issue
  brief/checkpoint/native-usage integration.
- Retain standalone context size/link/archive checks, optional output capture and
  existing source/build tools. Preserve LFS hooks and immutable archive manifests.
- Keep shared PostgreSQL data/binaries in place: the independent asset registry
  uses them. Stopping the board must not stop this database.
- Preserve historical reports, task records and generated evidence; do not
  rewrite old deliveries or execute prepared tasks during this migration.

## Verification and handoff

Evidence belongs in `Saved/DirectWorkflow01/`. Check daemon state, launcher action
boundaries, remaining standalone context tests, repository context budgets and the
asset database connection. Inspect the scoped diff and commit only this migration.
This is an administrative workflow change; no game build or gameplay acceptance
is claimed. The owner retains final testing.

Verified on 2026-09-29:

- The daemon had zero active/running/waiting tasks and stopped cleanly. No matching
  Windows service, scheduled task or Run-key startup entry was found.
- Board `Start` passed API/web health checks without launching a worker;
  `StartRuntime` is rejected. Board API/web are stopped at handoff.
- Shared PostgreSQL remains on loopback port 15432. Existing asset credentials
  still connect successfully with the board stopped; no provisioning was needed.
- All 9 retained context regression tests pass. Entry points total 7,832 bytes;
  navigation and both immutable archive fingerprints pass the repository guard.
- The installed automatic pre-commit wrapper was removed through its preserving
  uninstaller. All four existing LFS hook fingerprints are unchanged.

Removed implementation sources remain at pre-migration Git revision
`53f2ac2f51ff4d16b14b73e478f7fc86a003a65b`; no saved task/evidence/database files
were deleted. Unrelated owner edits in `Config/DefaultEngine.ini`, the lobby map
and `BP_Grenade` are excluded from the migration commit.
