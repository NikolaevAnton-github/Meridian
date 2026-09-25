# EnvironmentDestruction01: Next Gen toolkit integration plan

Updated 2026-09-25. Coordination parent: **MSQ-74**, under MSQ-67.
Authority: [owner task rewrite](../Approvals/NextGenDestruction01-TaskRewrite01.json).
Location and first pass: [later owner lobby scope](../Approvals/NextGenDestruction01-LobbyScope01.json).
Baseline: [accepted toolkit migration](../NextGenDestruction01.md).
Multica owns live state. MSQ-149 Candidate01 / Build03 is technically complete
under its later task-scoped start and review waiver; see the
[delivery](../NextGenDestructionIntegration01NGD01.md). MSQ-150/151 remain
undispatched backlog. Owner visual/play acceptance remains separate.

## Direction and sequence

Use `/Game/NextGenDestruction` as the asset source and the existing
`/Game/Maps/L_OpeningLobby_PainterStone01` as the sole integration and handoff map.
Start by bringing a small set of ready-made demo breakable props into available
lobby space. Verify the first source with our rifle, then place the remaining props
within NGD-01; approximately three to five props is a planning default. Record
sources, materials, transforms and supported break states. Reuse vendor behavior;
derive assets only if a necessary integration change would modify a vendor source.

Capture current saved/unsaved owner state and a recoverable pre-change map snapshot
before future edits. Preserve existing architecture, lighting, materials, actors,
player start and circulation; add identifiable removable instances. An old lobby
hash is not permission to overwrite current owner work. No separate laboratory or
duplicate gameplay map is a delivery milestone. The retired copied-lobby/custom ED
implementation stays retired. This gameplay placement does not resume broader
architecture/dressing production or grant final visual acceptance.

| Package | Multica | Result | Prerequisite |
| --- | --- | --- | --- |
| NGD-01 | MSQ-149 | [Demo props placed in our lobby and working with our rifle](NextGenDestruction01/NGD-01.md) | MSQ-68, MSQ-82, accepted toolkit migration |
| NGD-02 | MSQ-150 | [Their material, debris, reset and change contract](NextGenDestruction01/NGD-02.md) | NGD-01 |
| NGD-03 | MSQ-151 | [Lobby load, slowdown and owner-ready handoff](NextGenDestruction01/NGD-03.md) | NGD-02 |

Children execute sequentially only after an explicit start, with one production
worker/editor writer. They get fresh issues/native sessions rather than resuming
retired ED candidates. The parent has no executor or automatic successor dispatch.
The accepted migration is not repeated as a new milestone.

The replacement direction is now established. The AI lane retains MSQ-123..125,
MSQ-71, MSQ-126 and one-enemy MSQ-72. MSQ-131 consumes NGD-02's tested specimen/change
contract after MSQ-126 and the one-enemy encounter, before extensive tuning/group
work; it need not wait for NGD-03's final population handoff. Neither early toolkit
integration nor MSQ-74 completion depends on new AI. NGD-01 delivery does not
dispatch the AI lane or either remaining destruction child.

## Behavior and interfaces

Use the actual rifle/projectile path and finite-projectile collision rules. The
impacting bullet stops at an intact obstacle and applies damage once; subsequent
shots can pass through an opening only when their actual sweep fits. Intact-material
penetration is outside this plan. Declare the vendor object's damage granularity,
thresholds, anchoring, impulse and supported local/whole-object break states; do not
promise arbitrary cutting or restore the old mandatory two-layer column recipe.

Visual state, blocking collision and valid cover must agree. Record substantial
remaining geometry and settled debris instead of clearing all collision to make a
shot pass. Significant fragments retain world/mutual collision and stable settling;
fine nonblocking chips may be cosmetic. Keep counts and lifecycle bounded, preserve
one reproducibly movable piece, and invalidate support before removal/reset.

Expose object/fragment identity, affected bounds, collision/cover revision, support
invalidation and reset generation through a narrow adapter. Extend only measured
vendor gaps; no replacement destruction framework or obsolete AI integration.
NGD-02 hands this contract to MSQ-131 and MSQ-96/MSQ-78. MSQ-96 can prove contacts on
independent fixtures; NGD-02 need not wait for it. Real rubble crossing is MSQ-78's
acceptance, distinct from destruction and routing around unsupported debris.

## Measurements and acceptance

NGD-01 delivers a small playable demo-prop placement and real weapon loop in the
lobby. NGD-02 proves its material, debris/reset and notification contract before
additional density tuning. NGD-03 measures the same lobby with task-added props
disabled as baseline, intact props, individual/overlapping breaks, settled
debris and repeated reset using reproducible counts, camera and shot sequences.
Record engine/hardware, resolution/scalability, frame cap, execution mode, sample
duration, frame/Game/Render/GPU and available physics timings, P95/max spikes,
active bodies and memory trends. Use existing Unreal profiling; no new benchmark
framework, unlimited stress scene or unmeasured universal fragment/FPS promise.
Tune from measured cost, retain margin for AI/abilities, and disclose visual trades.

Check canonical slowdown: world, bullets and rifle cadence 0.25; hero movement 0.65.
Check entry, restoration, lifetime/cleanup and reset while debris is active.
Do not add the later full-stop ability. NGD-03 reuses valid NGD-01/02 evidence and
rechecks only changes, concrete gaps and affected transitions.

Substantive implementation has executor self-checks and one primary independent
technical review, followed by controller scope/evidence/finding closure. Preserve
independent visual review where applicable and separate owner visual/play acceptance.
Old ED review waivers do not transfer. At each future dispatch define runtime test
authority, verify live editor/project/bridge, max reasoning and standard speed, and
prepare the bounded brief/checkpoint under the execution/context policies.
Keep generated evidence under `Saved/NextGenDestructionIntegration01/<package>/<candidate>/`;
track source/config/docs in Git and binary assets in LFS. Preserve owner changes.
Parent closure requires all three child deliveries and the existing lobby ready
to play with the identified prop set and known limits, without claiming owner
acceptance or later AI/traversal. Existing lobby walls/columns are not automatically
converted to destructible architecture by this first-pass placement.

## Retired route and preservation

MSQ-140/141 (ED-00/01) retain done status as historical technical deliveries.
MSQ-142..147 (ED-02..07) are cancelled as superseded. MSQ-148 remains cancelled.
Their [old child briefs](EnvironmentDestruction01/ED-00.md), approvals, runs,
rejected/accepted candidates and exact evidence remain history, not an execution
queue. Their starts/waivers cannot authorize NGD work. Retired implementation bytes
and hashes remain under `Saved/NextGenDestruction01/RetiredImplementation` and its
removal manifest. No historical evidence or immutable manifest is rebaselined.
