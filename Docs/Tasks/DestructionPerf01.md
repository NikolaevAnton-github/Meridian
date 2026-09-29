# DestructionPerf01: fixed lobby blast and performance baseline

2026-09-29. Direct work under [the owner request](../Approvals/DestructionPerf01-OwnerScope01.json).
The fixture and measurement work are implemented. The [optimization plan](DestructionPerf01Plan.md)
is proposed future work; destruction behavior has not been optimized in this task.

## Use

Start Play in the retained lobby. A stationary sphere appears between the central
columns at **(-550, 0, 40) cm**. **F7** starts the existing NGD grenade's two-second
world-time fuse; the blast radius remains **400 cm**. Holding F7 produces one blast.
**F6** cancels a pending fuse, restores the breakables and rearms the charge.
The fixture rejects arming during slowdown. Ordinary G throws remain available.

The fixture is created only at runtime in this lobby. No saved map placement,
vendor asset, fracture settings or owner geometry was changed. It adds an F7 HUD hint.
The charge uses the real vendor grenade, including its explosion effects, sound
and fields. Runtime F6 also clears its queued fields through the existing reset path.

A native recorder retains pre-blast frame history and records 15 real seconds from
the actual field spawn. CSV and metadata JSON are written after measurement to
`Saved/DestructionPerf01/Captures/`, with unique filenames. Reset or PIE exit during
recording saves an explicitly aborted capture. No per-frame file I/O or Python
callbacks are used in the performance runs. The screenshot is taken after capture.

## Controlled measurements

Machine: Ryzen 7 9800X3D, GeForce RTX 5090, approximately 32 GB system RAM.
UE 5.8 Development Editor executable in standalone `-game` mode; DX12,
1920x1080, 100% screen percentage, VSync off, uncapped FPS. Existing quality
settings are retained and recorded. Camera: (-550,-600,172) cm, pitch -2, yaw 90.
The automated camera's movement is disabled; manual Play keeps normal movement.
Five normal runs and two diagnostic runs are in `Saved/DestructionPerf01/final-analysis.json`.

The primary three-run sequence is `measured01`: one initial blast, then two F6
resets with 12 seconds of settling/warmup before each repeat. `measured02` adds
one initial and one warm run with explicit Insights region tracing.

| Phase | First blast, primary run | Warm repeats, primary runs |
| --- | ---: | ---: |
| Intact, -5 to -0.1 s | 160.5 FPS | 160.7 FPS |
| First second after field spawn | 15.2 FPS | 23.0-24.2 FPS |
| Active destruction, 1-5 s | 40.1 FPS | 38.1-38.8 FPS |
| Settling/recovery, 5-15 s | 137.9 FPS | 135.3-139.8 FPS |
| Worst frame within first second | 196.27 ms | 156.97-159.99 ms |
| Frame p95 during 1-5 s | 35.51 ms | 35.19-35.27 ms |

FPS is frames divided by their total elapsed frame time, not an average of
instantaneous FPS. A 196 ms frame is a hitch, not a sustained 5 FPS result.
Across all five normal runs, first-second warm FPS is 23.0-24.2, and 1-5 s FPS
is 38.1-42.2. The original symptom is reproduced under the defined workload.

During 1-5 s the primary runs average **25.07-26.27 ms Game**, **7.18-7.68 ms
Render**, and **7.29-7.59 ms GPU**. These delayed engine counters overlap and
must not be added. They indicate a CPU-side limit; they do not identify the
entire cost as Blueprint execution or as the physics solver.

The scene contains 26 managed breakables. Ten central pillars receive substantial
damage. Secondary impacts occasionally break another pillar/glass, so final
broken-prop counts range from 10 to 12. Normal captures record **3,659-3,953 break
notifications**. These are events, not a measured active rigid-body count. Chaos
and vendor random impulses produce variable outcomes; this is a fixed workload,
not bit-identical simulation.

## Isolation and trace evidence

`noniagara02` sets the installed engine's `fx.NiagaraComponentsEnabled=false`.
The warm run still gives **23.0 FPS** during 0-1 s and **38.3 FPS** during 1-5 s;
Game time remains **26.20 ms** in the latter interval. GPU time falls to **6.74 ms**.
It has 3,878 break events and 12 broken props versus 3,899/12 in `measured02` warm.
Disabling Niagara activation alone does not remove the sustained bottleneck.
This global diagnostic still permits asset loading/component setup and is not
a complete removal of every effect-related cost or an acceptable visual candidate.

The warm 15-second `measured02` Insights region contains:

- **638,381** vendor Blueprint collision-delegate calls: 1.010644 s inclusive.
- **509,731** `SetPerParticleCollisionProfileName` calls: 0.299982 s exclusive.
- **3,899** break-delegate calls: 0.257383 s inclusive across all threads.
- GameThread `WaitForTasks`: **5.151226 s** exclusive, maximum single wait
  **117.376 ms**; `ProcessUntilTasksComplete`: **11.356955 s** inclusive.

These totals are across a 15-second region and nested/parallel work must not be
summed. The collision/profile repetition is directly observed and worth reducing;
it does not by itself explain all the lost frame time. Substantial worker work is
under generic task scopes, so detailed solver/contact/body attribution remains a
next-step measurement. Cold runs also show first-use Niagara compilation; warmed
runs retain large hitches, so preloading alone cannot solve the problem.

