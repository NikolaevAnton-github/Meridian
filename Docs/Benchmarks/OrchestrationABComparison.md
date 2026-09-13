# Blender to Painter to Unreal: direct Codex versus Multica

Both independently created assets passed external acceptance on September 13,
2026. In this single pair, Multica finished sooner with fewer model responses,
less cached input and less output, but 10.0% more uncached input. The experiment
does not support a blanket claim that Multica greatly increases usage. It also
does not establish that Multica causes a general saving: there is one observation
per route, with different model decisions and sequential execution.

The largest cost was building and checking this first measurement harness, not
the difference between the two asset workers. Reuse the saved procedures for
ordinary development; do not rebuild this experiment for each prop.

## Task and controlled conditions

The [frozen task](OrchestrationABTask.md) required a beveled industrial crate,
120 x 80 x 90 cm, eight closed components, two materials and six 1024 x 1024
PNG maps. Each worker created its own Blender source, FBX, Painter project,
textures and nine Unreal assets. This was a complete simple asset pipeline;
high-poly baking, wear painting, complex art direction and gameplay were outside
its scope.

Both routes used Codex CLI 0.153.4, GPT-6 Astra, medium reasoning, standard speed,
ChatGPT subscription authentication, the same workspace and reference recipes,
and Blender, Painter and official Epic MCP. Native subagents and memory were
disabled in both workers. No paid API, extra credits or cloud generation was used.
The Multica optional server LLM remained disabled.

The randomized order was BenchA/direct first, BenchB/Multica second. Each had a
fresh native session and task-scoped Codex home. The base prompts differed only
in RUN_ID; Multica added its normal issue workflow and instructions. Each worker
had exclusive ownership of all three editor instances. Before BenchB, Painter
was reopened on the clean baseline, and Blender's baseline scene, selection and
material count were restored. BenchA files remained saved in separate folders;
BenchB was prohibited from reading them. The Unreal level stayed unchanged.

Multica 0.4.43 ran locally on Windows with PostgreSQL, concurrency one and an
in-place project directory. Its services remained idle during the direct run,
so this is not a comparison against an uninstalled Multica system. There were no
duplicated Unreal worktrees. Each worker had a 30-minute upper time budget;
neither reached it. Configuration/parser checks before the runs made no asset
worker model turns; they did involve the separately counted controller/helpers.

## Worker measurements

| Metric | Direct / BenchA | Multica / BenchB | Observed difference |
| --- | ---: | ---: | ---: |
| Worker duration | 449.25 s | 334 s | Multica 25.7% shorter |
| Model responses | 22 | 16 | 6 fewer |
| Input without cache | 75,584 | 83,178 | Multica 10.0% more |
| Cached input | 1,255,296 | 856,064 | Multica 31.8% less |
| Total input, including cache | 1,330,880 | 939,242 | Multica 29.4% less |
| Output, including reasoning | 11,925 | 8,198 | Multica 31.3% less |
| Reasoning, already within output | 900 | 230 | Do not add again |
| Native input plus output | 1,342,805 | 947,440 | Accumulated model usage |
| MCP call events | 36 | 34 | Includes discovery and checks |
| Shell command events | 10 | 11 | Includes workflow administration |
| Model exec calls | 21 | 15 | Can contain several tool operations |
| FileChange events | 23 | 16 | File events, not patch call counts |
| Failed worker tool calls | 1 | 0 | Direct corrected an invalid backup mode |
| Worker attempts / external repair turns | 1 / 0 | 1 / 0 | Both accepted on first submission |

Direct duration is the native turn interval; its client launch through cleanup
took 454.047 seconds. Multica duration is the server task interval, including
its workflow administration, at one-second timestamp resolution. External
acceptance, baseline restoration, experiment preparation and publication are
outside these worker durations. The independent Unreal check took 14.11 seconds
for BenchA and 13.60 seconds for BenchB. A single synchronized timer for all
external validation and visual review was not collected.

