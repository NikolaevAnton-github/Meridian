# Local Multica pilot

Recorded September 13, 2026. Multica passed the first read-only orchestration
gate on this Windows computer. It runs native local components; Docker, WSL,
Windows services and additional paid services are not part of this deployment.
The existing Codex subscription remains the only model-service budget.

## Pinned components

| Component | Version / location |
| --- | --- |
| Multica | `v0.4.43`, commit `2ae2dbbb8f9ed9ffe1739ecf5abfe31a940ee50c` |
| Source | `.tools/multica/source/` |
| Go | Portable `1.26.8`, `.tools/multica/go/` |
| PostgreSQL | Portable `17.11`, `.tools/multica/pgsql/` |
| pnpm | `10.28.2`, `.tools/multica/node-tools/` |
| Node | Existing Rider runtime `24.13.0`; absolute path in the launcher |
| Web | Production Next.js 16 build |
| Codex | Native CLI `0.153.4`, existing ChatGPT authentication |

The official Windows Multica release supplies the CLI/daemon and Desktop app,
not prebuilt API/migrator binaries. This installation builds `cmd/server`,
`cmd/migrate` and the web app from the pinned source. PostgreSQL uses the
required `pgcrypto` and `pg_trgm` extensions; migrations passed.

Local source changes bind the API to loopback and set Next.js
`experimental.cpus=1` plus `experimental.webpackMemoryOptimizations=true`.
Next.js also regenerates `apps/web/next-env.d.ts` for the production build;
that generated difference is not part of the source patch.
The reviewable patch is [multica-0.4.43-local.patch](../Tools/Patches/multica-0.4.43-local.patch).
Dependency pins and download details are recorded in
[multica.json](../Tools/Requirements/multica.json). Preserve the patch when
recreating the checkout; do not enable automatic updates across this pin.

## Start, stop and access

Run from `D:\devgames\MeridianSquad`:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File Scripts/multica.ps1 Start
powershell.exe -NoProfile -ExecutionPolicy Bypass -File Scripts/multica.ps1 Status
powershell.exe -NoProfile -ExecutionPolicy Bypass -File Scripts/multica.ps1 Stop
```

The execution-policy option applies only to that PowerShell process; it does
not change the machine or user policy. The launcher starts components hidden,
records process identity and checks readiness. It waits for the runtime to
stop before stopping API/database; an unfinished runtime keeps those services
available. PostgreSQL is controlled with `pg_ctl`, without registering a service.

| Endpoint | Address |
| --- | --- |
| Web | `http://127.0.0.1:3000` |
| API | `http://127.0.0.1:8080` |
| PostgreSQL | `127.0.0.1:15432` |

All three listeners bind to loopback. Open the web address locally. Login
instructions and the local code are stored only in `Saved/Multica/Login.txt`;
do not copy that file or its contents into tracked documentation or reports.

## Private state and operating policy

- `.tools/multica/local-config.json` holds the launch environment and local
  secrets. The launcher reads it; backend binaries do not load `.env` themselves.
