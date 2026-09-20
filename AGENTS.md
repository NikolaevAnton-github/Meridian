# MeridianSquad agent instructions

Read [current project state](Docs/ProjectState.md) before choosing or dispatching
work, then read only the relevant task and its linked decisions. This file holds
durable rules; task history is not an execution queue. Later explicit owner
instructions supersede earlier guidance within their stated scope.

## Communication and authorization

- Use Russian in the owner's direct chat with Codex. Write all project content
  in English: documentation, code comments, names, commits and internal Multica
  progress messages, task discussions and final reports.
- Codex may launch existing applications and local project services needed for
  authorized work without asking again. Starting a service does not authorize
  unrelated execution, purchases or a pending design selection.
- Current family: MSQ-90 [stance, balance and terrain support](Docs/Tasks/PhysicsControlRefinement01Plan.md)
  contains MSQ-91 through MSQ-96 under the
  [owner's task-creation request](Docs/Approvals/PhysicsControlRefinement01-TaskCreation01.json).
  The later [MSQ-97 next-task decision](Docs/Approvals/PhysicsControlRecoverability01-NextTask01.json)
  inserts physical recoverability after MSQ-91 and before MSQ-92. The later
  [MSQ-97 start and review waiver](Docs/Approvals/PhysicsControlRecoverability01-OwnerStart01.json)
  authorized the delivered Candidate07 without an independent reviewer. See
  [the task](Docs/Tasks/PhysicsControlRecoverability01.md) and
  [handoff](Docs/PhysicsControlRecoverability01Handoff.md); focused self-checks and
  controller scope/evidence acceptance pass, with owner motion/play judgement separate.
  The later [MSQ-91 start and review waiver](Docs/Approvals/PhysicsControlLegPose01-OwnerStart01.json)
  authorized the delivered Candidate07 stance correction. See the
  [handoff](Docs/PhysicsControlLegPose01Handoff.md); MSQ-89 Candidate05 and its
  evidence remain preserved. MSQ-92 through MSQ-96 remain undispatched.
  Review waivers stay task-scoped. Owner play/motion acceptance stays separate. The MSQ-85
  [relative slowdown decision](Docs/Approvals/PhysicsControlVariants01-OwnerScope01.json)
  requires partial player movement/firing slowdown while the world slows more,
  superseding the earlier normal-player slowdown rule. Full stop remains later scope.
  MSQ-69, MSQ-68 and MSQ-82 are verified prerequisites in the sequential
  [CombatSlice01 task family](Docs/Tasks/CombatSlice01Plan.md).
  [MSQ-82 review](Docs/CombatTiming01Review.md) records timing acceptance and the
  retained low-FPS recoil limitation. Manny remains a technical placeholder;
  MSQ-70 and successors remain undispatched. See ProjectState for current scope.
  PurchasedArms06 is the retained rifle presentation baseline.
  Original modeling and its successors are paused;
  lobby architecture remains deferred. Preserve character sources and evidence.
  The protagonist concept batch is evaluated by the owner alone; do not dispatch
  an independent concept reviewer. Later integrated review is separate.

## Budget and preservation

- Use the existing $200/month Codex subscription. The owner's existing Tripo
  Studio and Meshy web allowances are the scoped exception for the protagonist
  AI3D pipeline; free Hunyuan3D Studio is an alternative subject to verified terms.
  No new paid services, purchases, credit top-ups or separately billed API usage.
  Local models are allowed within measured RAM/VRAM and project disk capacity.
- The entire project must fit within 250 GB, including generated data, local
  version history and project services. Avoid duplicate Unreal worktrees and
  unrestricted caches. Never delete owner assets to reclaim space.
- Preserve owner edits, original sources, accepted assets, rejected candidates
  and exact review/approval evidence. Do not restore historical worker bytes
  over owner edits or silently rebaseline an immutable candidate manifest.
- Track code, configuration, accepted decisions and asset sources in Git; use
  Git LFS for binary assets. Keep generated data and large logs outside Git.
  Never put credentials in tracked files or tool output.
- After closing each task, the controller must commit its verified, task-scoped
  changes locally before the final owner handoff. Include the task ID in an
  English commit message; preserve unrelated owner edits. Workers leave the
  closure commit to the controller unless explicitly delegated. See the
  [standing owner instruction](Docs/Approvals/TaskClosureCommits01.json).

## Execution and tools

- Multica is the default implementation route; use the existing project and
  keep production concurrency at one. Direct chat handles clarification,
  dispatch, review and small administrative updates.
- For trivial local corrections such as changing one key binding, the controller
  edits directly without dispatching an executor or reviewer. Use only the build
  or narrow check needed to make the change effective; avoid a task-sized workflow.
- For administrative access, use `Scripts/multica.ps1 -Action StartServices`
  (database/API/web); start the task runtime only for intended execution.
  Use `suppress_run=true` / CLI `--no-start` for administrative status, assignment
  or description changes. Dispatch intended runs explicitly.
- The controller stays active through the run, handoff review and required
  bounded corrections until a verified result or a concrete owner decision gate.
  Dispatch or background execution alone does not complete the work.
- Do not build a competing dispatcher or task database. Reuse existing validators;
  do not rebuild the benchmark harness or repeat A/B runs for routine assets.
  Track native input, cache and output separately.
- Optimize for a verified result including rework. Use Astra for difficult work;
  use other models when appropriate and available. All project executors and
  reviewers must use **max reasoning**, at standard speed, per the
  [standing owner instruction](Docs/Approvals/WorkerReviewerMax01.json).
  Verify both configured profiles/native arguments and actual execution settings;
  a profile label alone is insufficient. Restore task-local settings afterward
  without reverting this standing max requirement to an older saved level.
- Delegate bounded independent tasks with focused context and concise findings;
  save full logs under `Saved/`.
- One writer per running Unreal/Blender/Substance instance, coordinated for the
  entire editing operation. Run one memory-heavy build, bake, render or local
  model workload at a time until measurements justify more.
- Prefer official Epic MCP for Unreal editor operations: `unreal_epic` at
  `http://127.0.0.1:8000/mcp`. Discover toolsets on demand and confirm the project
  and live editor state before mutations. Rider's code/debug connection is separate.
- Check installed versions and actual capabilities before using any DCC bridge;
  configuration alone is not evidence of a working connection.

## Acceptance and sources

- Define acceptance criteria, make a bounded change and verify it. Repeat failed
  actions only with new evidence; after two equivalent failures change the
  diagnostic approach. Avoid redundant passing tests.
- Follow [review responsibilities](Docs/AgentDevelopment.md#review-responsibilities):
  the executor implements and self-checks; one primary independent reviewer owns
  technical review for substantive changes; the controller accepts owner scope,
  evidence applicability and finding closure without a second full technical review.
  Assign additional reviewers distinct criteria only. Reuse applicable passing
  evidence; repeat checks only for a recorded change, gap, contradiction or uncovered
  risk, limited to affected criteria. Small obvious low-impact changes may use
  executor self-checks and controller acceptance unless independent review is
  explicitly required. Preserve visual and owner gates. See the
  [owner decision](Docs/Approvals/ReviewResponsibilities01.json).
- For animation and gameplay corrections, verify only behavior directly affected
  by the change and its related transitions. Do not run the full animation or
  feature matrix. This is a standing owner instruction for future tasks; see
  [focused verification](Docs/Approvals/FocusedVerification01.json).
- For variant sets requested for owner experimentation, verify the requested set
  renders and shared functionality works on one representative instance. Leave
  subjective comparison to the owner; do not run a per-variant matrix or independent
  visual comparison unless requested or a concrete distinct defect needs a bounded
  check. See [owner variant testing](Docs/Approvals/OwnerVariantTesting01.json).
- Before environment layout or model production, create a separate concept-art
  task and obtain explicit owner approval of an identified art version. Environment
  preproduction requires dimensioned plans/sections with human scale, approved as
  a named package before renewed 3D work. Preserve approved scale and label proposed
  dimensional changes for owner review.
- Follow [visual acceptance](Docs/VisualAcceptance.md) within current scope.
  Independent visual reviewers inspect actual art and comparable views, subject
  to the explicit protagonist concept exception above. Technical validation,
  independent review and owner visual acceptance are distinct; prototype acceptance
  or a request for the next task does not itself approve a visual design.
- Use [GameBrief](Docs/Design/GameBrief.md) for game/level requirements and also
  [StoryCanon](Docs/Design/StoryCanon.md) for narrative work. Keep fixed facts,
  working proposals and unresolved details separate. The documented first playable
  is the [lobby walkthrough](Docs/Tasks/OpeningLobby.md); its environment backlog
  remains subject to the owner's current deferral.
- For the original protagonist and FP arms, read the [task plan](Docs/Tasks/PlayerCharacter01Plan.md),
  [task index](Docs/Tasks/PlayerCharacter01Tasks.md) and [AI3D pipeline](Docs/PlayerCharacter01AI3DPipeline.md).
  Use `Assets/Source/PlayerCharacter01/` as the canonical editable source root.
  Preserve all concept packages and owner experiments; named approval is required
  before production modeling, including when a concept is used as a planning example.
- For material authoring, read the verified [native Painter workflow](Docs/PainterWorkflow.md).
  Preserve editable native sources; do not reuse rejected texture pixels or wrap
  them in a ceremonial Painter project.
- Asset metadata belongs in the separate local PostgreSQL database `meridian_assets`.
  Use register/inspect/validate from [AssetRegistry](Docs/AssetRegistry.md), preserving
  accepted fingerprints and relationship uncertainty. Registration is not acceptance
  of changed asset bytes. See [registry acceptance](Docs/AssetRegistryAcceptance.md)
  and [agent development](Docs/AgentDevelopment.md) for evidence and tooling details.

## Maintaining these instructions

- Keep this file to durable rules and a small navigation index. Update the dated
  `Docs/ProjectState.md` snapshot when active scope changes; put task detail in
  `Docs/Tasks/` and exact owner decisions in `Docs/Approvals/`.
- Preserve historical evidence unchanged; clearly identify superseded directions
  in the current summary instead of appending a running diary here. Multica remains
  the source of live task state, not the summary or archived instructions.
- The [pre-compaction archive](Docs/Archive/AgentInstructions/README.md) preserves
  the original instructions exactly. Consult it only for relevant historical
  context; its old "current", "latest" and dispatch wording is not active authority.
