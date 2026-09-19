# MeridianSquad agent development

Current lobby status, 2026-09-16: MSQ-4/6/7/14/20/28/30 are closed by owner
deferral. Future lobby work awaits the owner's new list after gameplay
integration; older in-progress/backlog/in-review wording below is historical.
See [the closure decision](Approvals/LobbyDeferred01-OwnerClosure01.json) and
[summary](OpeningLobbyDeferred01.md). UpperVoid01 remains accepted and closed.

## Constraints and decisions

- Current review responsibilities, 2026-09-19: one primary technical reviewer for
  substantive changes; controller acceptance checks scope, evidence applicability
  and finding closure without repeating the full technical review. See
  [the standing workflow](#review-responsibilities) and
  [owner decision](Approvals/ReviewResponsibilities01.json).
- Current standing owner instruction, 2026-09-17: all project executors and
  reviewers use max reasoning at standard speed. Verify actual native settings;
  retain max when restoring other task-local profile values. See
  [WorkerReviewerMax01](Approvals/WorkerReviewerMax01.json). Earlier high/medium
  execution records below remain historical evidence, not current defaults.

- Ryzen 9800X3D, 32 GB RAM, RTX 5090. Project disk budget: at most 250 GB.
- Use only the existing $200/month Codex subscription. Paid APIs and additional
  cloud subscriptions are excluded. Available local models are allowed.
- Judge quality by accepted, verified tasks, including rework.
  Use Astra for difficult tasks and scripts for repeatable operations.
- Limit context, concurrent agents and heavy workloads.
  Allow only one agent to change the state of each open editor.
- Use Russian in the owner's direct chat only. Write all project content and
  internal Multica progress/discussions/reports in English, including
  documentation, code comments, names and commit messages.
- The owner selected Multica as the default route for project implementation.
  Direct chat handles requirements, dispatch, acceptance and administration.
  The controller stays active through dispatched execution, handoff review and
  bounded corrections to a verified result or a concrete owner decision gate.
  Ending the direct turn immediately after background dispatch is not completion.
- Lobby production requires explicit owner approval of a named concept-art
  version before any renewed 3D layout, blockout, architecture or modular model
  work. The owner explicitly approved `LobbyArt-Review02` on 2026-09-13,
  authorizing the separate [layout revision](Tasks/OpeningLobbyLayout02.md).
  The current Stage 1 layout remains rejected. See the
  [concept-art task](Tasks/OpeningLobbyConceptArt.md) for the approved art scope.
- The owner subsequently rejected MSQ-9/Layout02 for insufficient architectural
  scale and requires at least twice its scale with clear monumentality. MSQ-10
  completed [scale drawings](OpeningLobbyScaleReview.md), owner-approved on
  2026-09-14. MSQ-11 implements the separate Layout03 neutral blockout.
  [Visual acceptance](VisualAcceptance.md) now requires a dimensioned package,
  an independent visual review and explicit owner approval. Dedicated Multica
  Spatial Designer and Visual Reviewer profiles use Astra/high/default; existing
  profiles and user-level Codex settings are unchanged. Runtime concurrency stays one.

## Review responsibilities

Standing workflow approved on 2026-09-19 under
[ReviewResponsibilities01](Approvals/ReviewResponsibilities01.json), implemented
in [MSQ-83](Tasks/ReviewResponsibilities01.md). This clarifies future execution;
historical reviews remain unchanged.

| Role | Responsibility |
| --- | --- |
| Executor | Implement the bounded change, run focused self-checks, and supply the candidate, results and known limitations. |
| Primary independent reviewer | Inspect the relevant candidate code/assets and evidence, evaluate technical criteria and test adequacy, identify defects and verify correction of findings. |
| Controller | Own task scope, dispatch, progress, correction coordination, owner-request acceptance, evidence applicability, finding closure, administrative closure, commit and owner handoff. |
| Owner | Retain the required design selections and final visual/play acceptance. |

Before dispatch, identify the acceptance criteria, expected evidence and one review
owner for each criterion in the existing task brief. Use one primary independent
technical reviewer for substantive changes, such as gameplay logic, timing,
architecture and significant visual work. Add a specialist only for distinct
criteria the primary reviewer does not cover; do not assign overlapping full
reviews. Technical and visual verdicts remain distinct where required.

Small, obvious, low-impact changes can finish with executor self-checks and
controller acceptance when no explicit independent review requirement applies.
The controller may execute small administrative updates directly under AGENTS.md;
this does not require adding a worker or reviewer. Record the chosen review route
briefly in the existing task record rather than creating another review document.
Required independent visual review, named owner approval and the protagonist
concept owner-only exception remain in force.

The executor provides evidence that identifies the checked candidate (commit,
hashes or an existing suitable manifest), checks performed, results, and limits.
The independent reviewer directly examines the relevant implementation and actual
views for visual claims; an executor's PASS summary alone is insufficient. Reuse
credible, applicable executor test output instead of rerunning every passing test.
The reviewer requests or performs only the missing checks needed for a verdict.

The controller checks that the delivered scope answers the owner, evidence applies
to the delivered version, mandatory criteria have a supported verdict, findings
are closed or explicitly retained within the authorized scope, and owner edits
are preserved. This is task acceptance, not a second complete code/asset review,
independent reimplementation of the verifier, or repetition of passing tests.

Repeat a check or deepen controller investigation only for a concrete reason:
a relevant candidate change after the evidence was collected; missing, stale or
unreliable evidence; conflicting results; or a specific uncovered risk. Record the
reason and affected criteria in the existing task/review report, then check only
that subset and related transitions. Reuse unaffected evidence with its original
candidate identity; do not silently rebaseline historical results. Corrections
return to the same review scope; they do not restart the entire review by default.
Additional integrated checks need a newly coupled risk or an explicit task criterion.

The controller remains accountable through completion. Max reasoning, standard
speed, one production writer, existing authorization boundaries and the local
closure commit still apply. This workflow grants no successor dispatch or owner
visual acceptance.

## Stage 1: Codex and Unreal

Verified on this computer on September 13, 2026:

| Component | Status |
| --- | --- |
| Unreal Engine | 5.8.1, installed at `D:\UE_5.8` |
| Project | C++, `MeridianSquad`; one verified Blender-to-Unreal smoke-test mesh |
| Codex CLI | 0.153.4, signed in through ChatGPT |
| Blender | 5.2.1 LTS; installed community MCP 1.9.1 / addon 1.6, protocol 5 verified |
| Substance Painter | 12.1.4; project, fill layer, texture export and UE material verified through MCP |
| Substance Designer | 16.0.6; MCP connection not yet verified |
| Substance Sampler | 6.0.2, executable verified; MCP connection not yet verified |
| LM Studio | 0.4.24+1; no local model selected for the project yet |
| Multica | Local 0.4.43; read-only and complete asset tasks accepted; selected for implementation |
| PostgreSQL | Portable 17.11; Multica task database, loopback port 15432 |

The verified Sampler executable is
`C:\Program Files\Adobe\Adobe Substance 3D Sampler\Adobe Substance 3D Sampler.exe`.

The built-in `ModelContextProtocol` and `EditorToolset` plugins are enabled in
the `.uproject`. Project settings start MCP with the editor at
`127.0.0.1:8000/mcp`. The port binds to loopback. Tool discovery is enabled:
read detailed schemas on demand through `list_toolsets`, `describe_toolset`
and `call_tool`. `AllToolsets` is not needed yet. Epic MCP is experimental
in this version.

The client connection is configured in `.codex/config.toml` as `unreal_epic`.
Open this project in Unreal before starting a new Codex session.
Codex applies project settings only for a trusted directory.
An existing session may require an MCP/agent restart to load new tools.
The user's model and reasoning settings have not been changed.

The check on September 13, 2026 at 13:21 MSK passed:
`MeridianSquad.uproject` was running, port 8000 listened on `127.0.0.1`,
initialize negotiated protocol `2025-11-25`, and the initialized notification
returned HTTP 202. Three discovery tools and 19 toolsets were available.
Epic MCP returned `IsPIERunning=false` and the current level
`/Temp/Untitled_1`. The level was not saved and no assets were changed.

Repeatable check from the project root in PowerShell, without installing libraries:

```powershell
& 'D:\UE_5.8\Engine\Binaries\ThirdParty\Python3\Win64\python.exe' Scripts\check_unreal_mcp.py
```

Results are stored in `Saved/AgentSetup/McpProbe/`; `latest.json` contains
the summary and check time. The script checks HTTP and editor reads;
loading a newly configured MCP into the current Codex session requires
a separate agent/MCP restart. `codex.cmd mcp get unreal_epic` already reads
the configuration. The project directory is marked as trusted in the user's
Codex config; its previous version is saved in `C:\Users\Origa\.codex\backups\`.

After the Codex session restart on September 13, 2026, native Epic MCP tools
were available to the agent. Direct `mcp__unreal_epic__call_tool` calls returned
`IsPIERunning=false` and `get_current_level=/Temp/Untitled_1`, verifying stage 1
from the restarted Codex session.

## Stage 2: Blender to Unreal

The first transfer passed on September 13, 2026. Codex used the installed
community Blender MCP to create a dedicated `PipelineProbe` scene, exported FBX,
then used official Epic MCP to import and inspect the resulting Unreal assets.
The startup Blender scene and Unreal level were preserved.

- Source: `Assets/Source/SmokeTest/PipelineProbe.blend`.
- Unreal mesh: `/Game/Development/SmokeTest/SM_PipelineProbe`.
- Material: `/Game/Development/SmokeTest/M_PipelineProbe_Green`.
- Blender dimensions: 2 x 1 x 0.5 m; Unreal dimensions: 200 x 100 x 50 cm.
- Expected bounds in cm: min `(0, -50, 0)`, max `(200, 50, 50)`.
  Actual bounds passed a 0.01 cm tolerance, confirming the positive X direction
  from the tail pivot as well as scale. Both sides had 24 triangles.
- The Blender source has one UV layer. Unreal has one material slot; its green material was bound,
  saved and visually checked through an Unreal asset thumbnail.
- The saved Blender file contains only the probe scene, object and material.
- Detailed results and SHA-256 hashes: `Saved/AgentSetup/BlenderProbe/`.
  The three source/Unreal asset files total approximately 92 KiB.

Start Blender with the installed addon using PowerShell:

```powershell
& 'D:\blender\blender.exe' --python "$PWD\Scripts\start_blender_mcp.py"
```

The bootstrap requires the installed community addon and a GUI session. It binds
to `127.0.0.1:9876`, disables content telemetry and external asset/generation
integrations for the session, and does not save startup preferences.
The project's `DISABLE_TELEMETRY=true` override also disables minimal anonymous
usage collection after the Blender MCP server is next restarted; during the
current session, the opt-out tool only disabled prompts/code/images/scene data.

`Scripts/create_pipeline_probe.py` creates the probe on a clean run and refuses
to overwrite existing source/export files. It runs inside Blender. The FBX export
is generated under `Saved/Exports/SmokeTest/`, outside Git. Export settings are
`axis_forward=-Y`, `axis_up=Z`, `apply_unit_scale=True`, and
`apply_scale_options=FBX_SCALE_NONE`, with no animation. These settings were
validated against Epic's `StaticMeshTools.import_file` defaults. A new workflow
using different import settings must recheck bounds rather than assume parity.

## Stage 3: Painter to Unreal

The first Painter transfer passed on September 13, 2026. The existing probe mesh
now uses a material driven by exported 1024 x 1024 Base Color, DirectX Normal and
ORM textures. The Painter source project, texture files and Unreal assets are
saved. Channel values, texture settings, graph connections, shader compilation
and the rendered result were checked. Painter's project audit reported no issues.

See [Painter workflow](PainterWorkflow.md) for the pinned bridge installation,
repeatable operations, verification evidence and the scope of this probe.
The transfer used the MCP SDK over stdio. After the agent restart on
September 13, 2026, native `substance_painter` tools appeared in Codex and
`painter_status` confirmed a working connection to Painter 12.1.4 with a project open.

## Stage 4: Local Multica pilot

Multica 0.4.43 is running natively on Windows with a production web build,
Go API, PostgreSQL 17.11 and one Codex runtime. Existing ChatGPT authentication
was reused; the optional server LLM is disabled. No Docker or WSL was installed.

Issue `MSQ-1` passed on its first attempt using Astra, medium reasoning and
standard speed. It verified the project rules in the existing project directory.
Multica restored its temporary `AGENTS.md` changes; project and user Codex
configuration hashes were unchanged. Stop/start and result persistence passed.

See [Multica pilot](MulticaPilot.md) for operation, pinned dependencies, evidence,
token measurements and limits. The read-only pilot was followed by the complete
asset comparison recorded below.

## Stage 5: Complete asset task and orchestration comparison

On September 13, 2026, two independent Astra medium/standard workers created the
same specified crate through Blender, Painter and official Epic Unreal MCP.
Direct BenchA and Multica BenchB both passed independent acceptance on their
first submission: 864 triangles, eight closed components, valid UVs, two Painter
sets, six maps and nine saved UE assets. Multica issue MSQ-2 is accepted and done.

Direct execution took 449.25 seconds; Multica took 334 seconds. Multica used more
uncached input but fewer model responses, less cached input and less output.
One sequential pair cannot establish a general causal saving. Native output
includes reasoning; Multica 0.4.43 adds reasoning again in its output counter.
The large shared preparation/measurement cost is recorded separately and was
disproportionate to one simple prop. Reuse the existing scripts and validators.

See [the full comparison](Benchmarks/OrchestrationABComparison.md), including
previews, native usage, quality evidence, storage, limitations and public hashes.
The finite direct measurement client is not a replacement task dispatcher.

## Storage

Git and Git LFS are prepared for source files, configuration, decisions and
binary assets. Caches, builds, local IDE state and `Saved/` are excluded from Git.
A Git repository alone is not a backup. The `origin` remote is configured as
`https://github.com/NikolaevAnton-github/Meridian.git`, and the development branch
is `main`. Commit authorship is configured locally for this repository as
Anton Nikolaev, using the email supplied by the user. Git Credential Manager
uses the `NikolaevAnton-github` account. Check Git status and the upstream branch
for synchronization state. An off-device backup has not been configured.
The local Multica database has one same-disk dump recorded in its pilot guide.
Copies of existing files from before setup are stored in
`Saved/AgentSetup/20260913-131612/`.

The template Android File Server is disabled for the current Windows stage,
and its token has been removed from tracked configuration. When adding Android,
configure this service separately with local credentials.

Files are the first system layer, not a replacement for the planned database.
Structured metadata, checks and asset relationships are stored in a database;
large source files and outputs will remain in files referenced by paths and hashes.
PostgreSQL now stores Multica's tasks, runs and related application data.
The minimal asset metadata registry is implemented in the separate local
`meridian_assets` database and accepted as MSQ-3: 3 assets, 48 artifacts and
59 evidence-backed dependency records with explicit certainty. See
[asset registry usage](AssetRegistry.md) and [acceptance](AssetRegistryAcceptance.md).
No graph database is installed. Keep task state in Multica, asset metadata in
the registry, and large source files and outputs in files/Git LFS.

## Next stages

1. Completed: verify Blender MCP and transfer one simple asset to UE with the
   correct scale, orientation and material. Results are recorded in stage 2.
2. Completed: verify Painter MCP, create a project and fill layer, export textures
   and connect them in UE. Add Designer and Sampler as tasks require them.
3. Completed: deploy local Multica using existing Codex authentication, limit
   concurrency to one and verify one complete read-only task.
4. Completed: one full asset task through Multica and an equivalent direct run,
   both independently accepted. The owner selected Multica for implementation;
   reuse acceptance scripts and native metrics.
5. Completed and accepted: the
   [minimal asset registry](Tasks/AssetRegistry.md) through Multica. It reuses
   PostgreSQL, distinguishes verified dependencies from declarations, and
   registers saved files without regenerating assets.
6. In progress: the [opening lobby walkthrough](Tasks/OpeningLobby.md), Multica
   parent MSQ-4. MSQ-5 passed technical acceptance: the saved on-foot prototype
   supports the full entrance/elevator route, side paths and return, with verified
   collision, gravity and mouse look. See [Stage 1 handoff](OpeningLobbyStage1.md).
   The owner clarified on 2026-09-13 that the current layout is not approved;
   the technical acceptance and its evidence remain historical results.
   The owner subsequently explicitly approved `LobbyArt-Review02`: both
   OwnerReferences01 images and the Review02 entrance security supplement.
   The [concept-art task](Tasks/OpeningLobbyConceptArt.md) has therefore met its
   owner approval gate. MSQ-9 implemented the separate
   [lobby layout revision](Tasks/OpeningLobbyLayout02.md), preserving the
   rejected Stage 1 prototype and its historical verification evidence.
   [Layout02](OpeningLobbyLayout02.md) passed controller technical review but
   was rejected by the owner for insufficient architectural scale. MSQ-9 is
   initially returned to backlog, unassigned. After the replacement scale was
   accepted, MSQ-9 was cancelled as superseded; its assets/evidence are preserved.
   MSQ-10 completed the
   [dimensioned scale package](OpeningLobbyScaleReview.md); independent visual
   review passed after a bounded label correction. On 2026-09-14 the owner
   explicitly approved the complete identified package and authorized proceeding
   to the [Layout03 neutral blockout](Tasks/OpeningLobbyLayout03.md).
   MSQ-11/Correction01 passed technical and independent visual review; the owner
   explicitly accepted its in-game scale on 2026-09-14, deferred detail assessment
   and authorized continuing. See the [scoped decision](Approvals/LobbyLayout03-Scale01.json).
   MSQ-6 now follows [Architecture01](Tasks/OpeningLobbyArchitecture01.md) with
   accepted scale preserved. Its [controller review](OpeningLobbyArchitecture01Review.md)
   records ten completed execution/review runs and Review04's open fixed-glazing
   criterion. The owner's later rejection concerns overall architectural quality,
   beyond fixed glazing. MSQ-12 now develops two dimensioned entrance/colonnade
   alternatives under [ArchitectureRework01](Tasks/OpeningLobbyArchitectureRework01.md),
   followed by an independent MSQ-13 review and named owner selection before 3D.
   MSQ-6 remains incomplete and unassigned; detail acceptance has not been granted.
   MSQ-7 (atmosphere and final acceptance) remains backlog pending architecture/material
   review and the owner's detail decision.
   The owner's [game direction](Design/GameBrief.md) and
   [story foundation](Design/StoryCanon.md) are recorded in English.
7. Use 10–15 real tasks to measure first-pass acceptance, rework, time and
   available subscription usage metrics; use the results to tune model selection.

## Architectural specialization, 2026-09-14

The architectural recovery introduces three project-owned skills under
`.agents/skills/`, imported and assigned in the existing Multica installation:

- Spatial Designer: `environment-reference-analysis` and
  `environment-architecture-production`.
- Environment Artist: `environment-architecture-production`.
- Visual Reviewer: `environment-architecture-review`.

These skills distinguish primary scale, secondary depth and tertiary detail;
require actual image inspection, coherent dimensional handoff and independent
whole-to-part judgement; and permit explicitly authorized creative development
beyond weak proxy surfaces. Their presence does not establish artistic quality.
MSQ-12/13 are the first live exercise, not an additional benchmark campaign.
Both runs are complete. The [identified 2D package](OpeningLobbyArchitectureRework01.md)
passed independent review, with A recommended. The owner subsequently selected
A in direct chat; the [external decision](Approvals/LobbyArchitectureRework01-VariantA.json)
binds the reviewed package. After executor clarification, the owner explicitly
authorized max-effort production. MSQ-14 implemented the bounded neutral A assembly;
fresh MSQ-15 visual and technical evidence review passed with no required correction.
Both ran on Astra/max/standard. The [verified 3D handoff](OpeningLobbyArchitectureReworkA01Review.md)
is ready for the owner walkthrough; 3D acceptance remains pending, MSQ-6 remains
incomplete and MSQ-7 backlog. Task-local profiles returned to their prior settings.

The installed model catalog confirmed Astra `max` at standard speed. It is a
task-local setting for this design/review study, with matching native configuration;
other roles are unchanged. Existing subscription authentication and single-task
Multica concurrency remain. Native effort and usage evidence is recorded under
`Saved/OpeningLobby/ArchitectureRework01/Controller/`, using the existing summarizer
without adding reasoning to native output a second time.
After the verified runs, the two profiles returned to their prior high-effort
baseline while retaining specialized instructions and assigned skills.

## Focused functional lobby revision, 2026-09-14

After walking through ReworkA01, the owner gave positive feedback and requested
four terminal colonnade enclosures with inverse hall/aisle door orientation,
a two-lane entrance checkpoint and a larger inner elevator with an opaque upper
wall for future branding. The remaining architecture and approved scale stay.
The scoped feedback is recorded in
`Docs/Approvals/LobbyArchitectureReworkA01-Walkthrough01.json`.

MSQ-16 prepared `LobbyFunctional-Revision01/Candidate01` as five dimensioned 2D
sheets. Fresh MSQ-17 independently passed visual and technical review with no
required correction. Both ran on Astra/high/standard through the existing
subscription and one-task Multica runtime. Actual images, common dimensions,
route arithmetic and immutable fingerprints were checked. Task-local instructions
were restored afterward; no run remains active. No 3D/editor mutation occurred.

The [reviewed handoff](OpeningLobbyFunctionalRevision01.md) binds all 29 candidate
entries and links the sheets, dimensions and verdict. The owner's next decision
is named-package approval of new dimensions, the 11.2 m central-only checkpoint
interpretation, closed terminal crossovers/adjacent-bay alternatives and blank
sign reservation. MSQ-16 remains in review; MSQ-17 is done. Final look/atmosphere
and overall milestone acceptance remain pending.

## Owner-marked functional correction, 2026-09-14

The owner rejected FunctionalRevision01's narrow-room interpretation and supplied
yellow plan markup. MSQ-18 prepared LobbyFunctional-Revision02/Candidate01 with
four full-depth corner rooms, entrance doors in transverse caps, inner doors
facing the hall and four central columns reaching the 18 m ceiling. The prior
terminal side-aisle bypass is closed. Old candidate/review bytes remain intact;
MSQ-16 is cancelled as superseded, not recorded as owner-approved.

Fresh MSQ-19 independently passed visual and technical review with no required
correction. Both design and review used Astra/high/standard and assigned skills,
existing subscription authentication and single-task concurrency. The prior
drawing/occlusion/verification pipeline was reused. Final verification covers
35 frozen entries, 256 checks, 15 analytic routes and 377 protected original files.
Profiles were restored; no run remains active. No editor or 3D mutation occurred.

See [the exact five-sheet handoff](OpeningLobbyFunctionalRevision02.md). MSQ-18
remains in review and MSQ-19 is done. Owner approval is pending for the proposed
room/door dimensions, four 2.4 m square columns at X +/-12.6 / Y +/-2.4, their
visual density, roof joints and retained checkpoint/elevator dimensions. The
new 2.4 m axial and 2.0 m lateral passages are exposed on the drawings; analytic
clearance is not runtime acceptance. Final materials and atmosphere remain later work.

## Documentation

- [Epic: Unreal MCP](https://dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor)
- [Codex: MCP connection](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)
- [Multica: self-hosting](https://github.com/multica-ai/multica/blob/main/SELF_HOSTING.md)
