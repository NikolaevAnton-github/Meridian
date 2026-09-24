# MSQ-121 / GASPALSLocomotion01 controller acceptance

2026-09-24. **Candidate02 / Correction01 is accepted within the authorized technical scope and delivered for owner testing.** Build, focused checks and the sole primary technical review pass. GL01-R1 and GL01-R2 are closed; no remaining technical finding exists in scope.

Authority: [direct owner start and gameplay direction](Approvals/GASPALSLocomotion01-OwnerStart02.json) and [bounded brief](Tasks/GASPALSLocomotion01.md). Implementation and review ran directly outside Multica. The previously prepared MSQ-121 issue remains cancelled with zero runs; its identifier labels this work and the local closure commit.

## Delivered scope and evidence applicability

The active opponent and passive fixture modes use the local canonical GASPALS CharacterMovement character with its full animation stack, explicit Masculine base and Rifle layer. Source gait, directional speed selection, acceleration, braking, rotation and aim transitions own locomotion. Source CDO function results agree with the derived pawn: forward/side/back walk 200/180/150, run 500/350/300, crouch 225/200/180, sprint 700/700/700 cm/s. AI does not request sprint. These are verified settings/function results, not measured gameplay velocities.

Custom upright balance holding and recovery stepping no longer own the active enemy. Ordinary valid skeletal hits use localized physical response while allowing combat; strong or accumulated impacts use source ragdoll/get-up, and death/corpse impacts retain physical response. Current AI, source crouch/aim, mobile fire, torso lean, reset and slowdown use the adapted source state. Player movement and the retained lobby are outside the changed scope.

The original sole primary review found two blocking migration defects: an owned CMC movement capsule could consume skeletal projectile contacts, and tactical proposed stance geometry still required Mover. Candidate02 corrects those consumers. The resumed sole primary reviewer confirms both findings closed and L01-L06 technically satisfied with retained evidence. The two corrected production files compile in the final Development Editor build. The reviewer reuses 29 routing/arbitration and 26 proposed-geometry/clearance assertions after verifying their actual production extraction and consumer wiring; no passing test or build is repeated.

Passing Candidate01 asset/Blueprint/source checks remain applicable because correction assets and animation graphs are unchanged. The primary review's full-object-path comparison establishes 1,172 retained original non-comment graph nodes plus four lean nodes; it supersedes the original executor's 1,084 display-name count. Four scoped CVar inputs preserve source defaults alongside existing owner configuration. No full feature/animation matrix was repeated.

No agent Play, firing, game-world simulation or performance probe ran. Physical feel, exact visual source equivalence, practical cover/mobile fire, get-up reliability and slowdown/reset through real contacts remain owner Play judgment. Source/code acceptance does not establish those results. Packaging/cooking and multiplayer remain out of scope.

## Identity, preservation and registration

Candidate02 manifest SHA-256: `6f793201dcb434658006c477fec6857dd0861525844b9ef3caf403455f4e6291`. DLL SHA-256: `600731ab8e22aba32834ec33bd2b26798377b69879f1de0f70d3a0f28667f3b8`. The controller identity validator matches all **2,250** current production, native input, DLL, receipt, evidence and archive records at technical acceptance; see `Saved/GASPALSLocomotion01/Controller/identity-Candidate02.json`. Candidate01 and its original rejection remain immutable. Candidate02 reuses its original asset archive plus a 1.20 MB correction archive. Project size at freeze is 56.93 GB, below the 250 GB limit.

The controller subsequently adds three exact-byte preservation rules to `.gitattributes`, documented in `Controller/closure-attributes.json`. This administrative supplement prevents checkout newline conversion in the corrected source, reports and registry manifests; it changes no built source, asset or frozen candidate. Controller approval/task/state/acceptance and reviewer outputs are separate from the frozen production inventory.

The source GASPALS project, historical assets/candidates/review evidence and initial owner configuration are preserved. The project descriptor receives only additive GASPALS enablement relative to owner bytes; final staging isolates that addition from the owner's other uncommitted edits. New binary assets use Git LFS. No historical accepted fingerprint is replaced.

`GASPALSLocomotion01-Candidate02` is registered in the separate local `meridian_assets` database: **2,099 artifacts**, zero declared dependency edges. Existing provenance is recorded in intake/revision manifests; no inferred relationship is promoted. Inspect and validate exit 0; validation reports no changed files, affected chains or stale evidence. Results are preserved under `Controller/registry-*.json`.

## Execution and handoff

Executor, correction and sole primary reviewer use Astra/max/default, fast disabled, under the existing subscription. Native turn contexts confirm model/reasoning; explicit process arguments establish default tier. Shared profiles are unchanged. The controller checked scope, identity, applicability and finding closure without a second technical review.

The controller reconfirms editor PID **14348** responding on `/Game/Maps/L_OpeningLobby_PainterStone01`, with the matching DLL, no PIE and no dirty packages. Official Epic MCP state and Windows loaded-module evidence are saved under `Worker/editor-state-controller-handoff.json` and `Controller/editor-handoff.json`. Closure/staging and the local commit are recorded in `Controller/closure-summary.json`.

Start ordinary Play for the current one-opponent mode. Inspect Masculine directional rifle movement, aim transitions, crouch/standing torso lean and physical hits through knockdown/get-up/death. Existing Y slowdown and F6 reset remain. Manual fixture controls and exact limits are in the [implementation](GASPALSLocomotion01.md); see also [correction](GASPALSLocomotion01Correction01.md), [original review](GASPALSLocomotion01Review.md) and [correction review](GASPALSLocomotion01Correction01Review.md). Final motion/play acceptance belongs to the owner.
