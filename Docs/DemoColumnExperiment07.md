# DemoColumnExperiment07

[Owner direction](Approvals/DemoColumnExperiment07.json): refine the generally
liked Correction06 (`ee196f2`) with smaller large pieces, heavier concrete motion,
and ceramic facing that crumbles after release. Direct work; no Multica task,
agents or independent reviewer. Correction06 and earlier candidates are preserved.
Owner visual/play acceptance of this refinement remains open.

## Behavior

Correction07 splits only 144 exterior fragments with at least 4,000 square cm
of lateral surface. Each is divided into two at its area-weighted median along
the longest axis. Their median equivalent visible linear size is 70.73% of the
original, approximately the requested 30% reduction. Individual ratios range
from 62.0% to 78.5%; no uniform tiny-fragment fracture pass is applied.
There are 874 concrete leaves, including the unchanged 167 anchored core pieces.
The remaining smaller pieces retain their original geometry. Facing remains
1,560 pieces, with 4,412 complete footprint support links rebuilt for the new cuts.
The collection has 5,009,813 faces versus 4,933,268 in Correction06 (+1.55%).

The concrete launch speed is bounded to 55–115 cm/s, using a fixed impulse divided
by mass before clamping. Random lateral motion is limited to 12 cm/s and the
upward addition to 8 cm/s. Spin is 0.35–0.8 rad/s. The new physical material has
0.025 restitution (minimum combine), 0.85 friction and 0.95 static friction
(maximum combine). Existing collection mass settings are preserved. The reduction
in launch speed, spin and bounce provides the heavier behavior.

On the first sufficiently hard floor impact, up to two nearby carried facing
pieces break into five ceramic chips each. A real projectile hitting carried
facing or its released concrete breaks one nearby facing piece. The released
concrete receives no new launch impulse. Remaining facing stays on its carrier.
Temporary chips use small existing ceramic mesh variants, last four game seconds,
and have a strict 32-body limit per column; the oldest expires if the cap is full.
They collide only with static surfaces and do not enter the retained-debris budget.

The shared 50-piece retention budget and verified floor-support settlement rules
from Correction06 remain. Retained concrete is kinematic with physical collision
disabled. Correction07 retains Visibility queries on concrete and carried facing
so shots can still chip their facing; those queries do not block player movement.
The engine's built-in UI profile supplies the retained concrete query filter,
without modifying project collision configuration. Independent retained tiles
remain collision-free. Excess concrete expires after 12 game seconds. F6 clears
temporary chips, retained debris and the damaged specimen.

## Evidence

Authoring, placement and real-rifle probes: `Scripts/DemoColumnExperiment07/`.
Generated geometry inspection, sizing, captures and probe results are under
`Saved/DemoColumnExperiment07/`, excluded from Git. Native build `compile02`
passed. Geometry comparison verifies all 586 unselected pieces, including the
167 protected core pieces, unchanged. Runtime `play-normal02` fires five actual
rifle shots: the falling piece crumbles facing on landing, then a facing hit and
a subsequent hit on exposed retained concrete each create additional ceramic
chips. The latter increments the concrete-hit counter and does not relaunch it.

Final `play-stress02` fires 91 real rifle shots across three sides and retained
debris. All 45 released concrete pieces crumble facing on floor impact. The
retained budget reaches exactly 50 (23 concrete, 27 independent tiles); temporary
chips reach their independent cap of 32. Protected core displacement, unsupported
retained pieces, active retained simulation, retained physical collision and
facing left over a released support all remain zero. Visibility queries remain
enabled on retained concrete as intended. F6 is tested with 50 retained pieces
and five active ceramic chips; the fresh specimen has all 1,560 facing instances
and no loose, carried or retained debris. `final-grounded50.png` records the pile
before reset. Earlier build01 probes remain historical evidence.

The saved lobby contains 145 actors; every unrelated actor's identity, label and
transform is unchanged. The editor is left idle on the lobby with the previous
camera and background throttling restored, and no dirty packages. Owner source
and configuration edits retain their exact pre-work hashes. Context budget and
the project footprint check pass (128.08 GB before adding the new local commit).
This is a bounded functional test, not a general performance benchmark.
