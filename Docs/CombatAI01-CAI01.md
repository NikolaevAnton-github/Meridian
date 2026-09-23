# MSQ-103 / CAI-01: persistent intent and running

Executor handoff, 2026-09-23. **Candidate01/build05** implements the bounded package.
Native Development Editor build and **35 focused source/pure checks PASS**.
Independent primary source review is **PENDING CONTROLLER DISPATCH**; gameplay,
motion and performance are **PENDING OWNER**. No agent PIE, firing probe, gameplay
automation, screenshot or performance run was performed.

## Identity and scope

Incoming HEAD: `b0e599d5f39023fa5c04d5e6b222b3415655621e` (delivered MSQ-102).
Engine: UE 5.8.3-58210709, Win64 Development Editor. Evidence root throughout this
report: `Saved/CombatAI01/CAI-01/Worker/Candidate01/`.
The immutable `candidate-manifest.json` identifies delivered source, scripts, this
report, DLL/modules and focused evidence. Final DLL SHA256:
`33557055caf7012005c525eef0482ed0cd22e82e99c16e67e8502bafe65455ae`.

Configured and actual execution are Astra/high, default service tier, fast mode
disabled, matching controller evidence in `../Controller/agent-configured.json`,
`native-process.json` and `native-turn-contexts.json` relative to the package root.
The executor did not delegate, commit, alter profiles, administer issue status,
dispatch successors or edit controller-owned approvals/task/state documents.
Controller retains acceptance, independent review and the local closure commit.

## Behavior and contracts

Confirmed sight latches `EncounterMemory.Alert` separately from observation
availability/time and the current action. Neither the old four-second sight limit
nor the twelve-second pursuit deadline clears contact. Death, reset, explicit
pause/resume and stop are declared lifecycle boundaries that clear it. Living
physical recovery retains the last observed positions, time and alert.

Perception remains at .12 world seconds and runs before tactical suppression and
reload handling. Failed movement and failed weapon actions have separate five-second
destination backoffs. The failed destination neighborhood is 160 cm; newly observed
destinations outside it are eligible immediately. A route failure does not suppress
an in-range weapon action. Search-point failures use a separate backoff, so they
cannot overwrite the failed pursuit destination's deadline. No cooldown disables sight.

The preliminary search cycles through nine proposals: last-seen ground, four points
360 cm around that anchor, then four nearby points 240 cm from actual feet. Proposals
are collision-validated by the existing bounded local planner; a proposed point is
not asserted reachable until planning succeeds. Reached points produce a two-second
outward observation dwell, at a point 400 cm ahead in the selected sector. Failed
points advance after .8 seconds; completing the cycle adds five seconds of observation
before retrying. New sight can interrupt search. If no proposal is reachable, the
enemy stays alert, observes candidate sectors and retries with bounded work.
This does not establish visible-area coverage, alternate room exits or a flank.

Move, aim, burst, reload and observe use one mutually exclusive action slot. Each has
an encounter generation, monotonically increasing per-executor ID, start/update
world times and a running/succeeded/canceled/failed outcome with typed reason.
Paths retain their request token across incremental planning and following. Obsolete
goals cancel the old path before replacement work. Stale path updates, launches and
reload completions cannot use a replaced/canceled request. Reload ammo commits only
after its original request successfully finishes, once. No asynchronous callback
queue is introduced; these guards cover the existing incremental/timed commands.

Physics/death cancel action, path/frontier, burst and movement commands before
ordinary decisions. Recovery restarts search from actual feet and reacquires sight;
it does not move the pawn back to its prior point. Reset invalidates action IDs even
if invoked twice within one encounter generation and clears path/reload tokens.
Already launched bullets retain the existing projectile lifecycle; cancellation
prevents new launches, not retroactive removal of legitimate bullets in flight.

Walking is selected for the last 250 cm before destination acceptance and for a
turn whose direction dot product is below .8. Clear pursuit/search transit requests
running. The retained return-purpose mapping is walking; the old automatic
return/amnesia behavior has no policy entry. Mover remains the only movement writer.
The setter still normalizes direction; direction magnitude is not used as speed.
Aim stops movement, waits .65 seconds by default and retains the unchanged animation,
movement-alpha, alignment and swept muzzle-corridor gates. Every bullet birth still
rechecks direct sight. This is a source contract, not demonstrated braking quality.

## Imported GASP mapping

`gait-mapping.json` records the actual imported `SandboxCharacter_Mover.Get_Gait`
entry branch: `CommandedWalk` true returns `NewEnumerator0`; false returns
`NewEnumerator1`. `ProduceInput` writes that result into the custom Mover input gait.
`gait-movement-mode.json` records `BP_MovementMode_Walking.GenerateWalkMove`:
the gait selector maps 0 to `WalkSpeed=165`, 1 to `RunSpeed=375`, and 2 to sprint
585 cm/s. Walking/running accelerations are 500/800; stopping deceleration is 1000.
These are imported defaults, not measured runtime speeds. No gait bridge correction
or asset edit was needed. The inspected Blueprint bytes match prerequisite LFS hashes.

## Changed files and retained tuning

- `Source/MeridianSquad/CombatAIAction.h`: pure memory, action, backoff, search-cycle
  and gait contracts shared by production and focused tests.
