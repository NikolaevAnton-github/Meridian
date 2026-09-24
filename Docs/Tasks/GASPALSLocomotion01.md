# GASPALSLocomotion01: exact source enemy locomotion and rifle movement

Authorized 2026-09-24 by the [owner request](../Approvals/GASPALSLocomotion01-OwnerStart01.json).
Read [ProjectState](../ProjectState.md) first. Baseline is current source at
`b4ee7a2` after MSQ-120. Prepared work identifier: **MSQ-121**.
The later [direct start and gameplay direction](../Approvals/GASPALSLocomotion01-OwnerStart02.json)
authorizes implementation outside Multica. The prepared issue is cancelled with
zero runs and must not be dispatched. This document remains the implementation brief.

Delivery: **Candidate02 / Correction01**, 2026-09-24. Native build, focused checks
and the sole primary [technical review closure](../GASPALSLocomotion01Correction01Review.md)
pass. Both Candidate01 integration findings are closed. See the
[controller acceptance](../GASPALSLocomotion01Acceptance.md) for scope, identity,
asset registration and preservation. Gameplay/motion judgment remains with the owner.

## Outcome

The owner rejects the partial transfer and requests the movement of
`D:/devgames/GASPALS_UE58` with its Masculine style: forward/back/side locomotion,
rifle aim entry/exit and movement with the rifle, at source demonstration speeds.
The previous integration imported individual rifle poses onto a different GASP
Mover graph and retained custom balance recovery. That is not source parity.

Implement a faithful source-driven movement/animation stack for active enemy
fixtures. Use the canonical source pawn, animation graph, chooser/database,
overlay, rotation, gait, acceleration/braking and aim-transition settings needed
for the specified behavior. Do not approximate source behavior by adding more
isolated poses to the old graph or tuning a single speed. Inspect whether source
uses CharacterMovement or Mover; confirmed direction is the source CharacterMovement stack.
Choose source Masculine style explicitly. Source animations and transition logic
must actually be selected by production commands in every requested direction.

Remove our custom upright balance holding, procedural recovery stepping and
recovery authority from the active enemy movement path. Preserve historical
implementations/assets/evidence. Damage, normal hit reactions, death and corpse
impacts must remain functional through the retained source physical facilities or
a bounded Physics Control adapter that does not reintroduce custom balance ownership.
The owner prioritizes dynamic shooting and enjoyable physical reactions. Ordinary
hits should permit continued combat, with localized physical response; strong hits,
knockdown/death and corpse impulses must retain physical consequences. Deep physical
balance is not a central mechanic and must not return through a renamed controller. Native
source ragdoll/get-up behavior may replace the custom balance path as needed.
Preserve combat AI, tactical commands, finite rifle fire, sight/muzzle safety,
lean when compatible, crouch and reset/slowdown integration. Source movement
speeds supersede the enemy 360 cm/s override; player movement is out of scope.

## Acceptance and focused evidence

One primary independent technical reviewer owns L01-L06. The executor implements
and self-checks. Controller accepts scope, evidence applicability and finding closure.

- L01: Identify the exact local source classes/packages/settings for Masculine,
  forward/back/side movement, starts/stops/turns, rifle Relax/Ready/Aim transitions
  and armed/aimed movement. Supply a compact source-to-destination parity table
  and real exported graph/default/asset evidence, including justified adaptations.
- L02: The active enemy uses that stack and source speed selection, including
  stance/gait/directional/aim effects, acceleration/braking and rotation. Show
  actual producer/consumer wiring; no residual 360 override or substitute rifle
  blend masks controlling the requested behavior. No guessed speed values.
- L03: Custom balance holding and stepping are absent from active enemy ownership
  and hit handling. Damage/death/ragdoll/get-up/reset paths remain coherent;
  archived sources and candidate evidence remain unchanged.
- L04: Existing AI movement/aim/crouch, finite-projectile launch/muzzle/pose gates,
  mobile fire and relevant lean/physical interruptions use actual achieved source
  state. Any source limitation or unavoidable conflict is explicit. Preserve
  unrelated tactics and owner player/config/map edits.
- L05: The migration is self-contained in MeridianSquad with no runtime source
  project mount requirement. Preserve exact pre-edit binary bytes and source
  provenance. Track assets in LFS and prepare a new revision registration manifest
  for controller acceptance without changing historical accepted fingerprints.
- L06: Native Development Editor build and focused source/asset/Blueprint compile
  checks pass. Use actual production data/wiring or meaningful native checks,
  not only string-presence assertions. Do not run full animation/feature matrices.
  Source parity is technical; visual motion/gameplay acceptance remains owner-only.

Carry forward the owner's testing boundary: no agent gameplay, PIE, firing,
gameplay simulation or performance probes. Read-only editor/asset inspection and
asset authoring/compile checks are allowed. Preserve active owner Play and unsaved
assets. Before mutations verify project/map/PIE/dirty state using official Epic
MCP. Guard build/reload and leave the ordinary retained lobby editor with the
matching DLL ready for owner Play. If a new owner Play starts, do not terminate it.

## Execution and delivery

Direct execution outside Multica, Astra/max/default with fast disabled; verify actual native
settings. One editor writer and one heavy build/editor process at a time. Inspect
capacity before any large copying; avoid duplicate project/worktree or unrestricted
cache growth. Existing source project is read-only. Owner changes initially are
`Config/DefaultEngine.ini` and `MeridianSquad.uproject`; capture exact current bytes
and preserve them. If new plugin enablement is necessary, preserve these edits and
make only the required additive change with an explicit diff and before archive.

Read only relevant prior handoffs: `Docs/GASPALSEnemy01.md`,
`Docs/GASPEnemyFoundation01Handoff.md`, `Docs/CombatAI01-CombatSpeed01.md` and
`Docs/CombatAI01-MobileLean01.md`. Reuse existing import/graph tooling where useful.
A concurrent read-only source audit may appear under
`Saved/GASPALSLocomotion01/SourceAudit/`; treat it as advisory, not acceptance.
Initial source audit identifies `/GASPALS/Blueprints/CBP_SandboxCharacter` and
`ABP_SandboxCharacter` with CharacterMovement, plus Masculine overlay assets under
`/GASPALS/OverlaySystem/Overlays/Bases/Masculine/`. The source demo appears to use
the playable pawn, not a separate enemy; use its equivalent locomotion states as
the enemy animation/speed reference and confirm this from actual source data.

Deliver `Docs/GASPALSLocomotion01.md`, reproducible bounded scripts and immutable
candidate identity/evidence under `Saved/GASPALSLocomotion01/Worker/Candidate01/`.
Use new candidate paths for corrections. Provide changed-file list, source parity
table, build/check outputs and limits. Preserve source material under
`Assets/Source/GASPALSLocomotion01/` as needed. No commits, registry mutation,
issue/profile administration, additional dispatch or new purchases by the worker.
Controller owns final review, registry acceptance, closure and local commit.