Multica's API reported 8,428 output tokens. Its pinned Codex adapter adds the
230 reasoning tokens to an output counter that already includes them. The
original native trace gives 8,198; this report uses native counters for both
routes. API and native records reconcile after reproducing the adapter's
normalization. Likewise, the direct harness's adapter-compatible output field
is 12,825, while its canonical output is 11,925.

The project AGENTS file grew from 2,702 to 17,858 bytes during Multica execution:
a 15,156-byte net increase, including any newline normalization. This is a file
size measurement, not a token estimate or the whole prompt. It was restored
after completion. The first run's repeated context accumulated over 22 responses;
the second accumulated over 16. That difference matters alongside instruction
size and caching. It cannot be attributed exclusively to orchestration.

For an illustrative comparison using published Astra standard token weights,
`uncached_input + 0.1 * cached_input + 5 * output` gives 260,738.6 for direct and
209,774.4 for Multica, 19.5% lower in this pair. These weights follow the published
250 / 25 / 1,250 credits per million token rates. This is a derived comparison,
not purchased credits, a billed amount or the measured percentage of the included
$200 subscription allowance. [OpenAI pricing](https://learn.chatgpt.com/docs/pricing).

## Independent quality acceptance

| Criterion | Direct | Multica |
| --- | --- | --- |
| Saved source and actual exported FBX | Pass | Pass |
| Eight closed components, outward winding, no degenerate triangles | Pass | Pass |
| 0.01 m bevel, two segments, component dimensions | Pass | Pass |
| 448 source vertices / 864 triangles; same UE triangle count | Pass | Pass |
| Base-centered pivot, applied transforms, correct bounds | Pass | Pass |
| One finite UV layer, nonzero UV areas, no overlaps within each material | Pass | Pass |
| Two Painter texture sets, one fill per set, clean audit | Pass | Pass |
| Six 1024 x 1024, 8-bit PNGs; color and ORM/normal samples | Pass | Pass |
| Two UE slots, six texture settings, ten material connections | Pass | Pass |
| Material compilation and nine saved, initially clean UE assets | Pass | Pass |
| Existing 40 tracked files preserved before report publication | Pass | Pass |

The controller loaded the saved Blender library in a separate headless Blender
process and independently imported the actual FBX. PNG validation decoded the
images and sampled conservative UV interiors. Unreal validation used registered
Epic tools, checked dirty state before recompilation, and verified physical asset
files and hashes. Painter's currently loaded saved project and both layer stacks
were inspected independently. Each stack also retained Painter's empty default
paint layer; each contained exactly one requested fill layer.

DirectX/per-fragment creation settings are supported by the successful typed
creation plans, not by an independent parser of the saved SPP. Flat normals do
not test the sign of a non-flat normal map. PNG sampling is not exhaustive over
all texels. The saved Blender source is an isolated library: append its named
Scene to view it; it is not a saved editor workspace. No high-resolution art
review, performance-in-game, UV lightmap assessment or bake-quality claim is made.

| Direct | Multica |
| --- | --- |
| ![Direct Unreal preview](Images/BenchA.png) | ![Multica Unreal preview](Images/BenchB.png) |

All six exported Painter PNGs are byte-identical to their counterpart from the
other run. These are original 256 x 256 Unreal asset thumbnails. Both show the same blue
crate, separate lid, metallic corner posts, feet and visible bevels, with no
obvious missing-material or scale defect. They are not pixel-identical: mean
absolute RGBA component difference is 0.05574 on a 0-255 scale, maximum 18.
This small thumbnail difference is not a general artistic quality score.

## Shared preparation and total experiment cost

<!-- SHARED_ACCOUNTING_START -->
Snapshot: **2026-09-13T12:35:46.871816+00:00**, from the user instruction at
2026-09-13T11:45:22.582Z. This includes the root and locally recorded
helper threads in that root session, counted once per model response. It is a
lower bound for the whole experiment because subsequent publication and final
chat responses are outside the snapshot.

| Work | Uncached input | Cached input | Output including reasoning |
| --- | ---: | ---: | ---: |
| Both asset workers combined | 158,762 | 2,111,360 | 20,123 |
| Shared controller, preparation and helpers through snapshot | 653,262 | 21,203,328 | 155,307 |
| Combined through snapshot | 812,024 | 23,314,688 | 175,430 |

[Public accounting snapshot](OrchestrationABSharedUsage.json) records the cutoff
and measurement limits. Cached input is accumulated processing of context,
not millions of words of unique project data.
<!-- SHARED_ACCOUNTING_END -->

Shared work includes protocol design, matching native client configuration,
measurement-client implementation, validator implementation and review,
controller actions, independent acceptance and report preparation. It is shared
by the comparison and cannot fairly be assigned entirely to either route.
The prior Multica installation/read-only pilot is outside this instruction's
accounting boundary. All work used the existing subscription; no dollar value
or exact remaining quota is inferred from token counts.

This setup effort was disproportionate to one simple prop. The implementation
and helper-agent work, not an established Multica surcharge, dominated the
experiment. Reuse the checked-in validators, scripts and bounded task pattern
for subsequent work. Measure new ordinary tasks without repeating two workers
or recreating the measurement harness for every asset.

## Machine and storage observations

Each deliverable occupies about 15.2 MiB including its generated FBX: 15,949,775
bytes direct and 15,939,467 bytes Multica. Two 12.3 MiB baseline backup copies
were moved under ignored Saved. No user assets were deleted.

The project inventory after the pair was 8.849 GiB by file-entry length,
7.941 GiB counting hard-linked files once, before final Git/LFS publication.
Multica tooling accounts for 5.670 GiB by entry length. Junction targets were
excluded to avoid counting shared installations; these are file lengths, not
allocated disk blocks. The project remains well within its 250 GB budget.

Five-second samples recorded at least 10.271 GiB available system RAM during
direct execution and 10.110 GiB during Multica. Sampled peak private commit:

| Process group | Direct MiB | Multica MiB |
| --- | ---: | ---: |
| UnrealEditor | 8,407.6 | 8,032.0 |
| Painter | 4,848.7 | 5,010.5 |
| Blender | 1,629.5 | 1,563.9 |
| Multica runtime | 56.9 | 61.8 |
| PostgreSQL processes | 74.8 | 77.3 |

These are whole-host sampled process groups, not isolated allocation or causal
overhead measurements. Private commit is not resident RAM. Codex groups also
include controller/helper sessions. API/web Node processes and GPU/VRAM were
not included in this sampler. The earlier idle-service measurement remains in
the [pilot guide](../MulticaPilot.md). No local model, bake or render workload ran
concurrently with the asset workers.

## Decision and evidence

Keep Multica for complete queued asset tasks, acceptance records and task
history; keep direct Codex for short interactive edits or diagnosis when no task
coordination is needed. One card should describe a useful finished result with
acceptance criteria. Keep one DCC owner and concurrency one. Prefer the saved
scripts and targeted tool schemas, and record native usage per accepted task,
including corrections. Measure several subsequent real tasks before asserting
a stable saving or changing model-selection policy. Astra medium/standard passed
this task; this experiment did not compare other models or orchestration systems.

MSQ-2 completed on its first attempt and was marked done after independent
acceptance. Local Multica services remain available. An updated local database
backup is saved at `Saved/Multica/backups/asset-ab-20260913.dump`.
Asset metadata is the next
design stage; no additional task database or graph database was installed.

- [Public result data and hashes](OrchestrationABResults.json)
- [Frozen protocol](OrchestrationABProtocol.json)
- [Task specification](OrchestrationABTask.md)
- [Reusable measurement and acceptance source](../../Scripts/Benchmarks/OrchestrationAB/README.md)
- Full native traces, RPC logs and verification JSON: `Saved/AgentSetup/OrchestrationAB/`.
- Multica issue: MSQ-2; task `01a09ab2-6231-79a5-a4c5-34ad73ba4b90`.

The public report excludes authentication files, account details and large logs.
