# EnemyCombat01: owner-test handoff

Date: 2026-09-23. Task: **MSQ-70**, CombatSlice01 stage 4.

Implemented directly outside Multica under the [owner's start and testing decision](Approvals/EnemyCombat01-OwnerStart02.json). The native Development Editor build and focused source checks pass. Gameplay, firing, movement, physical handover and visual acceptance are **pending owner testing**. No Play session, automated gameplay probe, shot, screenshot or recording was run for this task.

## Delivered implementation

Play defaults to **one profile-1 GASP opponent** at its retained fixture position, carrying the adopted M4. The original three fixture profiles, sources, tuning and positions remain available in passive mode. The logical fixture retains its one GASP pawn and one command controller; no second AI pawn/controller or Behavior Tree is introduced.

`UEnemyCombatComponent` drives the existing Mover movement command and rifle stance/aim seams. Its readable states are Idle, Acquire, Pursue, Aim, Burst, Reload, Search, Return, Blocked, Recovery and Dead; Disabled leaves the manual fixture controls available. The overhead label shows the current state and enemy magazine.

Sight checks range, facing cone and retained scene visibility collision. Only a visible player refreshes the remembered position. Losing sight immediately stops attack decisions and sends the enemy toward the last observed ground position for at most four world seconds, then home. The follow-player rifle test seam is never enabled by AI. Acquisition, pursuit, aiming, return and failed movement have bounded delays or outcomes.

Shots require Locomotion authority, a held weapon, settled rifle/aim weights, low movement speed and the actual M4 local +Y barrel within six degrees of the observed target. The eye/body-to-muzzle corridor and muzzle-to-target corridor must be clear. Visibility is checked again at the actual launch. Three failed muzzle reposition attempts, or an obstruction lasting over six seconds at those attempts, lead to return and cooldown; that budget survives Aim/Pursue state changes.

Accepted shots enter the existing `CombatProjectileWorld` finite-flight simulation. They use its cover sweeps, moving character contacts, physical body contacts, shot identity, point damage, lifetime and reset cancellation. A fixture shooter records the foundation's controller as instigator. Own physical bodies receive the same bounded launch-clearance treatment as the existing player capsule: immunity ends on clearance, and a round that never clears is retired within 200 cm. Later self contacts remain possible. Already launched rounds continue after the shooter dies; dead actors cannot launch more.

Each accepted shot also uses the existing rifle SoundCue and Niagara muzzle flash. The temporary M4 has an explicit local muzzle fallback `(0, 62, 9)` cm, matching its +Y length; a future authored `Muzzle` socket takes precedence. This prototype offset and final aim/flash readability need owner inspection. Reload uses the Ready pose and a timer, with no new reload animation or inventory system.

## Tuning and clocks

All delays use world time. Thus Y's retained 0.25 world/bullet slowdown also slows enemy thought, movement, cadence and reload, while the player's existing 0.65 movement behavior remains intact. Enemy cadence is quantized to rendered frames, with at most one accepted shot per update and no missed-frame catch-up burst.

| Setting | Default |
| --- | --- |
| Sight range / half angle / sensing interval | 2400 cm / 100 degrees / 0.12 s |
| Acquisition / initial aim | 0.65 s / 0.65 s |
| Attack range | 1000 cm; approach aims for 820 cm, chase resumes beyond 1150 cm |
| Burst / shot interval / burst pause | 3 rounds / 0.18 s / 1.1 s |
| Magazine / reload / reserve | 12 rounds / 2.6 s / unlimited reserve |
| Bullet speed / damage / cone spread | 14000 cm/s / 10 / 0.6 degrees |
| Lost-sight memory / pursuit / return bounds | 4 s / 12 s / 12 s |
| Failed route retry / stuck threshold | 2 attempts / 1.8 s without progress |
| Failed engagement cooldown | 5 s |

`FEnemyCombatTuning` exposes the remaining ranges, timings and navigation bounds. Runtime console tuning is session-local; F6 retains the component's tuning, while changing between one opponent and three fixtures creates fresh default components.

## Navigation and physical ownership

The lobby has no task-added navigation asset or map edit. A small incremental A* planner samples the current Pawn-blocking geometry, grounded capsule clearance and supported capsule-swept edges. It commands the retained Mover; it never teleports or directly places the pawn.

The default support envelope is one walkable layer within 2800 cm of home, at most 160 cm above/below its ground height, with 80 cm cells, up to 30 cm supported steps and 40-degree floor normals. This is local lobby navigation, not multi-floor navigation, jumping, crowds, dynamic-platform transport or demonstrated destruction-rubble traversal. Narrow passages can be conservatively rejected by the grid/capsule margin. Each followed edge is rechecked against current geometry.

Search work resumes across frames: at most 16 expanded nodes per update, with a 1.5 ms soft boundary between expansions, 1200 total expansions and a five-world-second timeout. A single node has at most eight bounded edges; the time boundary is not a hard real-time guarantee. Routes are not rebuilt every tick. Two failed attempts or a stuck/time limit produce a stopped return/cooldown outcome, with no task queue growth or teleport to an unreachable destination.

Any Recovery, Falling, Down, GettingUp or Dead authority clears AI movement, path, burst and reload intent before the adopted physical pipeline runs. Recovery/get-up keeps the existing physical feet, support, snapshots and 0.55-second pose handoff. After Locomotion returns, AI replans from the displaced capsule position, rechecks perception and waits for aim readiness. An interrupted reload restarts its full duration if the magazine is still empty. F6 clears projectiles and recreates the foundation/controller with fresh memory and timing. F10 and mode changes clear rounds before destroying fixtures.

MSQ-78's later rubble integration must supply representative collision/support and validate the ground/step/slope envelope, moving support, path invalidation and physical recovery handover there. This build does not establish rubble traversal acceptance.

## Damage and future seams

`AOpeningLobbyCharacter::TakeDamage` receives the established `ApplyPointDamage` call and lets the standard point/any-damage events run. It records hit count, total received damage, last amount/direction/causer and visible hit feedback. It never subtracts player health or triggers player death; those remain MSQ-71. The HUD shows `PLAYER HITS` and `DAMAGE`, briefly flashes a red hit indicator and shows the latest player hit. F6 clears these counters without changing player rifle ammunition.

The fixture exposes `GetHeldWeapon`, `IsRifleHeld`, `SetRifleHeld`, and left/right hand occupancy. The held M4 occupies the right hand; the left grip is occupied in Locomotion and released under physical authority. Setting the held-state seam false suppresses firing/weapon pose, but does not itself spawn or detach a dropped weapon. MSQ-99 owns that behavior; MSQ-100 owns wound gestures and arm-layer changes.

## Owner controls

Start Play in `/Game/Maps/L_OpeningLobby_PainterStone01`. Use the existing Tilde console for these commands, then close the console to inspect the opponent.

| Control | Result |
| --- | --- |
| **F6** or `msq.EnemyCombat reset` | Restart the current mode; clear projectiles, enemy memory/ammo/reload and player hit counters; player ammo is retained |
| `msq.EnemyCombat one` | Recreate one autonomous profile-1 opponent; default Play mode |
| `msq.EnemyCombat fixtures` | Recreate the three retained passive fixtures with original profile tuning |
| `msq.EnemyCombat pause` / `resume` | Pause AI for manual inspection / resume it in one-opponent mode |
| `msq.EnemyCombat status` | Write current state, reason, sight memory, ammo/shots, obstruction/path counters and timing to Output Log |
| `msq.EnemyCombat tune range 1200` | Change attack distance in cm |
| `msq.EnemyCombat tune sight 2400` | Change sight distance in cm |
| `msq.EnemyCombat tune aim 0.8` | Change aim delay in world seconds |
| `msq.EnemyCombat tune interval 0.25` | Change enemy shot interval |
| `msq.EnemyCombat tune pause 1.5` | Change pause between enemy bursts |
| `msq.EnemyCombat tune reload 3` | Change enemy reload duration |
| `msq.EnemyCombat tune search 4` | Change finite lost-sight memory |
| **Y** / **F10** | Existing relative slowdown / fixture enable-disable |

Existing `msq.EnemyRifle` manual pose/movement commands pause autonomous control before applying the command. F6 restores AI when the current mode is one opponent. The three-fixture mode remains passive across F6. Existing player LMB/RMB/reload, immortality and reserve controls are preserved.

For the owner's test, the affected behaviors are visible acquisition and pursuit around retained cover; stopping/aiming, bursts and reload; cover blocking shots and finite search/return; hits interrupting movement then recovery at the displaced position; death and F6 restart. The player receiver counters distinguish an actual damage event from muzzle/impact presentation. These are pending observations, not claimed results.

## Verification and evidence

Evidence root: `Saved/CombatSlice01/EnemyCombat01/`.

| Evidence | Result |
| --- | --- |
| `build03.log` | MeridianSquadEditor Win64 Development succeeds on UE 5.8.3; 9.37 s; includes the final obstruction-budget correction |
| `source-self-check.json` | Focused source scope, clean task-code whitespace check, preserved owner/map hashes, and explicit absence of gameplay testing |
| `Candidate01-identity.json` | SHA256 identities for the 14 native implementation files and resulting project DLL |
| `editor-before.json`, `editor-before-close.json`, `editor-after.json` | Official Epic MCP project/map, stopped Play and dirty-package state |
| `fresh-editor02.log`, `editor-launch.json` | Fresh editor load of the built project; no Play requested |
| `Controller/execution-settings.json` | Controller's native Astra/max execution evidence for executor and sole source reviewer |

Candidate identity manifest SHA256: `819c58d5f9faf218c6667cc22d5887ee284ae4de2343e4c88dd8aa570843438b`.
Final editor PID: **26792**, ordinary project launch, retained lobby, Play stopped and zero dirty packages. The targeted Blueprint/Class/Linker/Python/fatal load-error scan is empty in `editor-load-check.json`.

`build01.log` preserves the initial pointer-deduction/console-macro compile failure; `build02.log` preserves its passing correction before the source review finding. `fresh-editor.log` preserves an initial script-mode launch that exited normally after its bootstrap; the final session uses an ordinary editor launch. The final source review closed EC70-R1's potentially endless close-cover Aim/Pursue loop through a persistent obstruction budget. The primary independent reviewer owns the source review report; the controller owns scope/evidence acceptance and the local task closure commit.

Owner `Config/DefaultEngine.ini`, `MeridianSquad.uproject`, the retained map, character packages and historical candidate evidence are preserved. The new implementation is native code only; no content package, character source or old immutable manifest was edited. Temporary editor lifecycle tooling is under Saved and provides no gameplay-test entrypoint.

No runtime behavior, animation, motion quality, cover, damage timing, path reachability, performance, packaged build or networking acceptance is claimed from compilation/source inspection. The editor is left on the retained lobby with Play stopped for the owner's test.
