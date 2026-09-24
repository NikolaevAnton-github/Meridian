# Weapons and projectile source map

Use the relevant [CombatSlice01 task](../Tasks/CombatSlice01Plan.md) and
[gameplay policy](../AgentPolicies/Gameplay.md) for authority and time rules.

| Responsibility | Entry |
| --- | --- |
| Player fire/reload public API and timing seams | [CombatRifleComponent.h](../../Source/MeridianSquad/CombatRifleComponent.h), [implementation](../../Source/MeridianSquad/CombatRifleComponent.cpp) |
| Projectile interval coordination and finite flight | [CombatProjectileWorld.h](../../Source/MeridianSquad/CombatProjectileWorld.h), [implementation](../../Source/MeridianSquad/CombatProjectileWorld.cpp) |
| Enemy launch safety (`CanShoot`, `MuzzleCorridorBlocked`, `Fire`) | [EnemyCombatComponent.cpp](../../Source/MeridianSquad/EnemyCombatComponent.cpp) |
| Active enemy rifle pose | [GASPALSLocomotionFixture.cpp](../../Source/MeridianSquad/GASPALSLocomotionFixture.cpp) |
| Enemy fire/reload policy | [EnemyCombatPolicy.cpp](../../Source/MeridianSquad/EnemyCombatPolicy.cpp) |
| Player montage presentation | [PurchasedArmsAnimInstance.cpp](../../Source/MeridianSquad/PurchasedArmsAnimInstance.cpp) |

Contracts: ammunition transfer is tied to the matching reload commit; interrupted
or duplicate notifies must not grant another transfer. Projectile coordination owns
the interval after movement/camera sampling. Enemy shots use the real muzzle and
current safety checks. Player launch uses camera-relative geometry with its
obstruction/very-near view-origin fallback. Slowdown: world, bullets and rifle cadence 0.25, player
movement 0.65; full stop remains later scope. PurchasedArms06 is the presentation
baseline. Do not infer player health or new weapon mechanics from tuning inputs.

Verification: [timing review](../CombatTiming01Review.md) records applicable checks
and the retained low-FPS recoil limit. Existing timing analysis:
[analyze82.py](../../Scripts/CombatFoundation01/analyze82.py). For enemy launches
and moving reloads use [GASPALSAIFix01](../GASPALSAIFix01.md) and its existing
bounded evidence. Select changed behavior and related transitions, not every old
test case. Open [Animation](Animation.md) only for pose/montage coupling.
