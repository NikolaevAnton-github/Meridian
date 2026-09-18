# PurchasedArms06: slightly brighter muzzle flame

Multica implementation: **MSQ-66**.

Authorized by the owner's 2026-09-18 lobby play feedback; see
[exact scope](../Approvals/PurchasedArms06-OwnerScope01.json).

Increase the current rifle muzzle flame brightness modestly. Preserve its size,
duration, color character, smoke, firing cadence, recoil, gameplay and lobby
lighting/exposure. Prefer the existing flame material's emissive multiplier;
choose a small visible increase from a matched before/after comparison.

Use the existing Multica Unreal executor, Astra/max/standard, concurrency one.
Read ProjectState, this task and the scoped decision. Read-only source findings
may be available at `Saved/PurchasedArms06/Controller/source-audit.md`.
Verify live project, PIE and dirty packages before changes through official Epic
MCP. Record actual native execution settings, starting Git status and affected
hashes. `Config/DefaultEngine.ini` is an existing owner edit; preserve it exactly.
Preserve original vendor sources, previous evidence and immutable manifests.
Back up any changed asset to `Saved/PurchasedArms06/Worker/Rollback/` first.

Make the smallest brightness-only change. Reuse existing capture/input utilities;
a narrow task adapter is allowed, no new test framework. Capture comparable actual
first-person hip and aimed shooting before/after under unchanged lobby lighting
and exposure, using a short burst to avoid judging a random flash variant alone.
Check the flame is visibly brighter without an excessive opaque bloom covering
the sight, and firing stops normally. Inspect affected asset load/material errors
and saved parameter readback. Do not run jump, movement, reload or full animation
regressions; do not rebuild native code unless a necessary code edit requires it.

Worker may edit the affected asset, a narrow reusable task script if needed, and
`Docs/PurchasedArms06.md`. Report the exact old/new values, changed paths/hashes,
focused results and evidence under `Saved/PurchasedArms06/Worker/`. Leave PIE
stopped, retained lobby ready for Play, no unsaved task changes. Controller owns
registry revision, task/approval/state documentation, issue closure and local
commit. No purchases, source deletion, paused character/environment work or
unrelated cleanup. Continue through bounded corrections to a verified result.
