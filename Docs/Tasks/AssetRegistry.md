# Minimal asset registry

Status: Multica issue MSQ-3, backlog; implementation has not started.

Provide a small queryable inventory of accepted asset files and dependencies so
an agent can find the correct sources and identify stale downstream outputs.
Reuse the existing local PostgreSQL instance with a separate project asset
database and appropriately scoped credentials. Multica continues to own tasks;
its application schema and tables are outside this task's write scope.

## Deliverable

- Versioned SQL migrations and small command-line commands to register,
  inspect and validate assets. Reuse the installed PostgreSQL tools and Python.
- Stable asset IDs, project-relative file paths, artifact roles, SHA-256, size,
  associated Unreal package paths, dependency relationships and check evidence.
- Explicit evidence/source and verification status for relationships. Do not
  mark a dependency verified merely because a filename suggests it.
- Register PipelineProbe, BenchA and BenchB from their saved accepted outputs
  and existing verification reports. Record missing evidence honestly.
- Document local setup, repeatable usage, credential location, and database
  backup. Secrets and generated reports stay outside Git.

Binary data remains in files and Git LFS. No extra service, graph database,
embeddings, web dashboard, paid API or model-generated descriptions are needed.
Read only the relevant documentation/report sections; do not load full native
conversation traces or rebuild the orchestration benchmark.

## Acceptance

1. Inspecting one asset returns its Blender/Painter sources, exported maps and
   Unreal packages, plus the evidence supporting their relationships.
2. Repeated registration is idempotent: no duplicate logical assets or edges.
3. Validation detects a changed or missing artifact and reports the affected
   downstream dependency chain, with uncertainty preserved for unverified edges.
4. Exercise changed/missing-file cases with temporary fixtures under Saved;
   preserve all accepted asset bytes and do not open or mutate the DCC editors.
5. A fresh migration followed by a second migration invocation is safe. The
   asset database does not modify Multica's database or task records.
6. Return a concise English report with commands, results, remaining limitations
   and local evidence paths. Keep full logs under Saved/AssetRegistry.

Use one Astra worker at standard speed with reasoning suited to this bounded
code/database task. DCC MCP servers should be disabled for this task. Existing
subscription authentication is required; do not delegate. Record native usage
once, including any corrections, and stop when acceptance is satisfied.
