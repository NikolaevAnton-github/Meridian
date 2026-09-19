MSQ-69 / EnemyPrototype01 Correction01, 2026-09-19.

MSQ69-R1 is implemented and passes the executor's focused check. The same primary
reviewer still owns finding closure; controller acceptance remains pending.
This supplement leaves `EnemyPrototype01.md`, `EnemyPrototype01-Contract01.json`,
`EnemyPrototype01Evidence02.md` and all earlier candidate/evidence reports intact.

`Source/MeridianSquad/CombatProjectileWorld.cpp` now rejects invalid characters
and characters with disabled capsule query collision before testing their cached
aim spheres or changing the nearest contact. This matches the existing damage
collision gate: a lethal first hit immediately removes the corpse from aim
convergence for later births in the same processing interval. The 85 ms rifle
schedule, capsule interpolation and per-birth flight code are unchanged.

`ProbeEnemy(false, true)` adds one isolated case to the existing native enemy
probe in `EnemyPrototypeProbes.cpp`; the optional argument is declared in
`CombatProjectileWorld.h`. It uses a transient rifle component with the existing
editor timing seam and production `AdvanceFrame` / `EmitScheduledShot` paths.
A 25-health enemy is placed in front of world geometry, with two automatic births
processed in one 100 ms interval. The existing full probe is not rerun.

The Development Editor build succeeds. The corrected probe passes **12/12 checks**,
with independent recalculation from its recorded shot positions, velocities and
timestamps. The actual player rifle's state is identical before and after the
probe. Measurements from the corrected candidate:

| Observation | Result |
| --- | --- |
| First shot | Aims at the live enemy and kills it at +4.442562 ms; one hit, one death |
| Second birth | +85.000001 ms, in the same 100 ms processing interval |
| Cached frame history | All 28 enemy spheres remain; the dead query is excluded |
| Second convergence | Rear-world direction error below 1e-15; old-body direction difference 0.100554 |
| Residual flight | 14.999999 ms; surviving birth timestamp and position agree |
| Cleanup | Probe actors destroyed, bullets cleared, PIE stopped, no editor actor leaks |

The preserved negative control reproduces both finding-specific failures before
the guard: dead-target exclusion fails and the later shot still points at the
old body contact. Its additional `second_birth_history_preserved` assertion was
invalid because the production flight step consumes `BirthCapsules` after first
use. The corrected probe checks surviving birth time and residual flight instead.
This probe-only adjustment and the failed artifact are preserved explicitly;
they do not imply a production history defect.

Evidence root: `Saved/CombatSlice01/EnemyPrototype01/Worker/Correction01/`.

- `candidate-corrected01.json`: SHA-256
  `52e2d014158304be685e0287e2c341ee421f7c3e9498435598bffa4881f41fcf`.
- Loaded `Binaries/Win64/UnrealEditor-MeridianSquad.dll`: SHA-256
  `48501804cefb1f21fde4554735e477ffddf81fecaab71dd5bd28fbde388b9c84`.
- `probe-corrected01.json`: SHA-256
  `f3d75e5239a1701aa9e02cffb1f5758318c48bbe9985e1dd9f8b291fc8b13382`.
- `build-corrected01.log`, `verification01.json`, `correction01.patch`,
  `preservation01.json`, `evidence-manifest01.json` and `handoff01.json` identify
  the build, checks, exact source delta, preserved inputs and handoff.
- `candidate-regression01.json`, `probe-regression01.json` and
  `build-regression01.log` retain the negative control. Both compiled source
  snapshots and binaries are preserved in their named subdirectories.

Candidate06 idle/moving hits, rifle-pose and death evidence remains applicable:
animation, meshes, live-hit damage and physics are unchanged. Candidate08 remains
the reset evidence under the primary review's existing boundaries, including its
documented pre-recording warmup overloads. No new visual capture, animation sweep
or full timing matrix was needed. Earlier approximate sphere collision, immediate
animation transitions, rifle dressing and low-FPS recoil limits remain. Editable
source and bounded forearm adaptation feasibility retain their prior support;
detached-body production physics/materials and final enemy art remain unverified.

Owner configuration, the retained lobby, source packages, original documents and
historical evidence are unchanged. Only the three correction source files and
the compiled DLL differ among the captured baseline files. The editor is left
on `/Game/Maps/L_OpeningLobby_PainterStone01`, PIE stopped, with no dirty map or
content packages. Actual native execution is Astra/max/default with fast mode
disabled. Official Epic MCP controlled PIE; the existing Rider Python bridge
invoked the native probe and inspected dirty packages. No issue status/profile,
registry, commit or successor changes were made; those remain with the controller.
