# UtilityGOAP01 implementation plan

Date: 2026-09-24. Authority: [owner selection and clean replacement](../Approvals/UtilityGOAP01-TaskCreation01.json).
Read the [design](../Design/UtilityGOAP01.md), [source inventory](../Design/UtilityGOAP01SourceInventory.md)
and [live task mapping](UtilityGOAP01.md). This plan prepares implementation; it does
not report the new brain as delivered.

## Delivery sequence

1. **UG-00:** remove the obsolete active AI and extract verified primitives. Deliver
   an explicitly passive/manual compilable intermediate, then proceed to UG-01 as
   the next AI implementation package. Do not spend further milestones improving the
   old selectors, preserving an obsolete fallback or building a general AI framework.
2. **UG-01:** restore a useful single enemy through Utility goals, real GOAP plans,
   minimal native navigation and the new action executor. Demonstrate movement
   independent of first shot, moving fire/reload and evidence-based investigation.
3. **UG-02:** deliver real encounter navigation and persistent spatial search.
   Complete existing MSQ-71 for health/restart, UG-03 for initial individual cover,
   then MSQ-72 as a one-enemy repeatable encounter. Prioritize a bounded MSQ-74
   destruction specimen plus UG-08 before extensive tuning and group work.
   UG-04 later extends the fixture to two/three enemies behind group safety.
   This scheduling lane is explicit; missing destruction does
   not hold the initial core technically incomplete forever.
4. **UG-03..07:** weapon-aware individual tactics, safe groups, pressure/cues,
   cooperative plans, then controlled variety.
5. **UG-13/14:** measured performance/failure acceptance and a declared core slice.
   UG-08..12 integrations are independently gated by their actual mechanics.

No calendar estimates are asserted before the first replacement and measurements.
Close each bounded task with applicable evidence and a local task-ID commit. The
core has ten children (UG-00..07, UG-13/14); five integration children are unstaged.
One production writer runs at a time. Native child stages order the core; they do
not dispatch it or make conditional integrations prerequisites of every later stage.

## Shared acceptance and verification contract

- Max reasoning, standard speed; verify configured and native settings. Executor
  self-checks, one primary independent technical reviewer, controller scope/evidence
  acceptance. Previous task-specific review waivers do not carry forward.
- Read current state, the task and linked applicable decisions. Inspect actual
  prerequisite delivery evidence rather than assuming historical Multica status is
  the whole story (MSQ-70 and MSQ-121 include direct delivery).
- At dispatch declare applicable runtime verification authority. Existing owner-only
  gameplay reservations remain unless a later instruction covers the new scope.
  If runtime is owner-tested, leave runtime criteria pending and provide exact routes;
  build/source acceptance cannot silently close behavior or motion criteria.
- Preserve canonical GASPALS/CMC, finite-projectile launch safety, physical authority,
  current slowdown cadence, owner edits and original assets/evidence. No new art,
  purchases, inference APIs, duplicate project or historical evidence rebaseline.
- Test only changed behavior and related transitions. Extend existing check/trace
  tooling. Meaningful invariants and representative failure cases replace a blanket
  full feature matrix. Add performance checks only where the task changes cost.
- Handoff identifies candidate, changed files, removed code, retained primitive
  evidence, settings, build/check results, review findings, known limits and owner
  test controls. Keep generated logs under `Saved/UtilityGOAP01/<package>/<candidate>/`.
- An implementation task may have technical acceptance with explicitly pending owner
  play judgement; the family must not claim owner acceptance or untested runtime
  success. Planning creates backlog tasks unassigned and with zero runs.

## UG-00: Remove legacy AI and establish clean execution seams

**Result:** one compilable passive/manual enemy foundation, with no old autonomous
policy left in the active path. This intermediate is not a playable AI delivery.
Prerequisite evidence: current MSQ-121 direct Build07 correction, inspected by hash
and current owner edits; the cancelled preparation issue is not an execution gate.

Work: disposition every old AI symbol/call site using the source inventory. Extract
sensory validation, real launch/ammo transactions, geometry/achieved-pose checks,
generation tokens and bounded traces. Remove `AdvanceCombat`, old search/weapon
orchestration, cover/mobile/lean selectors, phase machines, duplicated knowledge,
unused timers, home-grid A* and obsolete fixture/debug consumers. Establish one new
adapter and knowledge/capability/action interfaces. Native navigation has an explicit
pending/unavailable contract, with no active local fallback. Keep original sources
through Git, not dead copies compiled into the replacement.

