# DemoColumnExperiment06

[Owner direction](Approvals/DemoColumnExperiment06.json): return to the previous
large-fragment column, release those pieces more easily, and carry surrounding
facing with them. Correction05 was rejected and is preserved separately. The
original checkpoint remains `6e82d7a`. This is direct work without a Multica task
or independent reviewer; owner play/design acceptance remains open.

## Behavior

Correction06 uses the same 730 original concrete fragment meshes as Correction04,
without another fracture pass. The hierarchy is flattened so one direct concrete
hit can release its actual exterior fragment. Internal pieces and every original
fragment entering the central 70 cm square stay anchored, even if they have a
small exterior patch. This protects 167 pieces, including all eight deep blocks
incorrectly classified as exterior in the first revision. The existing column
envelope, materials, reinforcement and 1,560 facing pieces are preserved.

Authoring intersects actual projected tile triangles with exterior concrete
triangles. Each tile records every fragment beneath its footprint. Releasing one
of those fragments carries the complete remaining tile with it, regardless of
the tile's previous bonded/clean category. Carried facing uses collision-free
instances bound to the moving concrete transform; it expires or remains with
that concrete piece. An already loose tile cannot be reassigned to another piece.
Independent direct tile impacts retain the earlier facing behavior.

Concrete fragments ignore other Destructible bodies, including the remainder,
and reinforcement ignores concrete debris. Floor collision remains enabled while
pieces fall. The shared budget retains up to 50 settled independent tiles or
concrete pieces; facing carried on a concrete piece is part of that same piece.
Loose concrete uses NeverSleep until the debris controller settles or expires it.
Retention requires one second of low velocity plus a static supporting surface
within 8 cm of the actual lowest convex vertex. Sleeping in mid-air is not
settlement; unsupported sleepers are woken. Tiles use their closest collision
point toward the ground for the same support check. Settled tiles stop simulation;
settled concrete becomes kinematic and NoCollision.
Excess debris expires after 12 game seconds; F6 removes all retained debris and
restores the specimen. Retained geometry still costs rendering and memory.

## Evidence

Authoring and placement: `Scripts/DemoColumnExperiment06/`.
Build, inspection, actual-rifle captures and reset evidence:
`Saved/DemoColumnExperiment06/` (generated, excluded from Git).
The owner rejected the interim result because deep blocks still ejected and
some debris remained airborne. The old normal02/stress01 probes checked only
the initially classified core and disabled simulation/collision; they did not
prove floor support and are not acceptance evidence. Their raw transforms reveal
that deep blocks 714, 715 and 728 moved despite the old zero core counter.
Saved debugger evidence
records bone 574 sleeping at Z=297.94 cm before the old retention conversion.
Interim assets and failed probes are preserved under Saved.
Corrected candidate: native build `compile07` passed. `play-stress02` repeats
90 real rifle shots over three sides. All original 20 deep blocks have zero
translation; all 167 protected fragments keep their rest transforms. The strict
shared cap reaches 50 (29 tiles, 21 concrete pieces); 19 excess concrete pieces
expire. Every retained piece has static support, no active simulation and no
collision. All 21 retained concrete pivots are below 22.57 cm; the previously
airborne bone 574 now rests at Z=8.49 cm. No attached facing overlaps a released
support. `coarse-grounded50.png` records the settled result. These checks do not
constitute a general FPS benchmark or owner visual acceptance.
`play-reset02` clears the accumulated 50 through real F6 input, restores all
1,560 facing pieces, fires two more real shots successfully, then resets again.
Both resets leave zero loose, carried or retained debris. Native build, geometry
invariance, support/collision/simulation checks and the context budget pass.
