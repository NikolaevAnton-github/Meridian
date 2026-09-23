# MSQ-104 / CAI-02 primary technical review

Date: 2026-09-24. Reviewer: MeridianSquad Code. **CHANGES REQUESTED** for
**Candidate02/build01**: CAI02-R1 (high) and CAI02-R2 (medium).

This is the first independent technical review of the integrated senses,
protected-movement and navigation delivery. It includes Candidate01's unchanged
implementation, not only Candidate02's navigation delta. The review is limited
to source, frozen evidence and narrow deterministic checks. Gameplay, motion,
audibility, difficulty, actual map-position usefulness and performance remain
**PENDING OWNER**. No editor, PIE, gameplay simulation or firing probe ran.

Authority: [task](Tasks/CombatAI01/CAI-02.md),
[owner follow-up](Approvals/CombatAI01-CAI02-OwnerStart01.json), current Multica
review assignment and its controller integration note. The controller retains
scope/evidence acceptance, correction coordination, issue administration,
ordinary editor reload and the local closure commit. No production files,
profiles or issue status were changed by this review.

## Candidate and applicable evidence

- Final manifest: `Saved/CombatAI01/CAI-02/Worker/Candidate02/candidate-manifest.json`.
  SHA-256: `2cf9d388930e7bc4142053a3eb38f7039980feff4b2736622c1a00d78f8d0566`.
- DLL SHA-256: `cf138423924d3bc3a820de26c6d6f9970dc01879265bcc94ad00edbada8203aa`.
- Baseline commit: `c4da5eaaf5793556c3a0884a10ad975573d6a0e0`.
- The 97 manifest entries match both working files and the frozen Candidate02
  archive. Direct source inspection therefore applies to the named candidate.
  Record: `Saved/CombatAI01/CAI-02/Review/candidate-identity.json`.
- Read together: [base handoff](CombatAI01-CAI02.md) and
  [navigation correction](CombatAI01-CAI02Navigation01.md). The latter supersedes
  the former's 28 m navigation limit, not its sensory/audio implementation.
- Reused Candidate02 native build success (`build01.log`, 23.43 seconds), 202
  navigation assertions and 16 supporting checks (`checks-check01.json`). Only
  the two tuning defaults and three radius clamps differ from Candidate01.
- Reused Candidate01's 66 pure assertions, 22 extracted-method assertions and
  supporting source checks (`checks-check04.json`), actual audio/notify graph
  audit, saved animation-class ancestry and retained geometry inventory.
  Their passing results are applicable but do not cover the two gaps below.
- Reviewer Astra/max/default is supported by the controller's configured/native
  capture and this run's local turn context. Fast mode is disabled. The sanitized
  record is `Saved/CombatAI01/CAI-02/Review/reviewer-settings.json`.

## Findings requiring correction

### CAI02-R1 — High: recurring fresh sounds can prevent any position selection

`Source/MeridianSquad/EnemyCombatSenses.cpp:44` treats a sufficiently shifted
sound region as a new investigation and calls `BeginSearch` at line 53.
`EnemyCombatPolicy.cpp:7` clears the current action and calls
`ResetTactics(false)`. Although history and transfer counts survive, the reset
at `EnemyCombatTactics.cpp:19` discards all candidates and scan progress.
`BeginTacticalScan` at line 179 also restarts the four-second scan deadline.
Selection can occur only after the incremental work or that deadline completes
(`EnemyCombatTactics.cpp:243`). There is no bound on how long a stream of new
regions can keep restarting this work.

The new pure check executes nine verbatim production methods, including the
consumer, intent update, search reset, candidate generation and scan scheduler.
With a stationary listener, stable supported geometry and one sound, selection
is reached with 35 candidates evaluated. With 20 accepted step records over
eight world seconds, spaced 0.4 seconds apart and moving the permitted region
200 cm at a time, it records **20 search restarts, zero selections**, and at
most eight candidates evaluated in each discarded scan. Selection becomes
reachable again after the sound stream stops. The fixture uses allowed stimulus
values and deterministic geometry callbacks; it is not a gameplay measurement.

This couples the requested hearing improvement to repeated cancellation of
protected movement. An audible moving target can keep the enemy collecting
partial scans instead of completing a useful position decision. The existing
consumer test exercises isolated updates and stubs `ResetTactics`, so it cannot
detect this integration failure. Its pure commitment test also does not exercise
the reset path.