- The named CLI profile is `%USERPROFILE%\.multica\profiles\meridiansquad\`.
  Its `config.json` contains authenticated local connection state. Keep it private.
- `.tools/multica/` is ignored by Git and contains tools, source, binaries,
  downloads and project-specific Go/pnpm caches.
- `Saved/Multica/` contains `postgres-data/`, local uploads/logs, lifecycle state
  in `processes.json`, and backups. Generated evidence lives under
  `Saved/AgentSetup/MulticaProbe/`. These directories stay outside Git.
- The runtime and agent each allow one concurrent task. The agent uses Astra,
  medium reasoning and `service_tier=default` through existing ChatGPT auth.
  The current pilot agent is restricted to reading documents, not asset editing.
- Server LLM assistance is disabled: `MULTICA_LLM_API_KEY` and
  `MULTICA_LLM_BASE_URL` are empty. No paid API credentials are required.
  Telemetry and automatic updates/reloads are disabled for this local pilot.
- The project resource uses `in_place` execution at the existing project root.
  It does not create a duplicate Unreal checkout or worktree. Keep one writer
  per running DCC instance and one heavy build/bake/render/model workload at a time.
- The 250 GB project disk limit includes this stack, its caches and retained
  task data. Review retention before expanding task volume; never reclaim space
  by deleting user assets.

The operational PostgreSQL database stores Multica task/workspace state. The
planned asset-metadata schema and asset relationships have not been implemented.

After setup, the project contained approximately 8.69 GiB of file lengths
(7.79 GiB counting hard-linked files once). The Multica tools/source/build/cache
directory accounted for 5.67 GiB before hard-link deduplication. Dependency
junctions were not followed; installed Unreal/DCC applications are outside this
project measurement. No user assets were removed. Idle Multica/API/web/PostgreSQL
processes together measured approximately 425 MiB of working set and 364 MiB
of private committed memory; working-set sums can count shared pages more than
once. Model execution and DCC workloads need separate measurements.

## Direct rebuild reference

Use the pinned checkout with the tracked patch applied. Stop the stack before
replacing running binaries. Run heavy builds sequentially. These commands rebuild
already provisioned components; they are not a complete installation procedure.

```powershell
$multicaRoot = Join-Path $PWD '.tools\multica'
$nodeExe = 'C:\Users\Origa\AppData\Local\JetBrains\Rider2026.2\acp-agents\.runtimes\node\24.13.0\node.exe'
$pnpmScript = Join-Path $multicaRoot 'node-tools\node_modules\pnpm\bin\pnpm.cjs'
$env:PATH = (Split-Path $nodeExe -Parent) + ';' + $env:PATH
$env:CGO_ENABLED = '0'
$env:GOMAXPROCS = '2'
$env:GOCACHE = Join-Path $multicaRoot 'go-cache'
$env:GOMODCACHE = Join-Path $multicaRoot 'go-modules'
& "$multicaRoot\go\bin\go.exe" -C "$multicaRoot\source\server" build -p 1 -trimpath -o ..\..\bin\server.exe ./cmd/server
& "$multicaRoot\go\bin\go.exe" -C "$multicaRoot\source\server" build -p 1 -trimpath -o ..\..\bin\migrate.exe ./cmd/migrate
$env:NEXT_TELEMETRY_DISABLED = '1'
$env:NODE_OPTIONS = '--max-old-space-size=2048'
& $nodeExe $pnpmScript --dir "$multicaRoot\source" --filter '@multica/web' build
```

Check each exit code before proceeding. The build does not require a C compiler.
The initial frozen pnpm installation used the pinned lockfile and the local
`pnpm-store/`; preserve those dependency pins when restoring dependencies.
Run `migrate.exe up` with the private database environment and working directory
`.tools/multica/source/server` only when provisioning or deliberately upgrading
the matching schema. Ordinary `Start` does not rerun migrations.

## Verification and limits

- Read-only issue `MSQ-1` completed in one attempt, approximately 47 seconds.
  Its reported working directory matched `D:\devgames\MeridianSquad` exactly.
- SHA-256 checks confirmed restoration of `AGENTS.md`, the project Codex config
  and the user's global Codex config after the pilot.
- API/migrator and production web builds passed. Stopping and restarting all
  components passed, and the completed result remained available in PostgreSQL.
- Visual browser verification was unavailable because computer-use reported no
  browser. HTTP/build checks do not establish visual layout or interactive UI QA.
- Multica reported 14,587 uncached input tokens, 54,912 cached input tokens and
  384 output tokens. Total input was 69,499 across three model responses; this
  is accumulated usage, not a unique context size. It does not measure money
  billed or the remaining subscription quota.

The pilot also measured a 15,682-byte Multica instructions block added to the
original 2,456-byte `AGENTS.md`. The model read the issue and its comment history
before reading project rules. These are upstream workflow costs. Use complete
tasks with acceptance criteria rather than creating a separate issue for every
small file read or command.

After this measurement, the document-reading pilot agent received task-local
CLI overrides disabling `unreal_epic`, `blender` and `substance_painter` MCP.
A prompt prohibiting MCP calls did not prevent those servers from starting in
the original run. Shared/project Codex config files are unchanged. The override
configuration was checked; its effect and token savings have not been measured
in a second run. Asset tasks need their own appropriate tool configuration.
All subsequent Multica reports are explicitly instructed to use English.

Full evidence is under `Saved/AgentSetup/MulticaProbe/`. The local database dump
is `Saved/Multica/backups/pilot-20260913.dump`. It is a same-disk backup, not an
off-device disaster-recovery copy or proof that restore has been tested.

This gate establishes read-only task dispatch, execution and reporting. The next
gate is one bounded real DCC asset task with explicit acceptance checks and
coordinated ownership of the running editors. Define finer task/context/retry and
retention budgets from measured accepted work, including rework, before scaling
the number or autonomy of agents. Multica remains the task orchestrator; the
PowerShell launcher only manages local component lifecycles.

## Primary sources

- [Multica v0.4.43 release](https://github.com/multica-ai/multica/releases/tag/v0.4.43)
- [Pinned self-hosting guide](https://github.com/multica-ai/multica/blob/v0.4.43/SELF_HOSTING.md)
- [Pinned build definitions](https://github.com/multica-ai/multica/blob/v0.4.43/Dockerfile)
  and [web build](https://github.com/multica-ai/multica/blob/v0.4.43/Dockerfile.web)
- [Go downloads](https://go.dev/dl/)
- [PostgreSQL Windows distribution](https://www.postgresql.org/download/windows/)
  and [EDB binary archives](https://www.enterprisedb.com/download-postgresql-binaries)