The warm **first five seconds** narrow this to **452,570 collision callbacks**,
**357,503 profile changes** (about 1,975 per engine frame), and **2.096303 s** of
GameThread task waits. Profile changes take 0.256371 s exclusive; callback
inclusive time is 0.668394 s. This is measurable avoidable-work potential, not a
claim that removing callbacks will recover the full frame budget.

UE 5.8's timer exporter includes GPU timelines even when `-threads=GameThread` is
selected. Accordingly `game-*.csv` contains GameThread CPU **plus GPU** timings;
only unambiguous CPU scopes above are attributed to GameThread. All durations in
Insights `Incl`/`Excl` columns are seconds.

## Evidence and reproduction

- `Saved/DestructionPerf01/final-analysis.json`: all seven valid capture summaries,
  embedded metadata and raw-input hashes.
- `Saved/DestructionPerf01/Captures/`: original CSV/JSON pairs and post-capture PNGs.
- `Saved/DestructionPerf01/measured01.utrace`, `measured02.utrace`,
  `noniagara02.utrace`: native traces. Region exports use `measured02` onward.
- `Saved/DestructionPerf01/measured02-insights01/`: successful timer exports,
  counter/thread inventories, response file and tool logs.
- `Saved/DestructionPerf01/measured02-first5-insights01/`: exact first-five-second
  timer exports; `measured02-insights01/hotspots-final.json` is the verified summary.
- `Saved/DestructionPerf01/noniagara02-insights01/`: the matching diagnostic trace
  exports; its warm interval still contains 622,837 collision callbacks and
  497,876 profile changes.
- `Scripts/DestructionPerf01/run.ps1`: isolated run launcher; requires the editor
  closed. Example: `-Name fresh-name -Trace -Repeats 3`. `-NoNiagara` and `-NoSound`
  are diagnostic options; no-sound has not been tested in this task.
- `Scripts/DestructionPerf01/analyze.py`: bounded offline CSV analysis; requires
  a fresh `--output` under Saved. Unreal's bundled Python can run it.
- `Scripts/DestructionPerf01/export_trace.ps1`: offline headless Insights exports;
  `-ExpectedRepeats` validates all repeated region files. Native trace channels
  must include `region`. Use a fresh output directory.

Rejected pilot records are preserved and excluded from the final analysis:
`baseline01/02` used a falling camera outside the lobby; `fixed01/02` froze that
outside-wall camera; `noniagara01` used an unavailable CVar and was not a valid
Niagara isolation. `measured01-insights01` failed because its source trace omitted
the region channel; its raw frame captures remain valid. None of these records
was overwritten or silently reclassified as successful evidence.

## Validation and limits

Build08 passed the focused Development Editor build. The analyzer's synthetic
metric/boundary tests passed. Native measurements verify an unchanged fixed blast
position/radius, correct frame timing origin and repeated F6 restoration.
Real-key PIE checks and final preservation results are recorded in the delivery
section below. Owner gameplay/visual acceptance remains separate.

The first real-key check exposed an existing grenade recognition guard at low
editor frame rates: the vendor Delay emitted the field at actor age 1.726504 s,
below the fixed 1.9 s recognition threshold. Native probe evidence is in
`editor-probe.log`; `lowfps-probe.log` separately records standalone 3 FPS with
age 2.000001 s. Recognition now allows the current simulation step when testing
the age. It does not alter the fuse, force or radius. The temporary field probe
was removed. The earlier `input-smoke.json` failure remains preserved.

Rider's native debugger attach succeeded but source breakpoints could not resolve
to executable lines and the sampled frame had no source stack. That route was
stopped after two unsuccessful breakpoint attempts; agent breakpoints were removed
and user breakpoint settings were unchanged. Native targeted logging supplied the
missing runtime values before the fix. No debugger was attached during benchmarks.

This is a local Development baseline with CPU/GPU tracing, fixed view and no active
combat encounter. It is not a packaged shipping benchmark, a target minimum-PC
guarantee, an exact reproduction of the owner's original camera/settings, or a
complete Chaos solver profile. A no-trace control and production stress matrix
remain part of the proposed optimization work. Existing GASPALS reset warnings
are preserved in logs and were not changed by this task.

## Delivery checks

- `Saved/DestructionPerf01/input-smoke02.json`: real-key PIE check passed, including
  a cancelled fuse, five-second F7 hold producing exactly one recognized blast,
  completed capture, no remaining grenades, and all 26 breakables restored by F6.
  This is functional evidence under background editor throttling, not FPS evidence.
- `preservation-final.json`: all 155 editor actor records are unchanged; owner map,
  grenade asset and DefaultEngine.ini hashes match the initial snapshot. No dirty
  content/map packages remain. The editor is open on the retained lobby, outside PIE.
- `context-budget-final.log`: context validation passed, 7,894 combined startup bytes.
- Final DLL SHA-256:
  `9fb7d9b6acc66284ec8733d81dfa782de725ab1058c9cfcfafa11d248e554b35`.
- `footprint.json`: project tree including history/services/generated evidence was
  about 65.19 GiB at measurement, below the 250 GB cap. Later small smoke artifacts
  do not materially change that total.

Only task code, scripts, scope/report/plan and the current-state route are included
in the local task commit. The three pre-existing owner modifications remain outside it.