- `EnemyCombatPolicy.cpp`: persistent policy, local search, recovery and action wiring.
- `EnemyCombatComponent.h/.cpp`: action lifecycle, memory separation, guarded fire,
  reset/stop and search tuning; explicit trace export now uses `CAI-01/Traces/`.
- `EnemyCombatNavigation.cpp`: request guards and purpose-based walk/run submission.
- `CombatAIObservation.h`, `EnemyCombatObservation.cpp`: schema 2 alert/action/gait,
  deadlines, search anchor/look and destination capture in the existing 64-entry ring.
- `Scripts/CombatAI01/CAI01/`: focused C++/source checks, read-only gait inspection,
  guarded editor lifecycle and immutable evidence packaging. This report is the only
  executor-owned project documentation change. No content/source assets changed.

`SearchSeconds` now means observation dwell (default 2, effective .5-5 seconds),
not evidence expiry. New `SearchRadius` defaults to 360 cm (clamped 200-650).
`PursuitSeconds=12` bounds an action before alternatives/backoff; `ReturnSeconds`
remains a legacy unused reflected field for compatibility. Other retained values:
2400 cm sight, 100-degree half-angle, 1000 cm attack range, .65 s acquire/aim,
12-round magazine, three-round bursts, .18 s cadence, 1.1 s pause and 2.6 s reload.
Unlimited reserve and Ready reload presentation remain. World/bullets/rifle cadence
0.25 and hero movement 0.65 during slowdown are unchanged.

## Verification and bounded corrections

| Criterion | Result and evidence |
| --- | --- |
| Native build | PASS `build05.log`, four actions, 4.65 s; no compile errors |
| Focused source and pure contracts | PASS all 35 checks in `self-check.json`; production-header test compiles `/W4 /WX`, `pure-test-build.log`, `pure-test.log` |
| Persistent alert/backoff contracts | PASS pure 10,000 bounded failed-action/search transitions, separated cooldowns and observation refresh; source verifies absence of timed memory erasure |
| Authority/reset/stale requests | PASS pure all five action kinds across cancellation/replacement/generation changes, same-generation reset and one-shot reload completion; source verifies live wiring |
| Gait mapping and asset preservation | PASS imported graph/default audit and prerequisite LFS matches in `gait-asset-preservation.json` |
| Owner config/project/map | PASS exact controller hashes in `preservation-after.json` |
| S01, 60-world-second hidden interval | PENDING OWNER: actual persistent hunt and useful observation behavior |
| S06 physical handover | PENDING OWNER: displaced feet, recovery movement, braking and no new invalid shots |
| S07 failed route | PENDING OWNER: actual alternative reachability/fallback and bounded behavior |
| S10 reset/death lifecycle | PENDING OWNER: live actor counts, cancellation and absence of ghost actions |
| Motion/readability/combat feel/performance | PENDING OWNER; no runtime claim |

Build01 compiled but failed to link because the editor still held the DLL. The
initial close guard correctly refused a package dirtied by read-only movement-graph
inspection. The task-created in-memory dirty state was discarded without saving,
after confirming it was the only dirty package and PIE remained off. Build02 linked;
build03/04/05 incorporated subsequent scoped source corrections. Evidence preserves
the initial failure and `editor-close-inspection-only.json`.
One initial pure-test assertion expected the preceding death outcome after a later
successful reload; its expectation was corrected, and the failure log retained.
Source self-checks also corrected search/pursuit backoff separation, outward dwell
aim, reset metadata and in-range aiming after a failed closing route before freezing
Candidate01. No independent review is claimed.

The ordinary retained-lobby editor is reopened for owner Play with final DLL;
`editor-launch.json` records its PID/log, `editor-after.json` records project/map,
PIE/dirty state and `editor-load-check.json` confirms the loaded module. The editor
is an owner handoff session, not a pending task process. Close it normally when done;
there is no supervisor guarantee. Historical manifests/evidence remain unchanged.

## Owner controls and focused route

Play the retained lobby in default one-opponent mode. Provoke pursuit over a clear
distance, hide behind existing cover for **60 world seconds**, relocate, then inflict
a nonlethal physical hit and observe recovery/re-entry. Try an obstructed route and
F6 during movement or reload. Judge visible running, braking, persistence and whether
fallback observation is useful. Slowdown stretches the real duration of world seconds.

F6/`msq.EnemyCombat reset` resets the current mode; `one` selects the opponent,
`fixtures` restores three passive profiles, `pause`/`resume` are explicit memory-clearing
lifecycle controls. `status` exposes current alert/evidence/action/request IDs, and
`trace` explicitly exports a bounded tail under `Saved/CombatAI01/CAI-01/Traces/`.
`tune search N` adjusts dwell; the other existing tuning commands remain.

Limits: one floor layer, home-centered 2800 cm local radius, 80 cm cells, 1200 path
expansions, 16 nodes/frame, a 1.5 ms boundary between nodes, five-world-second planner
timeout and 1.8-second stuck check. A node may exceed the CPU boundary; no measured
cost is claimed. No Recast, topology, hearing, incoming-fire sensing, squad work,
moving fire, art changes or successor package is included.
