# Animation and physical authority source map

Active enemy locomotion uses canonical GASPALS/CharacterMovement and complete
source Masculine/Rifle graphs. [Migration task](../Tasks/GASPALSLocomotion01.md)
and [current correction](../GASPALSAIFix01.md) identify scope and evidence.

| Responsibility | Entry |
| --- | --- |
| Combat shell, source pawn and pose API | [GASPALSLocomotionFixture.h](../../Source/MeridianSquad/GASPALSLocomotionFixture.h) |
| Commands, post-source tick, aim/lean and lifecycle | [GASPALSLocomotionFixture.cpp](../../Source/MeridianSquad/GASPALSLocomotionFixture.cpp) |
| Local physical hits and source ragdoll/get-up | [GASPALSLocomotionPhysics.cpp](../../Source/MeridianSquad/GASPALSLocomotionPhysics.cpp) |
| Stance anatomy and cover proposals | [GASPALSLocomotionCover.cpp](../../Source/MeridianSquad/GASPALSLocomotionCover.cpp) |
| Player purchased arms presentation | [PurchasedArmsAnimInstance.h](../../Source/MeridianSquad/PurchasedArmsAnimInstance.h) |

Contracts: retain source directional gait and aim movement. The combat shell never
reintroduces custom balance holding or recovery steps into the active enemy.
Respect physical authority transitions, evaluated pose/tick order and real muzzle
alignment. Reset/end-play must clear transient drives/caches. Preserve original
source graphs/assets and owner edits; technical checks do not grant motion acceptance.

Verification routes: [migration correction check](../../Scripts/GASPALSLocomotion01/Correction01/check.py)
for its affected C++ seams; [graph check](../../Scripts/GASPALSLocomotion01/graph_check.py)
for source wiring; [current correction analysis](../../Scripts/CombatAI01/GASPALSFix01/analyze.py)
for actual pose/launch/hit evidence. Read each script's candidate/output assumptions
before execution. Existing evidence may already cover unchanged criteria. New PIE,
renders or full animation matrices do not follow automatically from opening this map.