**Bounded correction:** coalesce compatible sound updates into current evidence
without continually clearing the scan/action. Preserve a finite decision deadline
across retargeting, and revalidate the selected point against the latest permitted
evidence before movement. Meaningful safety/authority changes may still cancel
work. Preserve transfer limits, spatial rejection history, uncertainty, immediate
attention and weapon gates. A continuing stream of ordinary regional updates
must allow a supported decision to complete within the declared work budget;
stopping the stream must not be a prerequisite. Add a focused repeated-sound
regression, including an update while moving and physical cancellation.

### CAI02-R2 — Medium: crouched observation still validates standing probe heights

Search now requests actual crouch at `EnemyCombatTactics.cpp:397`, but
`AssessTacticalPosition` still uses fixed chest/eye heights of 95/150 cm
(line 130), a 125 cm weapon root (line 145), and a 130 cm self-exposure origin
(line 162). These queries do not consume achieved or proposed stance. The
arrival and held-position checks reuse the same assessment at lines 404 and
368, so validating actual feet does not repair the height mismatch.

The narrow extracted-method check changes achieved stance while keeping feet,
evidence and geometry identical. It records **the same 29 visibility/weapon
query segments for standing and crouching**. An analytical ledge at 120–140 cm
rejects the front-facing 125 cm weapon probe in both cases, even though the
fixture's lower crouched weapon corridor is clear. The fixture demonstrates the
missing stance dependency, not a measured socket height or a claim about a
particular obstacle in the retained map. Conversely, fixed-height probes cannot
establish clearance or exposure for geometry that occludes only the lower pose.

Capsule support/clearance already uses actual capsule dimensions. Actual GASP
crouch and quiet audio wiring also exist. The defect is specifically the
visibility, exposure and useful weapon-facing assessment used to choose and
accept the position; a stance boolean alone cannot make those probes applicable.

**Bounded correction:** use an explicit compatible stance profile for candidate
body/eye/weapon probes, then verify it against achieved stance at arrival and
while holding. Reassess when the stance changes or cannot be achieved. Keep
the current launch-time socket/corridor safety checks. Add one height-sensitive
standing/crouched fixture and the affected return-to-standing transition; no
new assets, topology or full animation matrix are required.

## Remaining technical criteria

These are source/pure-check conclusions, not runtime or owner acceptance.

