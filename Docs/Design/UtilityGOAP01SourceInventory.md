# UtilityGOAP01 source inventory

Date: 2026-09-24. Source baseline: `7ba267f`.

This inventory supports the [UtilityGOAP01 design](UtilityGOAP01.md). It records
what can survive the replacement of the current enemy decision architecture,
what needs a new interface or owner, and what leaves the active implementation.
It is a planning artifact: no production code is changed by this document.
Source line references below identify the inspected baseline and may move during
implementation.

The owner's direction is to remove the AI that needs rebuilding at the start of
implementation and retain only justified parts. Previous suggestions to wrap the
entire cover controller or retain a selectable legacy AI fallback are superseded.
Retaining a gameplay capability does not require retaining its old controller.

## 1. Cutover contract

1. **UG-00 removes the active legacy decision path.** Extract the primitives named
   below, remove obsolete autonomous controllers and their private state, and
   leave a compilable passive/manual enemy intermediate if the replacement brain
   is not yet ready. The intermediate must identify its passive status honestly;
   it is not a completed combat delivery.
2. **UG-01 immediately follows with the first minimal Utility + GOAP enemy.** It
   supplies the new knowledge snapshot, goal selection, bounded plan construction
   and action execution needed for one playable opponent. It uses only the
   spatial domain actually supported at that stage; it does not restore the old
   custom local navigator to make the first slice work.
