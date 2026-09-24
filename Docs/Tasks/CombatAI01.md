# CombatAI01: surprising arcade combat AI program

Multica issue: **MSQ-101**.
Parent context: MSQ-67. Coordination only; do not assign a production executor here.

Prepared under the [owner task request](../Approvals/CombatAI01-TaskCreation01.json).
Read [current state](../ProjectState.md), the [implementation plan](CombatAI01Plan.md)
and [design](../Design/CombatAI01.md). Aim for surprising, understandable arcade
combat with persistent search, useful hearing and responses to incoming fire.

The original setup prepared all children as unassigned backlog tasks without runs.
The later [MSQ-102 start](../Approvals/CombatAI01-CAI00-OwnerStart01.json) authorizes
CAI-00 only, with controller-selected high reasoning and owner-only gameplay testing.
It now delivers [Candidate01/build02](../CombatAI01-CAI00Acceptance.md) with passing
build/source review; runtime criteria remain pending owner testing.
The later [MSQ-103 start](../Approvals/CombatAI01-CAI01-OwnerStart01.json) authorizes
CAI-01 through Multica at Astra/high, retaining owner-only gameplay testing.
It now delivers [Candidate01/build05](../CombatAI01-CAI01Acceptance.md) with passing
build, 35 focused checks and independent source review; runtime remains pending owner testing.
The later [owner follow-up](../Approvals/CombatAI01-CAI02-OwnerStart01.json) starts
MSQ-104 with lower-exposure positioning, quiet crouch and stronger senses after
MSQ-118 play. MSQ-105 through MSQ-117 remain undispatched. Core native
stages describe the sequence only; conditional future integrations are unstaged.
MSQ-104 now delivers [Candidate03/build01](../CombatAI01-CAI02Acceptance.md) with
passing native builds, affected checks and primary finding closure. Owner gameplay,
motion, audibility, position usefulness, difficulty and performance remain pending.
The controller verifies evidence and execution authorization before dispatch.
The owner retains play/visual judgement. No gameplay/editor work starts from task creation.

Deliver a persistent hunter first, then individual tactics, a coordinated small squad,
replay variety and prerequisite-driven physical/ability integrations. Profiling and
core-slice acceptance do not wait for all optional future mechanics. Existing MSQ-71/72
and MSQ-74 through MSQ-78 remain separate tasks, subject to the later
[owner priority decision](../Approvals/CombatPriorities01-OwnerScope01.json).
AI, shooting and environmental destruction take priority; MSQ-73 dismemberment
is deferred and cannot block this program or the initial integrated combat slice.
MSQ-74 now depends on MSQ-72 rather than MSQ-73. The implementation plan records
its recommended earlier placement; no task starts from this priority update.

Each child has its work, acceptance, prerequisite references and handoff contract in
its tracked document. Use max reasoning/standard speed, one production writer, one
primary technical reviewer and a local task-scoped closure commit. Preserve current
owner testing boundaries and source/evidence identity.

## Task index

The later [cover-fire follow-up](../Approvals/CombatAI01-CoverFire01-OwnerStart01.json)
authorizes **MSQ-119 / CAI-T02** after MSQ-104: weapon-aware ranged engagement,
left/right cover peeks, low-cover stand/burst/crouch, prompt fire and extensible
health/support inputs. This early slice preserves the unfinished full CAI-03/04/05
scope and current owner-only gameplay testing.
It now delivers [Candidate02/build01](../CombatAI01-CoverFire01Acceptance.md),
with passing build, focused checks and primary finding closure. Actual motion,
position usefulness and combat feel remain pending owner testing.