Acceptance: native build passes; source/call-site inventory proves no reachable old
decision path and exactly one command writer. Focused adapter checks cover passive
mode/reset generation, actual launch rejection, ammo transaction and physical
control loss. Remove obsolete tests tied to the old policy while preserving their
history; retain applicable primitive checks. Reused evidence must match current CMC.
Record any intentionally unavailable autonomy and make UG-01 the immediate successor.

## UG-01: First Utility and GOAP combat enemy

**Result:** one enemy sees/hears evidence, selects a goal, constructs an inspectable
plan and executes basic combat, reload or investigation through the new system.
Hard prerequisite: UG-00.

Work: implement authoritative known/unknown snapshots, alert/evidence age, Utility
eligibility/curves/commitment, finite GOAP search and initial actions. Add basic native
reachable-point movement and the executor with movement/weapon/posture ownership,
stable action identity, compatible progress carryover and observed effects. Declare
numeric candidate/node/depth/memory/work caps with a measured one-enemy baseline.
Separate reaction deadlines from goal/plan identity. Emit bounded causal diagnostics.

Acceptance: pure checks include a multi-step reload-then-fire plan, alternatives with
different costs, impossible/unknown goals, stale generation and search caps. Focused
scenario proves movement before first shot, moving burst/reload, loss/reacquisition
of sight, sound-region investigation and no hidden-position tracking. Replanning
during reload commits ammo once; death/reset/physical interruption rejects stale
actions. Persistent alert survives lost sight. Shot effects never assert target kill.
Gameplay remains a small one-enemy slice; advanced cover/group behavior arrives later.

## UG-02: Encounter navigation and persistent spatial search

**Result:** an alert enemy can investigate plausible regions through real encounter
topology without orbiting its spawn or knowing an unseen player's position.
Hard prerequisite: UG-01.

Work: finish native nav adapter coverage and agent sizing, route/follower ownership,
bounded async queries, partial-path policy, stuck detection, revisioned invalidation
and search coverage. Derive candidates from evidence plus reachable topology;
remember explored/blocked regions and expand or revisit after relevant changes.
Replace fixed left/right/sector loops with bounded candidates and costs. Support
safe observation when routes are unavailable, with backoff and explicit reason.

Acceptance: detour beyond the old home radius; disconnected/partial routes; blocked
door/changed collision; unreachable evidence; repeated identical sound; new evidence
during movement; negative search then fresh contact. Query pending never means
unreachable. No per-frame retry storm, spawn return or hidden-target route changes.
Fixture geometry is representative test content, not new lobby architecture.

## UG-03: Individual tactics, cover and weapon-aware plans

**Result:** a lone enemy deliberately chooses useful exposure, range, moving fire,
reload and observation while staying responsive. Hard prerequisites: UG-02, MSQ-71.

Work: pure tactical candidate queries using current CMC capsule/anatomy; Utility
curves for range, self health, ammo, evidence and travel/exposure; GOAP cover/stance,
left/right lean and low-cover actions. Rebuild coordination of movement, aim and
weapon channels. Add distinct `SuppressRegion` evidence/round/time contract for later
cooperation; direct fire cannot silently convert after losing sight.

Acceptance: rifle distance changes goal/candidate use; valid left/right lean and
low-cover stand/fire/crouch transitions; reload while moving; obstructed muzzle;
achieved-pose failure/timeout; protected lost-contact observation; owner damage/death
and restart from MSQ-71. Invalid cover/weapon state selects an alternative without
shooting through geometry or endlessly restarting aim. Unknown player health has
no score. Verify direct-fire versus bounded suppression authorization separately.

## UG-04: Safe two- and three-enemy foundation

**Result:** a small group shares only legitimate reports and does not compete for
the same place or fire through each other. Hard prerequisites: UG-03, MSQ-72.

Work: explicit membership/report model, delivery/freshness/provenance, leased roles
and destination/cover reservations; friendly corridor checks and deterministic
contention resolution. Install conservative shared attack-start/pressure permission
before enabling multi-enemy firing. Enable two enemies first, then representative
three-enemy content. Reuse MSQ-72 encounter generation and reset.

Acceptance: different private knowledge; delayed/expired reports; contested cover;
ally crossing a muzzle corridor; participant loss; partial reset and complete restart.
Release resources without conveying unseen target/death details. No independent
fixture scan populates shared enemy knowledge. Conservative group pressure, finite
bursts and helpful denied actions work before UG-05 adds richer tuning and cues.

## UG-05: Arcade pressure and truthful cues

**Result:** group combat has readable openings and initiative without relentless
simultaneous attacks or visible waiting queues. Hard prerequisite: UG-04.

