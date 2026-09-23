# MSQ-104 / CAI-02: sensory evidence and protected movement

Date: 2026-09-24. **Candidate01/build04 is ready for primary technical review.**
Native Development Editor build, affected production pure/method tests, supporting
source checks and read-only editor loading/wiring checks pass. Gameplay, actual
audibility, movement, position usefulness, difficulty and performance remain
**PENDING OWNER**. No agent Play, simulation, firing probe, screenshot or performance
run was performed. The controller dispatches the independent reviewer and owns
acceptance, issue administration, ordinary editor reopening and the closure commit.

Authority: [CAI-02 task](Tasks/CombatAI01/CAI-02.md) and
[owner follow-up](Approvals/CombatAI01-CAI02-OwnerStart01.json). This adds hearing and
the bounded tactical correction to MSQ-118; it does not deliver full CAI-03/04,
groups, suppression, near misses, equipment or player health.

## Candidate and preservation

Baseline Git revision: `c4da5eaaf5793556c3a0884a10ad975573d6a0e0`.
Evidence root: `Saved/CombatAI01/CAI-02/Worker/Candidate01/`.
The immutable `candidate-manifest.json` identifies sources, scripts, this handoff,
the DLL/modules and frozen evidence. `CAI02-Candidate01-frozen.zip` retains their
exact bytes; `CAI02-Candidate01-evidence.zip` is the smaller review attachment.
`freeze-result.json` records archive and manifest fingerprints.

DLL SHA256: `43eb050518c048591803159eece4530b3a3eb35d2049ef0e0862df920b0dfb0a`.
The final loaded module identity is recorded in `FinalReload/editor-load-check.json`.
The diagnostic editor was closed after verification. The controller will reopen
the ordinary retained lobby after review; no worker-owned editor remains running.

Owner configuration, project and map match the untouched controller preservation
manifest. No binary assets, animation graphs, content sources or geometry changed.
No asset registration is required for this source-only change. The original
controller manifest and 146 earlier worker/review evidence files remain preserved.
Multica appended its managed runtime block to AGENTS.md at startup; the executor
did not edit instructions or controller-owned task/state/approval documents.
`execution-settings.json` verifies configured and actual Astra/max/default with
fast mode disabled, without freezing mutable controller monitors.

## Delivered behavior and contracts

`CombatAISenses.h` supplies immutable consumer stimulus records and four bounded
hypotheses per listener. Records contain event/generation identity, kind, category,
observer, permitted target identity, region/bearing, confidence, localization
uncertainty, world occurrence/receipt and a separate projectile simulation timestamp.
The projectile-world adapter alone holds weak attribution/victim handles. Hearing
never assigns the sight target handle or gives knowledge a live source getter.

Sight and sound use the same knowledge acceptance path. Freshness, reset generation,
duplicate event IDs, shot/kind/listener receipts and uncertain sound identity are
checked before memory changes. A repeated shot/contact with a different transport
event ID is also rejected within the 64-receipt deduplication window.
Nearby events of a kind merge; a recent shot/hit masks weak steps for 0.35 world
seconds. Fresh evidence directs attention and protected investigation through the
active policy. Current sight takes precedence; reload deadlines retain ownership.
Quiet relocation supplies no position, velocity or aim update. Confidence ages while
the original region remains fixed. These regions describe localization, not a
claim about reachable rooms or a reconstructed hidden trajectory.

Accepted `LaunchTimed` births queue one shot event after bullet insertion. Resolved
contacts queue impact and, for an eligible actual victim, incoming-bearing evidence
before physical `ReceiveBullet`. Damage, sorted contacts and reset cancellation keep
their existing authority. The queue drains after the complete projectile frame,
outside collision iteration. Living recovery retains knowledge; dead/disabled
listeners reject delivery. Reset clears pending events and motion accumulators.
Shot and contact simulation times are carried separately: world occurrence means
the world frame in which the producer ran, and is not a conversion of contact time.
Real impact-presentation timestamps never set AI deadlines.

Incoming damage supplies an incoming direction and a broad investigation region
five meters along that direction with 6.5 m uncertainty. This is a declared search
proposal, not a measured shooter range. Other listeners receive only attenuated
impact noise. Friendly steps/shots are filtered; unfamiliar eligible impacts can be
investigated without identifying a player. Queue capacity is 64, delivery is bounded
to eight existing listeners, and overflow is counted. The delivered encounter still
uses one opponent.

The acoustic model is distance plus one static Visibility obstruction trace, with
obstruction reducing range to 55 percent and widening error. Quantized regions retain
at least 1.4 m localization error; source handles never refine them. This is an open
lobby approximation, not doorway propagation or physically accurate acoustics.
The installed UE 5.8.3 `AISense_Hearing.h` was inspected as an optional adapter;
its instigator/location event transport does not supply this project's uncertainty,
clock and generation contracts. No second AI Perception hearing route was enabled.

## Movement audio and stance

