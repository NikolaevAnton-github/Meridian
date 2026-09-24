# ContextBudget02 subsystem maps: primary review slice

Scope: documentation correctness and routing for `Docs/Subsystems/{README,AI,Navigation,Weapons,Animation}.md`, against current source interfaces, ProjectState and the Gameplay policy. No implementation changes, model sessions, Unreal runs, byte-budget or link rechecks were performed. Tooling review remains separate and pending.

Verdict: two P2 documentation corrections required; no scope/authorization regression found.

## Findings

- **MAP-01 (P2), Weapons.md:10 — wrong physical launch entrypoint.** `GASPEnemyRifle.cpp` contains base `AGASPEnemyFixture` stance/aim methods plus legacy Mover-dependent implementations. The active `AGASPALSLocomotionFixture` overrides fire-motion and evaluated rifle pose in `GASPALSLocomotionFixture.cpp:290,301` (declarations in its header:54-59). Actual enemy launch authority is `EnemyCombatComponent.cpp:229-325`: `CanShoot`, `MuzzleCorridorBlocked`, then `Fire` and `World->Launch`. Route physical launch/safety there, and active presentation/pose to the GASPALS fixture. If retaining the base rifle reference, label only the inherited setters it really supplies. The current label directs weapon work toward obsolete movement/pose code and omits the real launch seam.

- **MAP-02 (P2), Weapons.md:16 — overbroad real-muzzle contract.** The statement applies to enemy shots, whose current adapter samples the rifle `Muzzle` socket (`EnemyCombatComponent.cpp:244,277`). The player implementation intentionally derives its muzzle from camera/view transform and falls back to the view origin for obstructed or very near launches (`CombatRifleComponent.cpp:284-305`). Scope the real-socket claim to enemies and briefly describe the existing player launch boundary. This is a map correction; no weapon behavior change is requested.

## Passing observations

AI and navigation maps correctly distinguish current legacy implementation from the prepared Utility+GOAP replacement and do not authorize task execution or a selectable fallback. Listed navigation functions and canonical `ApplySourceCommands` exist; source CharacterMovement owns movement. Sensory provenance/freshness and reload commit identity/deduplication contracts match their interfaces. Projectile coordination runs at `TG_PostUpdateWork` after camera/movement sampling. Animation routes match active authority/pose seams and correctly reserve owner motion acceptance. Historical verification scripts are explicitly qualified by candidate assumptions; the maps avoid making them an execution queue or recursive startup reading list.

## Reviewed documentation identities
- `Docs/Subsystems/README.md` SHA-256 `55a921f536cc64be410b1a812456ab6837207aa6a253afa2c47aef32da2f3754`
- `Docs/Subsystems/AI.md` SHA-256 `82dae7ea9538dd21502c399ad29fc19e1006f79784ff34ac4fddc49b1d54ded2`
- `Docs/Subsystems/Navigation.md` SHA-256 `2d83fee3cfdf5245cee32492ce30a91489d20a76ea0558853a981d4f87fd4a26`
- `Docs/Subsystems/Weapons.md` SHA-256 `e260ccfc54c00682f639fcb3acba57046aa75d07cdf677fd26f5d9ec4d1d2c00`
- `Docs/Subsystems/Animation.md` SHA-256 `c8b278096b1b270eec56ad9ee8a044bda3d2283df17f59a7ab6c04e1f4cffea7`

## Finding closure

MAP-01 and MAP-02 are closed. Bounded reread of the changed Weapons.md clauses confirms the enemy launch/safety route now names `EnemyCombatComponent.cpp` and its three actual methods; active pose points to `GASPALSLocomotionFixture.cpp`. The muzzle statement is explicitly enemy-specific, with the player's camera-relative and obstruction/very-near fallback described separately. This matches the previously reviewed source; no unrelated rechecks were needed.

Corrected `Docs/Subsystems/Weapons.md` SHA-256: `78c31d4931b1957ad1a42a2a0b08d99505347f533edaf913be0e3a3638637b6a`.

Final documentation-slice verdict: PASS. Core tooling review remains pending candidate delivery.