Work: refine attack-start grants, bounded simultaneous pressure, release/cooldown
and attack windows. Give denied plans useful legal observation/reposition choices.
Expose truthful preparation/commit/interruption cues with existing presentation
channels; any new asset creation requires its applicable scope separately. Keep
privileged fairness information out of knowledge, aim, route and Utility snapshots.

Acceptance: correlated attack requests, exhausted/aborted grants, fast player
movement, lost contact and resets. Hidden-position variation leaves pre-gate
knowledge/targeting proposals identical; replay fairness inputs separately. No grant
bypasses actual launch/friendly safety. Owner evaluates perceived pressure, surprise
and openings in a focused repeatable encounter; record tuning rather than claiming
universal fairness from technical tests.

## UG-06: Cooperative actions and interruption

**Result:** two enemies can cover-and-move, then three can suppress and change angle
with a plan that the player can interrupt. Hard prerequisite: UG-05.

Work: explicit proposal/ready/commit/abort messages, bounded leases and timeouts,
finite support roles and confirmation of actual contribution. GOAP consumes assigned
goals through Utility eligibility; it cannot assume ally readiness or success.
Coordinate movement/cover/fire resources with the same executor and pressure gate.

Acceptance: late/unavailable supporter, failed path, lost sight, empty magazine,
friendly lane obstruction, death/reset before and after commit. Abort/reassign without
deadlock, stale leases or omniscient knowledge. Lone survivors keep effective actions.
Verify direct fire and bounded region suppression remain distinct. Test at least one
successful maneuver and its representative interruption; no full combinatorial matrix.

## UG-07: Controlled variety and observed-habit adaptation

**Result:** repeat encounters produce sensible differences with explainable causes.
Hard prerequisite: UG-06.

Work: bounded per-archetype Utility/cost curves, seeded near-equal choice variation,
recent action/route memory and limited adaptation to actually observed player habits.
Provide reset/decay and a small data-driven tuning surface. Do not add omniscient
player profiling, learning services or per-frame random goals.

Acceptance: identical permitted input/seed reproduces choices; different seeds vary
only feasible options; irrelevant hidden behavior cannot alter scores. Repeated
observed behavior changes a documented term then decays/reset clears it. Review
several short encounter replays, focusing on variety, readable commitment and no
oscillation. Owner judges whether the changes feel interesting rather than arbitrary.

## UG-08: Early destroyed-cover and route invalidation

**Result:** the new AI responds to a real bounded destructible specimen without
retaining invalid cover/routes. Hard prerequisites: UG-03, MSQ-74. Unstaged, high
priority; schedule after initial individual cover, one-enemy MSQ-72 and an MSQ-74
specimen, before extensive tuning and group work.

Work: collision/nav/cover revisions and safe invalidation, cancellation and bounded
requery through the UG-03 cover actions and UG-02 route adapter. MSQ-74 can establish
its own obstruction/cover-validity acceptance through the existing actual-geometry
guards and adapter notification seam; UG-08 extends that evidence to all affected
in-flight plans and query states. MSQ-74 completion does not depend back on UG-08.

Acceptance: cover destroyed before commitment, during movement and during a current
observation/fire action; nav update pending; debris blocks a formerly valid route.
Safe action or alternate reachable position, with no stale-cover immunity. Actual
traversal across rubble remains MSQ-95/96 and applicable MSQ-78 evidence; routing
around unsupported debris is sufficient here. Do not gate this early task on squads.

## UG-09: Time ability and knowledge integration

**Result:** the delivered MSQ-75 time ability preserves coherent plans, evidence and
action timing. Hard prerequisites: UG-01, MSQ-75. Unstaged integration.

Work: consume actual slowdown/full-stop state and confirm world-time action,
perception, query-result adoption and lease behavior. Current 0.25 world/bullet/rifle
cadence and 0.65 hero movement remain mandatory from UG-01; this task adds the full
mechanic's transitions, not permission to defer current cadence correctness.

Acceptance: enter/leave slowdown and stop during movement, burst, reload and pending
query; no stale catch-up fire, instant reload or knowledge aging through a stopped
world. Recheck group leases only if groups are delivered. No fictional new target
knowledge from the player's hidden motion while the enemy's simulation is stopped.

## UG-10: Force-push and telekinesis capability integration

**Result:** physical disruption changes available actions and cancels affected plans.
Hard prerequisites: UG-03, MSQ-76, MSQ-77. Unstaged integration.

Work: consume actual forced movement, control loss/recovery and observed thrown-object
threats. Define plan invalidation and bounded evade/recover goals only for achieved
mechanic capabilities. No telepathic anticipation or resurrection of custom deep
balance locomotion. Existing generic physical interruption works before this task.

