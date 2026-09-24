# CAI-T03: Mobile enemy fire and torso-lean cover peeking

Multica issue: **MSQ-120**. Parent: MSQ-101. Authorized 2026-09-24 by the
[owner follow-up](../../Approvals/CombatAI01-MobileLean01-OwnerStart01.json).
Read [ProjectState](../../ProjectState.md) first. Baseline: MSQ-119
Candidate02/build01 and current source; see its
[acceptance](../../CombatAI01-CoverFire01Acceptance.md).

Delivered **Candidate01/build03** for owner testing. Native build, 67 production
assertions, 18 native pose cases and the sole primary technical review pass.
The reviewer adds 33 passing scan/selection/edge-route checks. All 298 current
and archived manifest entries match. See
[handoff](../../CombatAI01-MobileLean01.md),
[review](../../CombatAI01-MobileLean01Review.md) and
[controller acceptance](../../CombatAI01-MobileLean01Acceptance.md).
The owner's active Play session is preserved; motion/play judgement remains owner-only.

## Requested behavior

The owner wants a more dynamic opponent who fires while moving and peeks around
corners with an actual left/right torso lean, comparable to Q/E in shooters.
The earlier lateral step-outs do not fulfill this clarified posture requirement.
This authorizes a bounded follow-up, not the remaining full CAI-03/04/05 packages.

1. Implement useful bounded combat movement while maintaining independent rifle
   aim and fire: deliberate short lateral reposition/strafe and cautious approach
   when useful, at weapon-appropriate range. Merely removing a stationary gate
   while the policy still stops every burst is insufficient. Avoid constant random
   weaving, rush-to-player behavior and move/stop oscillation. Prefer existing
   navigation, action ownership and typed weapon context; expose compact tuning.
2. Support firing during achieved controlled grounded movement, with an explicit
   movement-dependent accuracy cost and an honest supported speed/gait envelope.
   Preserve current sight, aim, muzzle/near-cover obstruction, finite projectile,
   cadence, reload, ammunition, world-time and physical-authority gates. A running
   reposition may lower the rifle if outside the supported envelope; communicate
   exact limits. Do not keep contradictory stationary-only launch consumers.
3. Add smooth signed upper-body lean at left/right cover edges, with pelvis/legs
   retaining grounded locomotion support and rifle/hands following the upper body.
   Do not rotate the entire pawn/capsule or fake leaning using a step-out/flag.
   Reuse existing native/AnimBP seams; a bounded procedural pose is acceptable.
   Preserve aim pitch/yaw and hit/recovery authority. Both sides are independent.
4. Integrate lean with actual static cover geometry: choose a reachable protected
   anchor/edge, validate leaned head/torso/rifle clearance and firing space, then
   blend out, acquire current sight, fire a finite burst and blend back. A small
   preparatory foot adjustment is allowed, but exposure must use torso lean.
   Revalidate actual achieved pose/muzzle; traces and projectile origin must agree
   with the achieved visible posture. Never shoot through a corner or inspect a
   hidden player's live location to choose a lean. No-contact/blocked-side fallback
   must terminate or replan with bounded work and diagnostic reason.
5. Keep the existing low-cover stand/burst/crouch behavior compatible. Interrupt,
   death, recovery, disable, weapon loss and reset cancel mobile/lean ownership,
   pending fire and stale offsets; replan from actual current position after recovery.
   Movement/lean/low-cover transitions must not fight for stance or movement.
6. Extend existing status/trace with mobile-fire/lean state and actual gate reasons.
   Preserve all owner edits and previous candidates. No player Q/E controls, new
   weapons, group AI, map changes, player health or unrelated task dispatch.

## Acceptance and evidence

The executor implements and self-checks; one primary independent technical reviewer
owns ML01-ML06. Controller accepts scope, evidence identity and finding closure.

- ML01: production policy actually requests bounded useful combat movement while
  valid fire continues; no forced stop-per-shot or range collapse. Cover/route
  failures and unsupported movement terminate or choose a safe bounded fallback.
- ML02: all launch producers/consumers use a consistent achieved-motion envelope,
  motion-dependent accuracy and existing current-sight/aim/muzzle safety. Preserve
  finite projectile cadence, ammo/reload and slowdown; reject physical interruptions.
- ML03: actual signed upper-body pose changes both left and right, feet remain
  supported, rifle/hands inherit the pose, aim remains coherent, and lean returns
  smoothly. Validate final pose wiring, not only a requested float or enum.
- ML04: both edge choices use actual geometry and permitted evidence; achieved
  head/torso/rifle space and muzzle authorize fire. Blocked side, lean refusal,
  stale contact and no lane cannot cause blind fire or an infinite action.
- ML05: mobile/lean/low-cover handoffs, interruption, recovery/death, weapon loss,
  disable and F6 reset clear incompatible ownership. Bound replanning and keep
  meaningful existing status/trace coverage.
- ML06: native Development Editor build and focused production code/pose-wiring
  checks pass. Cover adversarial affected transitions with real producer/consumer
  checks, not only string-presence assertions or mirrored predicates. Reuse
  unaffected evidence; do not run the whole animation/feature matrix.

No agent gameplay, PIE, firing, gameplay simulation/screenshots or performance
probes. Motion quality, cover usefulness, difficulty and feel remain for owner
play. Read-only editor/asset/geometry inspection is allowed. Before editor changes
verify actual project, retained map, PIE and dirty state through official Epic MCP.
Preserve unsaved owner assets and newly active owner sessions; report any blocker.
Guard necessary native rebuild/reload and leave matching ordinary editor ready.

## Execution and delivery

Initial read-only advisory: inspect EnemyCombatPolicy::AdvanceWeapon/AdvanceCombat,
EnemyCombatComponent::CanShoot/EnsureAction/ClearIntent and navigation PathRequest
ownership together. The current single action slot cancels Move when Aim/Burst
begins; simply deleting speed vetoes cannot satisfy ML01. GASPEnemyRifle and
GASPALSRifleAnimInstance already expose independent aim and moving rifle poses.
Scripts/GASPALSEnemy01/author.py documents the spine-layer/hand-IK graph seam;
verify actual current assets before edits. Treat these as leads, not acceptance.

One Multica production writer and one editor writer/heavy workload at a time.
Astra/max/default, fast disabled, configured and actual native settings verified.
Do not dispatch subexecutors/reviewers, change shared profiles/task status or commit.
Controller owns those actions. Preserve exact pre-edit binary sources; if assets
change, follow AssetRegistry revision/acceptance rules and keep historical bytes.

Deliver Docs/CombatAI01-MobileLean01.md with behavior, concrete tuning, changed
files, build/focused checks, limits and owner test route. Save bounded evidence
and an immutable manifest covering current source/assets/DLL/checks and preserved
inputs under Saved/CombatAI01/CAI-T03/Worker/Candidate01/. Use new candidate paths
for corrections. Do not alter earlier task evidence or broaden the requested scope.
