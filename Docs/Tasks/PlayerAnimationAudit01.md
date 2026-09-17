# PlayerAnimation-Audit01: MSQ-52 execution

Authorized on 2026-09-17 by the owner's direct instruction to execute MSQ-52.
The same instruction selects **Concept02 / Candidate01, 16 / Datum**;
see [the exact selection and execution record](../Approvals/PlayerCharacter01-Datum16Selection01.json).
Earlier pending-selection and no-dispatch statements describe their historical
operations and are superseded within this scope.

## Bounded execution

Execute the existing MSQ-52 description and acceptance checklist. Use the
existing MeridianSquad Unreal profile with task-local Astra/high/standard and
restore its saved profile/native arguments after handoff and corrections.
One production worker owns Unreal for this operation. Do not start successors.

Read the [plan](PlayerCharacter01Plan.md), [task index](PlayerCharacter01Tasks.md)
and [pipeline](../PlayerCharacter01AI3DPipeline.md). Audit the actual installed
engine and sources, preserving `D:/devgames/Weapon` and its embedded
`/Game/InfimaGames/TacticalFPSAnimations/` package root. Inspect local UE rifle
locomotion first. Migrate only a dependency-closed selected art subset; no vendor
demo gameplay or whole external frameworks. Technical mannequin use is permitted.
Original body/model production, new AI generation and final materials belong to
later tasks. Preserve all owner edits and deferred lobby content.

Acceptance requires actual representative FP/TP character and rifle playback in
Unreal, the four selected reload counterparts, contact/timing findings, crouch
blend-space inspection, and explicit coverage/gaps for directional walk/run,
crouch movement, jump/land, planted stepping turns and pivots. A filename or asset
load alone does not prove playback, animated legs or correct hand contact.

Provide a concrete skeleton contract with actual hierarchy, finger/twist/IK
bones, units/axes, root orientation, bind/retarget poses, import/export settings,
body/FP/world interfaces, and dimension/contact constraints. Preserve current
34/88 cm capsule and 170 cm standing camera baseline; distinguish measured source
dimensions, technical recommendations and owner-approved design. No invented
owner-approved body height. Missing motions need bounded later sourcing/authoring
actions, not a false full-coverage claim.

## Verification and handoff

- Confirm live project/editor/PIE/dirty state before mutation; prefer official
  Epic MCP. Do not discard dirty owner work or save the lobby to make a preview.
- Use temporary/transient preview fixtures outside shipped content and restore
  the prior editor/map state when feasible without touching owner edits.
- Measure project disk/storage growth; keep the complete project within 250 GB.
- Record source/subset hashes and dependency closure, provenance, skeleton data,
  animation metadata, playback evidence and missing-clip actions under
  `Saved/PlayerCharacter01/AnimationAudit01/Worker/`.
- Write the concise tracked handoff to `Docs/PlayerAnimationAudit01.md` and rig
  contract/selected-source manifests under `Assets/Source/PlayerCharacter01/`.
  Track intended binary assets with Git LFS. Reuse existing verification tools.
- Do not edit controller-owned ProjectState, task plan/index, approval records,
  this dispatch file or controller evidence. Do not change task states/profiles,
  post comments, commit/push, delegate or create tasks. Return an English handoff.
- The controller verifies the result and handles bounded corrections before
  completing MSQ-52. Later original-rig retarget quality remains a separate gate.