Acceptance: push during move/fire/reload, recover/reacquire, observed thrown obstacle
and blocked route, death/reset after interruption. No firing under invalid physical
authority or duplicate ammunition/resource commits. Mechanics and physical response
quality remain the external tasks' responsibility; owner judges the combined feel.

## UG-11: Disarming and weapon capability integration

**Result:** actual weapon loss removes firing plans while preserving useful survival
and search behavior. Hard prerequisites: UG-01, MSQ-99. Unstaged integration.

Work: consume the weapon/hand capability seam, cancel fire/reload/suppression and
release applicable group roles/leases. Select safe reachable observation/movement
from legitimate evidence. Add later squad consumers only when delivered.

Acceptance: weapon loss before/during shot/reload, stale completion callback,
physical recovery, death/reset and memory continuity. No phantom rounds or firing
without a weapon. MSQ-100 is independent; pickup, secondary weapons and healing are
not part of this task.

## UG-12: Wound gestures and action ownership

**Result:** delivered wound gestures cooperate with the new action channels.
Hard prerequisites: UG-01, MSQ-100. Unstaged integration.

Work: consume real arm/hand/weapon ownership and interruptibility; reconcile gesture,
fire, reload, posture and recovery with explicit compatible/conflicting resources.
Resume from achieved capabilities and fresh aim rather than a stale old action.

Acceptance: gesture starts during fire/reload/movement, interruption and completion,
repeated callbacks, death/reset and recovery. No conflicting hand owners, duplicate
ammo transaction or memory erasure. MSQ-99 remains independent; physical gesture
quality belongs to its mechanic and owner presentation judgement.

## UG-13: Measured performance and bounded failures

**Result:** representative one-/three-enemy AI has measured cost and useful behavior
when its budgets are exhausted. Hard prerequisite: UG-07.

Work: profile Utility, grounded queries, planning, execution, perception and traces;
record CPU percentiles/worst samples, allocation/storage, replan frequency and query
bursts. Tune documented limits from the real scene. Inject bounded no-path/no-plan,
stale results, contention and repeated invalidation; stagger background work while
maintaining immediate physical safety. Reuse existing harness and earlier evidence.

Acceptance: no unbounded search/storage or retry storm; budget exhaustion has an
explicit status, safe retained action/observation and bounded retry. Compare achieved
reaction latency and player-visible stalls with documented targets. Later optional
integrations recheck only their changed costs; they do not block this core baseline.

## UG-14: Representative core slice and owner handoff

**Result:** a declared Utility+GOAP core candidate is technically reviewed and ready
for focused owner evaluation. Hard prerequisites: UG-13, MSQ-71, MSQ-72.

Work: select the exact scenario/candidate and carry applicable passing evidence;
close only changed or missing criteria. Demonstrate contact, movement, cover,
lost-contact hunt, group maneuver, interruption, pressure openings and reset on a
small representative route. Document tuning, diagnostics and known limitations.

Acceptance: one primary technical review and controller finding closure, verified
candidate identity, no live legacy decision path, runtime criteria honestly scoped,
and local task-ID closure commit. Owner separately judges movement, surprise,
difficulty and combat feel. If owner feedback is pending, report a technical handoff,
not completed owner acceptance. Optional powers/destruction are named only if their
integration tasks and applicable MSQ-78 evidence are delivered; absent features
remain future criteria. Never label the core-only slice full-program acceptance.

## Backlog replacement and external boundaries

The [task index](UtilityGOAP01.md) records actual issue IDs and a one-way successor
mapping. MSQ-105..117 are cancelled as superseded, not completed. Their zero-run
descriptions/history are preserved in the before snapshot; delivered MSQ-102..104
and MSQ-118..120 remain delivered. MSQ-101 remains a historical coordination index.

MSQ-71/72/74..78/99/100 retain their external ownership. MSQ-72 gains UG-03 as an
explicit implementation dependency and starts with one enemy within its existing
cap of three; UG-04 owns enabling group combat. All original MSQ-72 acceptance
criteria remain, including reachable cover. Other external task fields stay unchanged.
At their eventual dispatch,
read current CMC and new adapter contracts rather than applying historical Mover
or old policy instructions. MSQ-73 stays deferred. AI smoke/trap extensions wait for
actual mechanic specifications/deliveries and are not phantom prerequisites here.
No new task depends on cancelled MSQ-105..117 or the cancelled MSQ-121 preparation
issue; its direct correction evidence is linked as the baseline instead.
