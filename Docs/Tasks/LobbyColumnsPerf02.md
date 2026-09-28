# MSQ-158: LobbyColumnsPerf02

Owner authorized the five-step plan on 2026-09-28. Authority: [OwnerScope01](../Approvals/LobbyColumnsPerf02-OwnerScope01.json).

## Objective and baseline

Reduce CPU rendering and destruction work for the 16 LobbyColumns01 columns without changing appearance, shadows, collision, first-hit behavior, support rules or F6. Perf01 is committed at `83181e1`; its direct/self-review waiver does not extend here. Preserve unrelated owner edits in Config/DefaultEngine.ini, MeridianSquad.uproject and Docs/EnvironmentDestruction01ED02.md.

Existing fixed-view baseline after Perf01: median Frame 9.779 ms, GT 8.559 ms, RT 9.774 ms, GPU 5.053 ms. RT shadow wait 3.390 ms overlaps worker ShadowInitDynamic 3.911 ms; do not add them. 10,318 RHI draws include 6,841 shadow and 2,439 occlusion draws. Facing uses 2,368 components (148 per column), 12,288 instances. These are prior measurements, not the new candidate's result.

## Authorized work

1. Attribute facing, concrete and rebar shadow/visibility work in identical views, restoring temporary diagnostic toggles.
2. Pilot shared rendering for 2-4 neighboring columns. Preserve exact source meshes/materials and query collision. Validate performance, first hit, destruction, movement and F6 before extending to all 16. Spatial grouping must not worsen culling/light interactions enough to erase the benefit.
3. Measure blocker collection and comparison separately. If still material, replace permanent world scanning with supported component registration/invalidation on spawn/removal/component changes. Preserve both history sample semantics, hit ordering and reset lifetimes.
4. Optimize damaged-column updates using active parts and required support checks; settled fragments may sleep only with reliable waking for hits, moving supports, external Chaos fracture, movement and reset. Avoid floating shells, stale velocities or missed unsupported parts.
5. Compare intact hall, real rifle fire across several columns, settled debris and F6. Record mean/median/p95/p99 frame/GT/RT/GPU timings in identical settings and views. Target 120+ FPS where practical; do not claim a guaranteed FPS or optimize for GPU utilization alone.

## Candidate guidance and boundaries

Renderer-only facing pooling is the initial candidate: retain hidden non-shadow-casting per-column query ISMs and tile hit maps; use shared NoCollision visible ISMs for attached facing. Keep carried/loose/shard paths unchanged unless evidence requires a scoped change. Stable render handles and owner generations must survive swap-removal, EndPlay and F6. Synchronize world transforms even if local tile transforms are unchanged. Check materials for actor-position/bounds/random dependencies. Never merge query ownership without preserving existing NGD actor routing and already-collected hit items.

One Multica production worker owns editor writes. Baseline attribution is controller preparation; editor ownership transfers explicitly after it finishes. One fresh independent primary technical reviewer examines the final candidate and evidence. Rendering equivalence needs independent visual evidence; owner play/design acceptance remains separate. No competing writer, automatic asset saves, engine source modifications or owner config edits. Preserve evidence and rejected trials.

## Evidence and delivery

- Preparation and new evidence: `Saved/LobbyColumnsPerf02/`; raw CSVs under `Saved/Profiling/CSV/` with unique Perf02 prefixes.
- Controller startup state: `Saved/LobbyColumnsPerf02/controller-before.json`. Restore original camera/throttle and stop PIE at handoff.
- Invalid initial capture: `attribution-excluded01.json`; minimized Unreal forces 3 FPS even with background throttle false. Profile only with a visible restored editor and verify real delta. Do not overwrite this excluded evidence.
- Prior probes: `Scripts/LobbyColumnsPerf01/probe.py`, `analyze.py`; prior report `Docs/LobbyColumnsPerf01.md`.
- Build helper reference: `Saved/LobbyColumnsPerf01/build.py`. Close editor gracefully before full build, bind source/DLL hashes, relaunch and recheck live health. One heavy operation at a time.
- Worker delivers a concise report, exact evidence paths, scoped diff and self-check results; controller owns review dispatch, finding closure and final local commit. No worker commits or unrelated documentation rewrites.

## Controller attribution

`Saved/LobbyColumnsPerf02/attribution02-run.json` completed all eight stages and restored all components. Median baseline/restored Frame: 10.170/10.152 ms; RT: 10.185/10.152 ms; shadow wait: 3.902/3.919 ms. Facing shadows disabled: RT 6.477 ms, shadow wait 0.782 ms; facing hidden: RT 4.845 ms, shadow wait 0.040 ms. Concrete/rebar shadow or visibility toggles did not materially improve the baseline. Exact summaries: `attribution02-summary.json`; script: `attribution02.py`. This attributes the primary cost to facing. Disabling it is diagnostic only, not an accepted implementation. Frame plateau 8.334 ms in faster cases suggests an existing 120 FPS cap; record cap/settings explicitly for final comparisons.

Controller preparation is complete and editor ownership transfers to MSQ-158 after explicit dispatch. Live task state is in Multica.

## Technical delivery

Build05 is accepted for the authorized optimization scope. [Worker handoff](../LobbyColumnsPerf02.md) preserves the candidate report; [MSQ-159 primary review](../LobbyColumnsPerf02Review.md) passes technical and supplied-view visual equivalence with no blocking findings. Controller verification matches all 62 files in `Saved/LobbyColumnsPerf02/evidence-manifest05-aligned.json`; exact acceptance evidence is under `Saved/LobbyColumnsPerf02/Admin/`.

Shared facing retains 12,288 instances while reducing visible components from 2,368 to 888. Final mean frame time improves from 11.407 to 7.668 ms intact, 12.197 to 8.572 ms firing, and 12.640 to 8.166 ms settled. The review independently recomputed all 25,180 final frames. Firing tails still exceed the 8.333 ms budget; mass destruction, grenades and telekinesis are not validated by these captures. Post-F6 measurements cover the restored steady state, not the reset hitch.

The reviewer exercised owner deletion, a fresh PIE world, registry lifecycle, damaged-column movement, external fracture and F6; source/DLL identity and original editor state were restored and checked. No implementation correction was requested. Owner play/design acceptance remains separate. The owner's subsequent request for scalable, repeatedly interactive debris is a planning direction, not authorization to execute that new architecture. Read-only research is preserved in `Saved/LobbyColumnsPerf02/mass-destruction-research.md`; no new implementation task was dispatched.
