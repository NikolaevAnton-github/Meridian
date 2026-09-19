# PhysicsControlVariants01 / MSQ-85

Candidate04 replaces the active legacy enemy and obstructing transient test boxes
with six numbered Physics Control mannequins. Original sources and evidence are
preserved. The owner adopted Physics Control under
[the scope decision](Approvals/PhysicsControlVariants01-OwnerScope01.json).

## Play and tuning

Use `/Game/Maps/L_OpeningLobby_PainterStone01`. Profiles 1-3 use X=-950 cm,
profiles 4-6 X=-630 cm, with Y=-320/0/320 cm, Z=8 cm and yaw 180 degrees.
All start with 100 health. Approach through the existing passages; columns block
distant views. These remain supported stationary fixtures, not balancing/AI actors.

| Input | Behavior |
| --- | --- |
| Y | Toggle normal time and 25% world/body/all-bullet time, with 65% player movement/firing. |
| F6 | Reset mannequins/feedback and restore time without refilling ammo. |
| F10 | Toggle the six-mannequin set. |
| F7 | Legacy enemy movement preview retired. |
| LMB / RMB / R | Existing fire, aim and reload. |

Normal scheduled shot spacing remains 85 ms; at 65% player speed it is about
130.77 ms in real time. Attached weapon presentation shares the player's clock;
projectiles retain their separate manager clock. Rates remain prototype defaults.

| Profile | Impulse cap (kg cm/s) | Velocity cap (cm/s) | Hit drive multiplier | Hold / recovery (world s) |
| --- | ---: | ---: | ---: | ---: |
| 1 | 1800 | 260 | .030 | .14 / .55 |
| 2 | 2300 | 300 | .015 | .22 / .65 |
| 3 | 2800 | 340 | .009 | .30 / .75 |
| 4 | 3400 | 370 | .008 | .36 / .85 |
| 5 | 4100 | 410 | .006 | .44 / 1.00 |
| 6 | 4800 | 450 | .005 | .60 / 1.20 |

The actual impulse obeys both mass-scaled velocity and impulse caps. The owner
compares and selects the desired reaction; no final profile selection is inferred.

## Narrowed acceptance

[OwnerVariantTesting01](Approvals/OwnerVariantTesting01.json) stopped excessive
per-profile tests and independent visual comparison. The controller cancelled run
`01a0baac-c474-7c85-9a36-6752710aba03` and interrupted its reviewer. Acceptance is
six mannequins and actual hits on one, using applicable existing evidence.

Candidate04's native build succeeds (`Worker/build06.log`). The reopened retained
map has clean packages. Runtime snapshots show six profiles, zero legacy enemies,
one manager and one controller. Existing rendered clips and Candidate03-Torso1
provide a representative real rifle hit: one consumed round, one physical hit,
health 100 to 75. Candidate04 changes only HUD occlusion and diagnostic joint
telemetry from Candidate03; this hit evidence remains applicable.

The controller's first new smoke view was obstructed by a column and is not hit
evidence. A further attempt refused to start because the owner had opened PIE.
That owner session remains untouched; its read-only snapshot again shows six
profiles, world scale .25 and player custom dilation about 2.6 (effective .65).
No further matrix or interruption of owner play is needed.

Existing `focused-probes02.json` passes normal/slowed/low-FPS/transition scheduler
checks with conserved ammo and residual flight. This is not a completed broad
runtime or visual review. Earlier failed/superseded metrics and unfinished review
notes remain preserved. The known MSQ-84 grounded trajectory discrepancy is not
claimed fixed. Full time ability/stop, AI and final art remain later work.

Evidence root: `Saved/CombatSlice01/PhysicsControlVariants01/`, including
`Worker/Candidate04/manifest.json`, `Worker/Candidate03-Torso1.json`, `Worker/Video/`,
`Worker/state-OwnerSmokeBefore01.json`, `Worker/sample-OwnerSession01.json` and
controller closure records. Owner configuration, descriptor and retained map
remain preserved. No new binary assets, registry replacements or purchases.
The controller closes and commits the task under the owner's narrowed acceptance.