The read-only audit found player `AnimNotify_PlaySound` footstep cues in locomotion
clips and the jump montage, plus GASP foley notifies routed through
`AC_FoleyEvents.PlayFoleyEvent` to `SpawnSoundAttached`. Clip time alone cannot
establish actual grounded progress for the first-person arms or blocked movement.
One grounded-distance producer now supplies player step/landing audio and gameplay
hearing. It also supplies enemy step presentation from actual Mover motion/stance.

`UCombatLocomotionAnimInstance::HandleNotify` consumes the audited old player foot
cue notifies and GASP walk/run/crouch/scuff notifies in a combat world. Both existing
native animation hosts inherit it. The saved player and GASP AnimBP generated classes
were loaded and their native ancestry confirmed through Epic MCP, without resaving
assets. Original GASP jump/landing/physical foley remains on its existing route;
the new enemy producer deliberately emits no second landing sound.

Actual feet displacement pays a stride. Ground state, actual crouch, generation,
physical authority, stationary/blocked motion, flight and discontinuities gate it.
One established flight-to-ground transition emits a player landing; no animation
landing notify emits a second copy. Audio is a separate consumer after the gameplay
event: audio mute, voice virtualization or a missing voice cannot turn off hearing.
The existing purchased footstep cue is reused for the distance-based presentation.

Protected search movement and observation request actual GASP crouch through the
existing CharacterMover bridge. Navigation requests walking while crouched. Actual
achieved crouch, rather than the request boolean, controls quiet step presentation.
Visible engagement retains standing and the existing pursuit gait policy.

## Sight and position selection

Read-only geometry identifies the retained floor as 6080 x 2480 cm, approximately
6567 cm diagonally. Sight defaults to 7000 cm. Camera, upper torso and lower torso
are tested independently with a maximum of three visibility samples. Only a successful
sample refreshes sight position/aim. Contact is retained for 0.5 world seconds with
a modest acquisition-cone allowance; movement stops during an obstructed brief loss.
The actual `Fire` method still re-observes at birth, and the unchanged `CanShoot`
requires current visibility, readiness, aim alignment and both muzzle corridors.
Remembered contact never authorizes a blocked shot.

Position safety combines five plausible firing approaches around permitted evidence
with eight local open sectors. Safety cannot be offset by rear-column protection,
view or escape rewards. Selection first finds the safest eligible exposure, then
chooses the shortest checked route among choices within 0.04 exposure of it.
Normal switching rejects an exposure increase above 0.025. Useful moves from 35 cm
are eligible; commitment, finite transfers and spatial failure history remain.

Scanner-hit static column bounds supply opposite-side and corner candidates, beyond
the original front-face points. A bounded four-corner ring tests short supported
capsule strips, at most 13 distinct strips per route attempt and 1200 cm total travel.
The checked winner route is executed directly. No hidden pawn location is queried
and no full topology system is introduced. Candidate count is capped at 53; one
surface or assessment is processed per 0.025 world seconds, with a four-second scan
deadline. Facing is relative to each candidate's evidence direction.

Arrival uses actual feet within 25 cm, freshly validated support, clearance and
facing, and at most 0.06 added exposure over the selected position. Held geometry is
rechecked. Route and observation state are canceled by physical authority; replanning
starts from recovered feet. Sensory retargeting preserves the transfer budget and
failure history rather than granting unlimited retries.

## Tuning

| Parameter | Candidate value |
| --- | --- |
| Sight / brief contact | 7000 cm / 0.5 world seconds |
| Base sight half-angle / brief retention allowance | 100 degrees / +20 degrees |
| Walk / run / crouch stride | 150 / 175 / 115 cm |
| Walk / run / crouch step hearing range | 900 / 2000 / 180 cm |
| Walk / run / crouch step audio multiplier | 0.45 / 0.85 / 0.06 |
| Player landing range / crouched range | 1500 / 750 cm |
| Player landing audio / crouched audio | 0.7 / 0.22 |
| Flight needed for landing recognition | At least 0.12 world seconds and 12 cm displacement |
| Rifle noise / impact noise range | 7000 / 1800 cm |
| Occluded range multiplier | 0.55 |
| Sound localization error | 140-650 cm, widened by occlusion |
| Maximum step delivery age / other sound age | 1.2 / 3 world seconds |
| Sensory retarget debounce | 0.25 world seconds |
| Hypotheses / duplicate receipt keys / queued events / listeners | 4 / 64 / 64 / 8 |
| Tactical candidates / transfer budget | 53 / two per 12 world seconds |

Damage, magazine, rifle cadence, aim settling, finite-projectile behavior and the
slowdown values remain unchanged: world/bullets/rifle 0.25, hero movement 0.65.
All new cognition, retention and response timing uses world time.

## Verification and review boundary

Final native build: `build04.log`, **PASS**, 25 actions, 35.66 seconds total on
UE 5.8.3 and installed MSVC 14.44, two parallel compiler actions. `build01.log`
preserves the initial compiler failures; their corrections include pointer/boolean
types and heap ownership of the enlarged bounded trace ring. `build02.log` also
passes; build03 includes the player animation-host connection and high-rate motion
gating correction. Build04 adds the explicit shot/contact receipt deduplication.
No new compiler warnings occur in the final build; retained
StructUtils deprecation notices remain.