| Criterion | Review result and relevant implementation |
| --- | --- |
| Multiple approaches, protected side, nearby safe choice | PASS for the selection mechanism, subject to R1/R2 in execution. `EnemyCombatTactics.cpp:123` assesses five evidence-region approaches and eight local sectors; `CombatAITactics.h:143` prevents exposure being bought by view/protection rewards. The two-pass selection at `EnemyCombatTactics.cpp:266` selects shortest checked travel within 0.04 of the safest eligible exposure. |
| Reachable column detours and actual-feet arrival | PASS for route/arrival mechanisms, subject to stance applicability in R2. Static bounds generate opposite-side/corner candidates at `EnemyCombatTactics.cpp:214`; `CombatAITactics.h:185` caps the ring at 13 distinct strips and 1200 cm. The selected checked route is used at `EnemyCombatTactics.cpp:300`; actual feet, support and exposure are reassessed at arrival. This is local static geometry, not full topology. |
| Real crouch and audible enemy steps | PASS for wiring, with R2 separately open. `AdvanceSearch` requests crouch, `EnemyCombatNavigation.cpp:230` requests walking, and `GASPEnemyRifle.cpp:98` reaches CharacterMover crouch. `IsMovementCrouched` reads achieved Mover state; `GASPALSRifleAnimInstance.cpp:84` consumes it. `CombatStimulusWorld.cpp:91` uses achieved stance for the 0.06 volume/180 cm step presentation. Visible engagement requests standing at `EnemyCombatPolicy.cpp:119`; physical authority gates both movement and new enemy steps. |
| One grounded movement producer | PASS. `CombatAISenses.h:175` pays actual ground displacement, rejects stationary/blocked/airborne/discontinuous travel, and emits one established flight-to-ground landing. `CombatStimulusWorld.cpp:47` queues hearing before audio rendering. Generation reset clears accumulators. The audited player foot cue and GASP walk/run/crouch/scuff notifies are intercepted by `CombatLocomotionAnimInstance.cpp:8`; installed UE `AnimInstance.cpp:2053` confirms a handled notify returns before its ordinary callback. Saved player/GASP classes inherit this host. Enemy landing remains on its existing GASP route without a second generated landing. |
| Room-scale sight and honest contact retention | PASS. The retained 6080 × 2480 cm floor has a roughly 6567 cm diagonal; the 7000 cm default is sufficient. `EnemyCombatComponent.cpp:174` independently tests up to three body samples; only success updates target knowledge. `Knowledge::RetainsContact` retains 0.5 world seconds, and the policy stops movement during brief occlusion. `Fire` re-observes at birth (line 233), then `CanShoot` checks current visibility, capability, actual alignment and both muzzle corridors. Retention does not authorize obstructed fire. |
| Navigation integration note | PASS for the bounded correction. The actual home is about 4284 cm from the farthest retained floor corner; 4500 cm now contains the floor domain, with matching 5000 cm hard clamps at all three sites. The 24-world-second pursuit deadline has a documented nominal-speed rationale. The inspected extracted planner tests exercise far-room routes and their returned strips, unsupported/out-of-domain goals, work limits, retries, cancellation and reset. Heard evidence still feeds nearby protected investigation; location-wide sound pursuit or guaranteed access is not claimed. |
| Accepted launch, contact ordering and delivery | PASS. `CombatProjectileWorld.cpp:203` queues shot sound only after accepted bullet insertion. Sorted resolved contacts queue impact/direct-victim bearing before physical interruption at line 575. Delivery follows `AdvanceFrame`, with an assertion against projectile iteration in `CombatStimulusWorld.cpp:101`. Consumer delivery only records memory. Generation checks and event/shot-kind receipts reject stale or duplicate delivery; one shot and its distinct impact/damage evidence are not conflated. |
| Uncertain memory and hidden relocation | PASS for the knowledge boundary; active-decision progress fails R1. Consumer records contain values rather than actor handles. Attribution/victim handles stay in the adapter and are used only for lifecycle/filtering. Category, direct-victim, freshness, generation and uncertainty checks precede acceptance. Sound regions are quantized and damage supplies a bearing-region proposal without shooter range. Storage is four hypotheses and 64 receipt keys. Living physical interruption retains knowledge; death/reset clears it. The inspected policy has no hidden target transform getter, and paired permitted-input tests preserve identical memory/proposals. |
| World clocks and bounded work | PASS for clock/storage/work ceilings; decision completion fails R1. World occurrence/receipt and projectile simulation time remain separate, while presentation real time is not used as a reaction deadline. Current weapon/slowdown implementations remain unchanged. Queue/listener caps are 64/8; candidates cap at 53; transfers remain two per 12 world seconds. Navigation retains per-update, expansion, timeout and finite-retry limits. These bounds do not establish measured performance. |
| Diagnostic observability | PASS for the requested investigation. Schema 4 captures evidence kind/region/timestamps, knowledge revision, requested/achieved crouch, contact retention, action/assignment, scan progress, score/exposure, rejected positions, gates and query counts. `AppendSensesStatus` exposes hypotheses and bearing provenance; manager status exposes queue/delivery/drop totals. The bounded trace is not a full physics replay. |

## New review evidence and handoff

All new full evidence is in `Saved/CombatAI01/CAI-02/Review/`. `gaps-02.json`
records compilation success and **candidate acceptance failure**, with both
gaps reproduced; `gaps-run-02.log` contains the counts above. `gap-generated.cpp`
contains the exact extracted production methods, with their hashes in the JSON.
The adapters/tests/runner are included for inspection. The initial compiler
attempt is preserved as `gaps-01.json`; it only failed on double-to-float warnings
from unchanged production scanner expressions under the standalone `/W4 /WX`
configuration. Attempt 02 disables C4244 for that adapter compilation. No
production expression was changed to make the checks compile.

Reuse the passing evidence above. Correct only R1/R2 and their affected
transitions, provide a new immutable candidate, and return those findings to this
primary review. Keep Candidate01, Candidate02, their reports and this failed
review evidence unchanged. No full predecessor matrix, gameplay probe, topology,
squad, equipment or health work is requested. Controller acceptance and owner
gameplay judgement remain separate from this verdict.
