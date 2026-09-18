# PurchasedArms04: jump from Shift sprint

Multica implementation: **MSQ-64**.

Authorized by the owner's 2026-09-18 request; see
[exact scope](../Approvals/PurchasedArms04-OwnerScope01.json) and
[standing focused-verification rule](../Approvals/FocusedVerification01.json).

## Required result

Allow Space to jump while moving with held Shift in the retained lobby. The
vendor calls Shift "run" and Alt "tactical sprint"; respect the owner's intended
Shift control without remapping controls. Use a modest vertical increase, about
10 percent takeoff velocity as an initial tuning choice, and retain momentum for
a farther jump. Ordinary jump remains unchanged. A stationary Shift press alone
must not grant a running boost. Preserve existing busy/crouch and airborne gates.
Keep source jump/landing presentation coherent with the actual airborne duration,
restore ordinary settings after landing, and recover held/released Shift naturally.
Handle the closely shared Alt path coherently if the same gate is changed, without
adding another amplified jump tier or expanding the feature scope.

## Bounded execution and acceptance

Use the existing Multica Unreal executor, Astra/max/standard, one production writer
and one heavy workload. Read ProjectState, this task, relevant native pawn/source
jump graphs and PurchasedArms02 implementation. Read-only independent findings may
be available at `Saved/PurchasedArms04/Controller/source-audit.md`.

Record starting Git status and affected hashes. Prefer official Epic MCP and verify
live project/PIE/dirty state before mutations. Preserve owner state, vendor source,
all prior sources/evidence and the heading-independent ADS fix. Keep map and asset
bytes unchanged if native adaptation suffices. No new dispatcher or test framework;
reuse existing input probes, evaluated telemetry and capture utilities.

- Establish the present native/source jump gate and make the smallest coherent fix.
- Verify actual input-driven ordinary versus Shift jump on comparable flat ground:
  successful takeoff, measured apex and travel, complete landing presentation and
  recovery. Validate held/released Shift and a subsequent ordinary jump so boost
  state does not leak. Check repeated airborne Space and retained disallowed gates
  only as directly affected. One Alt case suffices if its shared behavior changes.
- Use modest tuning, report actual height/distance and explain the contribution of
  existing movement speed; do not introduce a dash or arbitrary horizontal launch.
- Build/load the changed code and inspect short actual first-person jump/landing
  views. No full animation, shooting, reload, traversal or unrelated ADS matrix.
- Leave PIE stopped, the retained lobby ready for Play, no unsaved task mutations.
- Deliver `Docs/PurchasedArms04.md`, exact changed paths, scoped results and limits;
  generated evidence under `Saved/PurchasedArms04/Worker/`.

Worker owns implementation and focused checks only. Controller owns task/approval
documents, profiles, issue closure, handoff review and task-scoped local commit.
No purchases, source deletion, paused character/environment work or unrelated
cleanup. Continue to a verified result; dispatch or diagnosis alone is not done.

## Bounded presentation correction from controller review

Initial physics checks pass, but the actual `Views01-ShiftHeld` recording around
1.50 seconds shows almost the entire rifle/arms outside the viewport. The ordinary
jump retains them. See `Saved/PurchasedArms04/Controller/visual-review-note.md`,
the actual extracted `Controller/Views/` images and `visual-source-review.md`.
The source jump is a local-space additive authored against the standing idle pose;
the current running locomotion base is incompatible with it. This new combination
was prohibited by the source's original run gate.

Correct only the jump/landing presentation so it uses a compatible base through
the authored landing tail, while preserving physical fast-movement state/speed,
held/released Shift recovery, ordinary jump and unrelated action gates. Keep the
initial evidence unchanged. Recheck only the affected jump transitions; no broad
animation sweep or repeated unrelated passing checks. Worker must address this
observed issue before final handoff, not infer visual success from montage activity.
