# MSQ-103 / CAI-01 primary technical review

Independent source review, 2026-09-23. **PASS for the authorized build/source
verification of Candidate01/build05.** No open technical finding. The controller
confirmed the Multica executor completed without an error before this verdict.
Gameplay and owner acceptance remain separate below.

Authority: [CAI-01](Tasks/CombatAI01/CAI-01.md),
[owner start and verification boundary](Approvals/CombatAI01-CAI01-OwnerStart01.json),
and the controller's `Saved/CombatAI01/CAI-01/Controller/review-brief.md`.
This is the sole primary independent technical review. Controller acceptance,
preservation, task administration and closure commit remain separate.

## Reviewed contracts

| Criterion | Source review conclusion |
| --- | --- |
| Persistent encounter alert | `CombatAIAction.h` separates alert, observation time and action state. `EnemyCombatPolicy.cpp:5` and `:20` retain memory when search or tactical failure begins. The four-second memory expiry and automatic return are removed; the pursuit deadline fails an action without clearing alert. Explicit stop, pause/reset and death remain memory-clearing lifecycle boundaries. |
| Fresh evidence during backoff | `EnemyCombatPolicy.cpp:99` samples perception before backoff selection and reload handling. Movement, weapon and search-point backoffs have distinct storage. A new observed destination outside the failed neighborhood remains eligible. Build05's `:160` correction allows an already in-range observation to brake into aim after a failed closing route. |
| Knowledge boundary | Only successful `TryObservePlayer` in `EnemyCombatComponent.cpp:136` refreshes last-known aim/ground. Search/navigation read the recorded positions and actual self feet, with no hidden player-transform read. `SetRifleAimTarget` disables the follow-player seam. Fire independently rechecks sight at projectile birth. |
| Bounded preliminary search | `EnemyCombatPolicy.cpp:31` selects nine fixed proposals, validates movement through the retained local planner, advances failed proposals with a pause and inserts a cycle pause. Arrival observes an outward sector at `:67`. Search failures cannot replace the pursuit destination backoff. These are proposals and facing directions; visibility coverage and runtime reachability are not established. |
| Action lifecycle and identities | `EnemyCombatComponent.cpp:32` starts/updates a mutually exclusive action, records replacement cancellation and terminal outcomes. `CombatAIAction.h` rejects stale tokens and prevents repeated completion. Reset increments identity even within the same encounter generation. Paths hold their original request; reload commits ammunition only after `FinishAction(ReloadRequest)` succeeds at `EnemyCombatPolicy.cpp:129`. |
| Movement cancellation | `EnemyCombatNavigation.cpp:97` rejects obsolete incremental planning requests; `:204` rejects obsolete movement submission. Destination replacement clears the old path before replacement planning. `ClearIntent` clears path/frontier and burst state, stops movement and releases aim-follow state. No asynchronous callback system is added. |
| Physical handover and reset wiring | `GASPEnemyFixture.cpp:71` immediately cancels combat when physical authority changes; `EnemyCombatPolicy.cpp:86` checks death/authority before readiness and decisions. Living interruption preserves memory, then `:94` restarts search, with `PlanPath` taking actual feet. Fixture reset/EndPlay call combat cleanup; `CombatProjectileWorld.cpp:611` increments encounter generation before target reset. The retained Mover command bridge remains the movement authority. |
| Explicit gait and stationary launch | `EnemyCombatNavigation.cpp:217` selects gait by purpose, approach distance and corner angle, then submits normalized direction plus the walk flag. The imported graph audit supports the actual walk/run mapping below. `CanShoot` remains byte-equivalent at source-function level to the prerequisite, including velocity-derived movement alpha, pose/alignment and swept corridor checks. The policy stops movement and waits before aiming/fire. |
| Weapon/time boundaries | `EnemyCombatComponent.cpp:192` rejects stale burst requests before a fresh sight check and finite projectile launch. Magazine consumption and bounded world-time cadence remain; cancellation does not erase already launched bullets. Player rifle, projectile world, slowdown, physical fixture and rifle bridge implementations are unchanged from the prerequisite. |
| Observability | Schema 2 exports alert independently from sight evidence, action identity/outcome/reason, search anchor/look and requested gait in the retained bounded ring. It is a diagnostic tail, not full deterministic policy/physics replay. |

## Evidence and limits

Evidence root: `Saved/CombatAI01/CAI-01/Worker/Candidate01/`.

- Frozen `candidate-manifest.json` SHA256:
  `8895cac07915989168fa7e52573a31e3589d6ba3a4b25ef9c60b9e7ef63e3272`.
  All 19 applicable reviewed source/script/handoff/build/gait/check/DLL entries
  match, recorded in `Saved/CombatAI01/CAI-01/Review/reviewed-identity.json`.
  Final DLL SHA256:
  `33557055caf7012005c525eef0482ed0cd22e82e99c16e67e8502bafe65455ae`.
  The frozen executor report's pending-review wording records its handoff state;
  this separate report supplies the subsequent review result without rewriting it.
- `build05.log` records a successful native Development Editor build, four actions,
  4.65 seconds. The earlier build04 is not the final policy binary.
- The final `self-check.json` contains 35 passing checks, matching the frozen handoff.
  `pure-test-build.log` and `pure-test.log` support the shared production-header
  assertions, including 10,000 bounded search/failure transitions, token rejection
  across five action kinds, one-shot reload completion and gait selection.
- The pure checks exercise value contracts. String/function checks constrain source
  structure and preservation; neither executes Unreal's policy/navigation/physics.
  This review separately traced the affected production callers and control flow.
- `pure-test-initial.log` and `self-check-initial.json` preserve the initial failed
  assertion. The assertion expected a previous canceled outcome after subsequent
  actions. The final test correctly checks the action's reset state and does not
  remove stale-token or reload assertions to obtain a pass.
- `gait-mapping.json` shows the executed `Get_Gait` entry branch calling
  `CommandedWalk`, with true returning enum 0 and false enum 1. `ProduceInput`
  writes that result to the custom Mover gait. `gait-movement-mode.json` connects
  gait 0/1 to walk/run defaults 165/375 cm/s and the maximum-speed override;
  crouch has a separate override. These are graph/default facts, not observed
  movement speed. The existing native setter still normalizes direction.
- No build, pure checks or gameplay matrix was rerun by the reviewer. No editor
  operation, PIE, shot, asset edit or production change was performed.

S01 (60 world seconds hidden), S06 (physical displacement/recovery), S07 (actual
failed-route alternatives), S10 (live reset/death/stale-action behavior), visible
running/braking, motion, combat feel and performance remain **PENDING OWNER**.
Their absence is the explicit authorized verification boundary, not a failed
source-review gate. The package does not claim Recast, multi-room coverage,
hearing, incoming-fire awareness, moving fire or successor features.

## Findings

No blocking or nonblocking source defect identified in the reviewed bounded scope.
No correction request remains open. The build05 in-range fallback, search/pursuit
backoff separation, outward dwell direction and same-generation reset safeguards
were executor corrections made before candidate freeze; they are included in this
review, not represented as independent findings retroactively.