The later [owner start](../Approvals/CombatAI01-Tactical01-OwnerStart01.json)
authorizes **MSQ-118 / CAI-T01** as a bounded early single-enemy tactical slice
after MSQ-103 and before the remaining core packages. It uses existing sight/local
navigation and introduces protected lost-contact observation plus faster known
contact response. MSQ-104 now delivers the owner's sensory/tactical follow-up;
MSQ-105 through MSQ-117 retain their unfinished scope and remain undispatched.
MSQ-118 now delivers [Candidate02/build01](../CombatAI01-Tactical01Acceptance.md)
with passing build, focused evidence and the same primary review's finding closure.
Gameplay acceptance remains pending owner. MSQ-104 consumes this current policy.

| Package | Issue | Task | Prerequisites | Stage |
| --- | --- | --- | --- | --- |
| CAI-T02 | MSQ-119 | [Weapon-aware cover peeking and prompt fire](CombatAI01/CAI-T02.md) | MSQ-104 | Unstaged early slice |
| CAI-T01 | MSQ-118 | [Situational single-enemy tactics and coordinator foundation](CombatAI01/CAI-T01.md) | MSQ-103 | Unstaged early slice |
| CAI-00 | MSQ-102 | [Baseline, contracts and observability](CombatAI01/CAI-00.md) | MSQ-70 | 1 |
| CAI-01 | MSQ-103 | [Persistent intent and running](CombatAI01/CAI-01.md) | MSQ-102 | 2 |
| CAI-02 | MSQ-104 | [Footsteps, incoming fire and evidence memory](CombatAI01/CAI-02.md) | MSQ-103, MSQ-118 | 3 |
| CAI-03 | MSQ-105 | [Encounter navigation and persistent spatial search](CombatAI01/CAI-03.md) | MSQ-104 | 4 |
| CAI-04 | MSQ-106 | [Individual tactics, cover and firing rhythm](CombatAI01/CAI-04.md) | MSQ-105, MSQ-71 | 5 |
| CAI-05 | MSQ-107 | [Safe multi-enemy foundation and shared information](CombatAI01/CAI-05.md) | MSQ-106, MSQ-72 | 6 |
| CAI-06 | MSQ-108 | [Arcade pressure and player-facing cues](CombatAI01/CAI-06.md) | MSQ-107 | 7 |
| CAI-07 | MSQ-109 | [Cooperative maneuvers and interruption](CombatAI01/CAI-07.md) | MSQ-108 | 8 |
| CAI-08 | MSQ-110 | [Behavior variety and observed-habit adaptation](CombatAI01/CAI-08.md) | MSQ-109 | 9 |
| CAI-09A | MSQ-111 | [Destroyed-cover and navigation invalidation](CombatAI01/CAI-09A.md) | MSQ-109, MSQ-74 | Unstaged integration |
| CAI-09B | MSQ-112 | [Slowdown and full-stop knowledge integration](CombatAI01/CAI-09B.md) | MSQ-109, MSQ-75 | Unstaged integration |
| CAI-09C | MSQ-113 | [Force-push and telekinesis AI integration](CombatAI01/CAI-09C.md) | MSQ-109, MSQ-76, MSQ-77 | Unstaged integration |
| CAI-09D1 | MSQ-114 | [Disarming and combat capability integration](CombatAI01/CAI-09D1.md) | MSQ-109, MSQ-99 | Unstaged integration |
| CAI-09D2 | MSQ-115 | [Wound gestures and combat action ownership](CombatAI01/CAI-09D2.md) | MSQ-109, MSQ-100 | Unstaged integration |
| CAI-10 | MSQ-116 | [Measured performance and bounded failure handling](CombatAI01/CAI-10.md) | MSQ-110 | 10 |
| CAI-11 | MSQ-117 | [Representative slice and owner acceptance](CombatAI01/CAI-11.md) | MSQ-116, MSQ-71, MSQ-72 | 11 |

CAI-09D is split into D1/D2 so MSQ-99 and MSQ-100 remain independent.
Conditional integration evidence and selected-slice scope are specified in each task.

See [setup verification](../CombatAI01TaskSetup01.md) for the prepared-state snapshot.
