# ContextBudget02 global config preservation audit

**Byte preservation failed; no ContextBudget global config writer was found. Preserve the current file.**

- The initial hash was `a5493bff7af024690f868f67b4e43109d563b450eb948195abca4d6b622ce181`; current hash is `20cd2e358d4dbf6355778de282687961bfa46fa3d06c44b7a223cd690a1f3d50`. Exact values/timestamps are recorded in `global-config-review.json`.
- Global creation/write timestamps are both 17:52:15.690Z, consistent with atomic replacement. The installed issue began at 17:52:37Z, about 21 seconds later. Its task execution therefore cannot have caused this prior write. The file currently has one NTFS hardlink.
- `execenv/codex_home.go:17-29,231-243,1353-1416` shares only auth and creates config as a separate regular file after removing any stale destination. `execenv.go:635-642` selects the private home; `daemon.go:8121` sets `CODEX_HOME` to it. `context_budget.go:206` rewrites that private config. `native_smoke.py:22-29,125-128` explicitly selects its Saved role home and links only auth. No reviewed ContextBudget path writes the global config.
- Safe inherited-copy comparison identifies Node REPL/browser executable, module/trust/service/pipe integration fields and the new `shell_environment_policy.set.NODE_REPL_TRUSTED_BROWSER_CLIENT_SHA256S` field. The browser app version changed from `26.917.62051` in the inherited copy to `26.917.71314` globally. This supports an independent host integration refresh. Model/notify and task-only settings in that comparison are not reliable global deltas.

The original evidence stores only a hash, and the older private copy includes task overrides. The exact original bytes/diff and writer process cannot be reconstructed or conclusively attributed from these artifacts. Do not replace current host configuration with an old task copy or rebaseline the original preservation record. No restoration or production mutation was performed.
