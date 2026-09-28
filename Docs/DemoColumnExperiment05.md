# DemoColumnExperiment05

**Rejected by the owner on 2026-09-28.** Small chips, facing left over departed
concrete and an ejected core were unacceptable. Correction04 was restored; the
replacement is [DemoColumnExperiment06](DemoColumnExperiment06.md). Correction05
assets, authoring source and Saved evidence are preserved as a rejected candidate.

Owner-authorized direct experiment, outside Multica and without independent review:
[scope](Approvals/DemoColumnExperiment05.json). The previous placed column is
preserved by checkpoint `6e82d7a`; Correction03/04 assets remain unchanged.
Owner visual/play acceptance remains open.

## Behavior

Correction05 subdivides large exterior concrete leaves using jittered 30 cm
surface sites, 6–12 cm inward. Coarser interior sites preserve deeper chunks.
It retains the existing column envelope, materials, reinforcement and 1,560
varied facing pieces. Facing supports are remapped to the new surface leaves.
The actual rigid leaves sit immediately under the root; an impact uses the
engine collision query restricted to authored rigid leaves to release its fragment, without spending shots
opening intermediate cluster levels. Collision damage and damage propagation
remain disabled for this specimen. The generic engine leaf query is unsuitable
after the first break: it can return the disabled old root. Retained/removed
leaves are excluded explicitly. A directly hit original fixed support leaf
becomes dynamic after release; untouched support stays fixed. Reinforcement
ignores concrete-debris collision, while preserving weapon/pawn queries.

A shared per-column budget retains at most 50 settled tile/concrete pieces.
The controller polls every 0.25 game seconds. A piece must stay below 5 cm/s and
0.2 rad/s for one second before retention. Tile debris stops simulating and uses
NoCollision. Concrete is changed to kinematic on its owning Chaos solver, then
gets a per-particle NoCollision profile. It remains visible with zero motion;
its inert Chaos representation remains allocated. Pending physics commands
reserve budget slots to prevent overshoot. Unretained pieces expire after
12 game seconds. Destroying/resetting the specimen removes retained debris too.

This bounds continuing physics work; retained geometry still costs rendering
and memory. Fifty pieces is an experimental limit, not an FPS guarantee for
many columns. A representative multi-column performance budget remains separate.

## Reproduction and evidence

`Scripts/DemoColumnExperiment05/author.py` builds the isolated candidate from
Correction03 concrete and Correction04 cladding. `place.py` replaces only
`EXP_DemoTiledColumn01` in `/Game/Maps/L_OpeningLobby_PainterStone01` after saving
a map backup under Saved. `play_probe.py` drives actual rifle input/projectiles;
`analyze.py` summarizes stored evidence. Generated logs and captures live under
`Saved/DemoColumnExperiment05/` and are excluded from Git.

Historical probes reached the shared limit of 50 and verified inert retained
geometry, but also exposed self-collision trapping fragments in the column.
A live Destructible-ignore probe made those same pieces reach the floor. This
does not constitute owner acceptance of the rejected geometry/design.
