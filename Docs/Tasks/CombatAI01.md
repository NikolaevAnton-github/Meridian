# CombatAI01: surprising arcade combat AI program

Multica issue: **MSQ-101**.
Parent context: MSQ-67. Coordination only; do not assign a production executor here.

Prepared under the [owner task request](../Approvals/CombatAI01-TaskCreation01.json).
Read [current state](../ProjectState.md), the [implementation plan](CombatAI01Plan.md)
and [design](../Design/CombatAI01.md). Aim for surprising, understandable arcade
combat with persistent search, useful hearing and responses to incoming fire.

All children are prepared backlog tasks, unassigned and without runs. Core native
stages describe the sequence only; conditional future integrations are unstaged.
The controller verifies evidence and execution authorization before dispatch.
The owner retains play/visual judgement. No gameplay/editor work starts from task creation.

Deliver a persistent hunter first, then individual tactics, a coordinated small squad,
replay variety and prerequisite-driven physical/ability integrations. Profiling and
core-slice acceptance do not wait for all optional future mechanics. Existing MSQ-71/72
and MSQ-74 through MSQ-78 remain separate tasks with preserved status and scope.

Each child has its work, acceptance, prerequisite references and handoff contract in
its tracked document. Use max reasoning/standard speed, one production writer, one
primary technical reviewer and a local task-scoped closure commit. Preserve current
owner testing boundaries and source/evidence identity.

## Task index

| Package | Issue | Task | Prerequisites | Stage |
| --- | --- | --- | --- | --- |
| CAI-00 | MSQ-102 | [Baseline, contracts and observability](CombatAI01/CAI-00.md) | MSQ-70 | 1 |
| CAI-01 | MSQ-103 | [Persistent intent and running](CombatAI01/CAI-01.md) | MSQ-102 | 2 |
| CAI-02 | MSQ-104 | [Footsteps, incoming fire and evidence memory](CombatAI01/CAI-02.md) | MSQ-103 | 3 |
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