`checks-check04.json`: **PASS**, 66 production-header assertions, 22 assertions
against verbatim extracted production consumer/intent/search/Fire methods, and
source/preservation checks. The adapters are deterministic native C++ fixtures,
not Unreal gameplay. Earlier failed attempts remain named evidence. The tests
caught stale dominant-evidence regression and include a slow crouch stride at
144 updates per second. `editor-asset_wiring.json` verifies saved-class ancestry;
it is reused after the receipt-only change. `FinalReload/editor-after.json`,
`FinalReload/editor-load-check.json` and `FinalReload/editor-closed.json` verify
the final loaded DLL identity, retained clean map, no PIE and diagnostic shutdown.

| Affected criterion | Applicable evidence | Runtime status |
| --- | --- | --- |
| S02 hidden relocation | Immutable values, paired consumer histories, no hidden getters, stable old region | PENDING OWNER |
| S03 footsteps | Actual-distance producer tests: walk/run/crouch, stationary, obstruction, flight, landing, reset, high update rate; audited notify interception | PENDING OWNER |
| S04 incoming fire | Contact-before-physics source order, bearing-only consumer, recovery retention fixture | PENDING OWNER |
| S05 occluded sound/fire | Distance/obstruction fixtures, current Fire launch veto, accepted-birth and ordered-contact source checks | PENDING OWNER; near miss remains later scope |
| S06 physical handover | Living memory retained; physical bridge source unchanged; consumer recovery transition | PENDING OWNER |
| S10 lifecycle | Generation/stale/duplicate/dead rejection, bounded hypotheses/queue, reset motion cleanup | PENDING OWNER |
| S11 slowdown | Separate world and simulation fields; unchanged time implementation and Fire deadlines | PENDING OWNER |
| Owner tactical follow-up | Competing exposure/cover/nearest tests, short column route, strict actual-feet arrival, crouch/audio wiring, body visibility selector | PENDING OWNER |

Applicable earlier MSQ-118 evidence is retained for unaffected weapon deadlines,
channel filtering, physical ownership and action semantics. The final `Fire` and
`CanShoot` production bodies match the baseline exactly; source checks also compare
the rifle, time-preview, GASP physics/input, player movement and damage receiver
implementations. This is executor self-check evidence. **Primary independent review
is pending controller dispatch to MeridianSquad Code.** No independent findings or
controller acceptance are claimed in this handoff.

## Changed files

New native files: `CombatAISenses.h`, `CombatStimulusWorld.cpp`,
`CombatLocomotionAnimInstance.h/.cpp`, `EnemyCombatSenses.cpp`.
Changed native files: `CombatAIObservation.h`, `CombatAITactics.h`,
`CombatProjectileWorld.h/.cpp`, `EnemyCombatComponent.h/.cpp`,
`EnemyCombatPolicy.cpp`, `EnemyCombatNavigation.cpp`, `EnemyCombatTactics.cpp`,
`EnemyCombatObservation.cpp`, `GASPALSRifleAnimInstance.h`,
`PurchasedArmsAnimInstance.h`, all under `Source/MeridianSquad/`.
Task scripts/tests are in `Scripts/CombatAI01/CAI02/`; this handoff is the only
executor-authored project document. Binary assets are unchanged.

## Owner route and known limits

On the retained lobby, default one-enemy mode: establish sight, cross a column
briefly, then hide. Walk, run, stop against geometry, jump and land behind cover.
Fire from a new angle, relocate quietly/crouched and watch the old sound region.
Observe nearby protected-side selection and quiet crouched observation. Reappear
from another angle, hit the enemy to interrupt it, repeat an affected transition
with **Y** slowdown, then **F6** to reset. Judge actual sound, crouch motion, position
usefulness, persistence and whether deception/slowdown creates an understandable
escape. These are requested observations, not results already demonstrated.

`msq.EnemyCombat status` includes hypotheses and tactical state;
`msq.EnemyCombat trace` exports the bounded capture under
`Saved/CombatAI01/CAI-02/Traces/`. `msq.EnemySenses.Debug 1` draws permitted uncertainty
regions and incoming bearings; set it to `0` to disable. Manager status exposes
delivery/drop counts. Existing `one`, `fixtures`, `pause`, `resume`, `reset` and
`seed` commands retain their meaning. F6 retains player ammunition.

The existing one-floor navigation and 28 m home radius remain; sight range does not
promise pursuit across every point of the 60.8 m floor. Column routes are local
static-bounds previews, with conservative clearance, not Recast topology or support
for changed/destructible rooms. The additional bounded traces are unprofiled under
the owner's testing reservation. Fixed-stride audio is grounded motion presentation,
not foot-bone contact synchronization. GASP landing/physical foley retains its
existing path. Acoustic materials, portals, near-miss suppression and propagated
sound remain future work. Owner gameplay and combat-feel acceptance is still open.