3. The active enemy has one decision owner and one command application path.
   There is no dual controller, selectable legacy policy, hidden legacy fallback
   or second movement follower. The current GASPALS fixture already applies
   commands after advancing combat; retain that ownership order through the new
   interface. See [GASPALSLocomotionFixture.cpp, baseline line 325](../../Source/MeridianSquad/GASPALSLocomotionFixture.cpp#L325).
4. Preserve original assets, character sources, owner edits, accepted baseline
   evidence and historical candidates. Preserve replaced code in Git history;
   do not keep obsolete AI reachable from the active game merely for rollback.
5. Planning and backlog preparation do not claim that this cutover has run.

## 2. Retain narrowly defined primitives

These are candidates for extraction or reuse under new contracts. This is not
blanket acceptance of their containing files or unchanged integration.

| ID | Primitive to retain | Existing source and boundary |
| --- | --- | --- |
| R01 | Canonical GASPALS/CharacterMovement locomotion and source gait/pose execution; localized hit reactions, source recovery/get-up and death | [GASPALSLocomotionFixture.cpp](../../Source/MeridianSquad/GASPALSLocomotionFixture.cpp), [GASPALSLocomotionPhysics.cpp](../../Source/MeridianSquad/GASPALSLocomotionPhysics.cpp). Preserve the actual character and physical authority adapters. Replace the old combat invocation interface as required; do not reintroduce custom balance or the retired active Mover path. |
| R02 | Immutable stimulus records, provenance, uncertainty, world timestamps, generation/freshness validation and duplicate rejection | [CombatAISenses.h, line 22](../../Source/MeridianSquad/CombatAISenses.h#L22). Keep the distinction between attribution handles and knowledge accessible to AI. Bounded storage and reset semantics are useful; hypothesis selection and the planner-facing representation are rebuilt separately. |
| R03 | Actual visibility sampling and sensory event production | [TryObservePlayer, line 181](../../Source/MeridianSquad/EnemyCombatComponent.cpp#L181) and [ReceiveStimulus, line 15](../../Source/MeridianSquad/EnemyCombatSenses.cpp#L15). Preserve range/FOV/occlusion tests and the rule that only successful samples publish a seen position. Extract these from contact gates, intent changes and legacy state writes. |
| R04 | Actual firing eligibility: physical authority, held weapon, achieved stance/motion/pose, barrel alignment and clear muzzle corridor | [CanShoot, line 229](../../Source/MeridianSquad/EnemyCombatComponent.cpp#L229), [MuzzleCorridorBlocked, line 254](../../Source/MeridianSquad/EnemyCombatComponent.cpp#L254), [CombatAIMobile.h](../../Source/MeridianSquad/CombatAIMobile.h). Preserve the checks and their measured character/weapon assumptions. Inputs become explicit; old cover-state dependencies do not survive. |
| R05 | The finite-projectile launch path, ammunition decrement after successful launch, actual damage/death outcomes and world-time cadence | [Fire launch/commit, line 310](../../Source/MeridianSquad/EnemyCombatComponent.cpp#L310) and [CombatProjectileWorld.cpp](../../Source/MeridianSquad/CombatProjectileWorld.cpp). Extract the verified mechanics. Do not retain the whole `Fire` function: it currently reads legacy action, assignment and cover phases. A planned shot is not a confirmed hit or kill. |
| R06 | Measured CMC capsule/stance sizing, source cover anatomy, and achieved lean/body/barrel geometry checks | [PoseCapsuleSize, line 66](../../Source/MeridianSquad/EnemyCombatCover.cpp#L66), [CoverAnatomyAt, line 158](../../Source/MeridianSquad/EnemyCombatCover.cpp#L158), [EnemyCombatLean.cpp](../../Source/MeridianSquad/EnemyCombatLean.cpp), [GASPALSLocomotionCover.cpp](../../Source/MeridianSquad/GASPALSLocomotionCover.cpp). Extract explicit geometry queries. Do not carry their implicit `CoverPlan`, threat, phase or assignment ownership into the new service. |
| R07 | Generation/action-token validity and idempotent terminal outcome semantics | [ActionRuntime, line 28](../../Source/MeridianSquad/CombatAIAction.h#L28). These small lifecycle rules can support new action contracts. The existing two runtime fields and action-kind enumeration are not a complete new scheduler or GOAP domain. |
| R08 | Bounded trace storage, generation rejection and stable per-agent seeds | [TraceRing, line 106](../../Source/MeridianSquad/CombatAIObservation.h#L106), [ResetCombat, line 118](../../Source/MeridianSquad/EnemyCombatComponent.cpp#L118). Reuse storage/identity primitives while replacing legacy payload fields with observed facts, goal scores, plan revisions, action outcomes and rejection reasons. |

Weapon profile values, actual self-health and explicitly supplied target-health
evidence may feed new capability records. Their presence does not justify keeping
the current range policy or treating unknown target health as known.

## 3. Rebuild interfaces, ownership and decisions

| ID | Rebuild | Required boundary |
| --- | --- | --- |
| B01 | A single authoritative evidence snapshot | Consolidate the duplicated `EncounterMemory`, `Knowledge`, last-known positions and intent bookkeeping. Preserve useful stimulus storage/validation, but reconsider `Knowledge::Dominant` and contact retention as explicit policy. Unknown, inferred and confirmed facts remain distinguishable. The planner receives no hidden live target transform. |
| B02 | Utility goals and candidate evaluation | Replace the hard `SelectObjective`, `SelectRangeIntent`, fixed priority branches and unexamined score constants. Geometry services return measured features and validity; Utility evaluates goals/options with inspectable terms, commitments and switching margins. Existing scores are reference material, not automatically accepted new policy. |
| B03 | GOAP domain and bounded planner | Define grounded action preconditions, predicted effects, costs, failure reasons and bounded search. Predicted state remains private to planning. Only execution evidence updates confirmed arrival, stance, reload, inspected coverage, damage or death. Limit grounding, depth, expansions, time and outstanding work; reject stale revisions/generations. |
| B04 | Action/resource ownership and cancellation | Replace `ClearIntent`, `ChangeState`, `EnsureAction` orchestration and the special cases spread across callers. Keep compatible movement with firing/reloading through explicit resource claims. Replanning retains valid running actions, paid reaction/aim delays and an in-progress reload; reset/death/authority loss still revoke the appropriate ownership. Ammo transfer commits once. |
| B05 | Weapon and cover action executors | Recreate aim/burst/reload, protected movement, torso lean and low-cover stand/fire/crouch behavior through new action contracts and actual completion checks. Low-level execution may use internal phases, but the old cover FSM is not retained as a black-box policy. No action independently chooses the enemy's next tactical objective. |
| B06 | Navigation, spatial search and tactical queries | Replace the custom home-grid planner, its coupled follower, fixed scan loops and bespoke obstacle-detour policy. Use one new navigation adapter with explicit pending/complete/partial/invalid/unreachable outcomes, request identity and geometry revisions. Partial paths do not prove arrival. One executor follows paths through the existing CMC command adapter, retaining applicable local collision/support checks. |
| B07 | Squad membership, reports and resources | Replace the global fixture scan in `RefreshTacticalContext` before real squad behavior. Authoritative membership/resource cleanup and an individual's knowledge of an unseen ally casualty are different inputs. Reports, capabilities, reservations and cooperative action acknowledgements need explicit contracts. |
| B08 | Reset, observability and compatibility seams | Reconnect encounter reset, status commands, sensory callbacks and fixture lifecycle to the new owners. Rebuild snapshot/export mappings that currently encode legacy states. Preserve current evidence separately; do not relabel old passing captures as proof of the replacement. |

Concrete coupling examples:

- [ObservePlayer, line 162](../../Source/MeridianSquad/EnemyCombatComponent.cpp#L162)
  both samples sight and changes reaction/contact gates.
- [ApplyEvidenceIntent, line 28](../../Source/MeridianSquad/EnemyCombatSenses.cpp#L28)
  turns sensory updates into search, assignment and aim changes.
- [ChooseCover, line 272](../../Source/MeridianSquad/EnemyCombatCover.cpp#L272)
  selects a winner, clears intent, assigns an objective, installs a route and
  changes execution phase. These become separate responsibilities.
- [ClearIntent, line 70](../../Source/MeridianSquad/EnemyCombatComponent.cpp#L70)
  already contains a reload-preservation exception. Preserve the behavior through
  explicit ownership rather than copying the exception into every new action.
- [Fire, line 286](../../Source/MeridianSquad/EnemyCombatComponent.cpp#L286)
  combines actual launch safety with old cover/assignment authorization. Its
  mechanics survive; its policy coupling is removed.

## 4. Remove from the active implementation in UG-00

The removal boundary is by responsibility, not by deleting every byte in a file
that also contains a retained primitive. Extract justified primitives first, then
remove the obsolete controllers, invocation paths and now-unused private data.

| Active legacy area | Remove or replace |
| --- | --- |
| [EnemyCombatPolicy.cpp](../../Source/MeridianSquad/EnemyCombatPolicy.cpp) | `AdvanceCombat` tactical branching; `BeginSearch`, `FailTactic`, and the current weapon/reload orchestration. Retain required mechanics only through the extracted interfaces above. |
| [EnemyCombatCover.cpp](../../Source/MeridianSquad/EnemyCombatCover.cpp) | `AdvanceCoverScan`, `ChooseCover`, `SetCoverPhase`, `StartCoverMove`, `ReturnToCover`, `FailCoverReturn`, `AdvanceCover`, and coupled cover assignments/timers. |
| [EnemyCombatLean.cpp](../../Source/MeridianSquad/EnemyCombatLean.cpp) | `AdvanceLeanCover` policy/phase orchestration and its legacy ownership. Extract the justified pose and geometry checks before removal. |
| [EnemyCombatMobile.cpp](../../Source/MeridianSquad/EnemyCombatMobile.cpp) | `AdvanceMobile` and its fixed strafe/approach/cooldown policy. Preserve supported concurrent motion through the new executor. |
| [EnemyCombatTactics.cpp](../../Source/MeridianSquad/EnemyCombatTactics.cpp) | Existing scan/selection/holding/search controller, fixed candidate cycling, direct assignment/path/pose commits and bespoke obstacle-detour selection. Extract useful measured geometry separately. |
| [EnemyCombatNavigation.cpp](../../Source/MeridianSquad/EnemyCombatNavigation.cpp) | Custom home-grid `PlanPath`/`ContinuePath`, their open/node/cell state, radius/layer policy and coupled `FollowPath` orchestration. Do not keep a selectable old navigator. |
| [EnemyCombatComponent.h](../../Source/MeridianSquad/EnemyCombatComponent.h), [CombatAITactics.h](../../Source/MeridianSquad/CombatAITactics.h), [CombatAICover.h](../../Source/MeridianSquad/CombatAICover.h), [CombatAIMobile.h](../../Source/MeridianSquad/CombatAIMobile.h) | Obsolete combat/cover/mobile/tactical FSM fields and branches, old assignment/transfer/candidate state, hard objective/range selection and duplicate timing/intent owners. Retained data types or validators must have a named new consumer. |

Historical source assets, accepted character content, source animation graphs,
projectile physics and preserved candidate evidence are outside this removal.
The passive/manual intermediate must still preserve valid damage/death/reset and
manual fixture behavior supported by the retained foundation.

## 5. Evidence and acceptance for reuse

The latest applicable baseline is the direct GASPALS correction documented in
[GASPALSAIFix01](../GASPALSAIFix01.md), with finding closure in the
[primary review](../GASPALSAIFix01Review.md). Its focused evidence covers movement
before the first shot, moving fire/reload, actual muzzle alignment, localized hit
drives, source cover anatomy and reset. The preceding
[GASPALS migration acceptance](../GASPALSLocomotion01Acceptance.md) supplies the
source/asset context. The preserved
[failed audit](../GASPALSAIAudit01.md) explains the integration regressions that
the correction closed; it remains historical evidence.

Reuse acceptance requires both applicable latest CMC evidence and a focused
check of the affected new integration. A passing primitive or source build does
not automatically pass its extracted interface, the new executor, or gameplay
quality. Earlier Mover candidates do not prove current CMC behavior.

At minimum, the affected integration evidence must establish:

- one active decision owner and one movement command writer;
- no policy side effects during sensory ingestion and no hidden-state leakage;
- concurrent supported movement/fire/reload, with no deadline or ammo-commit
  restart caused merely by replanning;
- predicted effects separated from actual outcomes, including partial navigation,
  refused stance/lean, interrupted reload and rejected projectile launch;
- stale generation/revision rejection, bounded failure recovery and clean reset;
- preserved actual pose/muzzle/geometry safety after extraction.

Use focused checks for changed behavior and its transitions. Retain historical
evidence unchanged and record which exact assertions remain applicable. Owner
judgement of motion, combat feel, surprise and readability remains distinct from
technical acceptance. UG-00's passive state cannot satisfy UG-01's playable-enemy
acceptance.
