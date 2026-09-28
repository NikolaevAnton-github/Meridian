# LobbyColumnsPerf01

[Owner scope](Approvals/LobbyColumnsPerf01-OwnerScope01.json): implement only the
first two proposed performance fixes directly, without a Multica task or an
independent reviewer. Controller self-checks cover this change. No new visual
design or owner play acceptance is implied.

## Change

- `CombatProjectileWorld::SampleBlockers` resolves NGD membership once per actor
  per sample pass. Both original sample passes, every blocker entry, transform
  comparison and live collision response remain intact.
- Pristine stationary stacking-column cladding skips its full update, including
  the all-bone transform request and tile/debris loops. A cheap post-physics tick
  compares component and root transforms and checks fracture/decay state.
  Initial setup runs fully. Movement runs fully and receives one stationary
  update to clear tile velocity before returning to idle. Any handled impact
  keeps the existing full update path active until F6; external root fracture
  also wakes it without requiring a rifle event. F6 recreates the component,
  resetting the idle state. Legacy non-stacking specimens keep their full loop.
- `GetState` exposes idle status and full/skipped update counts for verification.

This does not change projectile history architecture, threading, collision,
fragment counts, debris limits, materials or saved scene assets. Damaged columns
intentionally retain their existing update behavior, even after debris settles.

## Verification

Evidence: `Saved/LobbyColumnsPerf01/`; CSV files:
`Saved/Profiling/CSV/LobbyColumnsPerf01-*.csv`. The pre-change candidate is
`09bc649`. `compile01.json` binds the build to source and DLL hashes.

- Development Editor build passed; a fresh editor loaded the resulting DLL.
- All 16 lobby columns perform two initial full updates, then skip the tile loop.
  Their full-update counts remain at two across the idle capture.
- Moving an untouched column 50 cm and returning it increases its full-update
  count from 2 to 4 to 6; it returns to idle after each move.
- External Chaos strain, without `HandleImpact`, breaks the root and wakes full
  updates: 447 released surface bones, zero rifle tile/concrete impacts. F6
  restores all 16 columns to 768 facing pieces and idle state.
- The existing real-rifle fixture fires 10 shots at Z=22 and 810 cm. Both heights
  lose facing and release concrete; damaged updates remain active. Sampled core
  movement, unsupported wall facing, debris inside the core and retained bodies
  resuming simulation remain zero; retention stays within 80. F6 again restores
  the column and idle behavior. `Scripts/LobbyColumnsPerf01/analyze.py` passes.
- PIE stopped; original editor camera and background throttle restored. No dirty
  maps/content packages remain. Pre-existing owner worktree edits are excluded.

Each performance capture contains 400 frames at the original spawn view
(-2850, -105, 90.15), with zero rotation, VSync off and no FPS cap. The summary
excludes capture boundaries. Median times in milliseconds:

| Condition | Frame | Game thread | Render thread | GPU |
| --- | ---: | ---: | ---: | ---: |
| Before changes | 17.087 | 17.089 | 9.601 | 4.990 |
| Fixed, initial idle | 9.983 | 9.992 | 9.178 | 5.088 |
| Fixed, after rifle/F6 | 9.779 | 8.559 | 9.774 | 5.053 |

This view improves from approximately 59 to 100-102 FPS. The final capture is
primarily limited by render-thread time. These are bounded PIE idle measurements,
not a guarantee of 120 FPS or a simultaneous whole-lobby destruction benchmark.
The owner's exact earlier 40-50 FPS viewpoint/state was not reconstructed.
