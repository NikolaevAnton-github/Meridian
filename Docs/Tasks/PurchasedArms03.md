# PurchasedArms03: heading-independent rifle aiming

Multica implementation: **MSQ-63**.

Authorized by the owner's 2026-09-18 lobby play report. Read
[the exact scope](../Approvals/PurchasedArms03-OwnerScope01.json).

The rifle aiming pose progressively misaligns when turning away from the initial
spawn axis, with the reverse heading showing the largest error. Diagnose and fix
the actual source/native animation integration. Do not retune around one heading.
The two original owner screenshots are preserved under
`Saved/PurchasedArms03/Owner/`; use them as observed symptom evidence.

## Bounded execution

Use one existing Multica production executor, Astra/max/standard, one editor writer
and one heavy workload. Read ProjectState, this task and relevant PurchasedArms02
implementation/source. Do not restart the old broad feature/movement acceptance
matrix. The later owner instruction explicitly limits verification to what the
fix directly affects. A read-only independent source audit may be available at
`Saved/PurchasedArms03/Controller/ads-source-audit.md`.

Establish the coordinate-space cause using source and evaluated runtime evidence.
Use official Epic MCP; verify the live project, PIE and dirty packages before
mutations. Use debugging-code if debugger-driven evidence is needed and Rider
debug tools are available; if unavailable, document that exact limit and use the
existing evaluated telemetry. Reuse existing graph/input/capture tools. Do not
create a dispatcher or rebuild the test harness. Preserve the starting Git state,
bounded rollback of changed binaries and all source/owner/history bytes.

## Acceptance

- Reproduce the original defect before the change at initial, quarter-turn and
  opposite headings using held aim and comparable camera-space measurements/views.
- Make the smallest coherent fix, preserving source recoil, hand IK, camera comfort
  and normal aim entry/exit. Cover canted aim/pitch only as directly affected by the
  same coordinate conversion; do not expand into locomotion or action regression.
- Verify stable aiming at 0, +90, 180, -90 and back to the initial heading, including
  held-aim turning and releasing/re-entering aim away from spawn. Check a nonzero
  pitch and canted aim if the changed transform path serves them. Avoid unrelated
  movement, jump, crouch, traversal, reload matrix or full feature tests.
- Validate changed code/assets compile and load, use actual comparable first-person
  screenshots and evaluated transforms, and leave PIE stopped with the retained
  lobby ready for Play. Never modify the lobby map or untouched vendor source to
  compensate for the defect. Keep all player presentation shadowless.
- Record cause, fix, focused results, limits and changed-file inventory in
  `Docs/PurchasedArms03.md`; evidence under `Saved/PurchasedArms03/Worker/`.
  Update current source metadata only if binaries change; preserve historical
  manifests/acceptance identities and provide hashes for controller registration.

Worker owns implementation and focused checks only. Controller owns task/approval
documents, profiles, issue closure, independent handoff review and the required
task-scoped local commit. No new paid services, art, source deletion, paused
character/environment work or unrelated cleanup. Continue to a verified fix.
