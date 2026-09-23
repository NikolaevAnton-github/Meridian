# GASPALSUE58Trial01: separate UE 5.8 owner trial

Date: 2026-09-23. Direct execution outside Multica under the
[owner request](Approvals/GASPALSUE58Trial01-OwnerScope01.json).

Later follow-up: the [Tripo model attempt](TripoCharacter01ChatHandoff.md) was
stopped and rejected by the owner for excessive deformation. Its model assets
were discarded at the owner's request; the original trial setup below remains.

## Delivery

The separate project is `D:/devgames/GASPALS_UE58/GASPALS.uproject`.
Its launcher is `D:/devgames/GASPALS_UE58/Open_GASPALS_UE58.cmd` and its local
usage guide is `D:/devgames/GASPALS_UE58/TRIAL_UE58.md`.
The editor is open on `/GASPALS/Levels/DefaultLevel`, with Play stopped and ready
for the owner's trial. Click Play, then click the game viewport.

This prepares an experiment only. It does not migrate GASPALS into MeridianSquad,
approve its motion/visual design, or dispatch a gameplay backlog task.

## Provenance and change

[PolygonHive/GASPALS](https://github.com/PolygonHive/GASPALS) was cloned with one
commit of history into the separate directory. The pinned upstream commit is
`a6d3812545063f0954b4b80d632848f2eb8032e2`, retained in the local repository.
The upstream project targets UE 5.7; no upstream 5.8 release/branch was identified.
Its 2,105 source files total 2,025,335,997 bytes. Source and the UE-Only license
statement remain preserved. The content is directly stored in upstream Git;
there are no submodules or required external LFS downloads.

Installed engine verification reads `D:/UE_5.8/Engine/Build/Build.version`:
**UE 5.8.3, CL 58210709**, compatible CL 55116800. This supersedes older local
tooling documents' 5.8.1 version for this trial only.

The local `trial/ue58` branch changes the engine association, enables editor-only
Epic MCP/EditorToolset/Python inspection, configures loopback MCP port 8000,
and adds the launcher, usage guide and empty root Content directory. No gameplay
logic or binary assets were modified or resaved. No native C++ build is required
for this content-only project; engine load and PIE perform the applicable
Blueprint validation.

## Focused verification

| Criterion | Result and evidence |
| --- | --- |
| Correct isolated project and engine | Process 10376 launched the separate `.uproject` in installed UE 5.8.3; engine version and source identity recorded. |
| Default map opens and renders | Official Epic MCP returns `/GASPALS/Levels/DefaultLevel`; `editor-0.png` shows the supplied test environment. |
| Play starts with its character | `play.json` reports active PIE; `possessed-0.png` shows the rendered orange character responding to crouch input. |
| Basic input and physical transition | Native keyboard C toggles crouch/stand; X produces ragdoll and the next X completes get-up. `ragdoll-0.png` and `recovered-0.png` show the resulting states. |
| Play stops cleanly | `stop.json` reports false; final `state.json` reports the default editor map and PIE false. |
| No blocking compile/runtime failures | Checked editor log has no Blueprint compile errors, fatal errors, ensures or Blueprint runtime errors. The warnings below remain. |
| Preservation and storage | Original owner config/project hashes and the existing GameAnimationSample descriptor are checked against the initial snapshot. Trial source and local changes are isolated. |

Evidence lives under `Saved/Experiments/GASPALSUE58Trial01/`: source identity,
upstream tree, preservation manifests, focused state responses, editor log and
screenshots. `Scripts/GASPALSUE58Trial01/probe.py` reuses the existing official
Epic MCP client. This is a bounded task probe, not a new benchmark harness.

`play-0.png` is an editor-camera capture taken during PIE and does not prove
the playable camera. The later possessed/ragdoll/recovered captures provide
the gameplay evidence. An initial editor capture failed while the window was
not active; activating the returned GASPALS window resolved capture. The scene
tool returns an empty level while the possessed PIE viewport has focus; process
identity and the initial default-map check established the stop target.

## Retained warnings and limits

- `CBP_SandboxCharacter` uses deprecated `ActivatePersistentGlobalCameraRig` and
  `ActivatePersistentBaseCameraRig` calls. The checked default third-person view
  works; other camera modes were not verified.
- Play logs an index-0 access to empty `CharactersSkeletalMeshes` during spawn.
  The default orange character remains playable for the checked actions;
  character switching is not validated.
- The first launch reported the absent empty root `Content/` directory. It now
  exists with `.gitkeep`; plugin content was present throughout.
- No full locomotion/traversal/overlay matrix, performance certification,
  packaging or multiplayer validation was performed. Owner motion/play judgement
  remains separate. The controls listed in the trial guide are upstream labels,
  not claims that every mode was tested.

At the initial inventory, the existing `D:/devgames` project/tool roots occupied
about 120.427 GiB. The new trial occupied 2.658 GiB after the smoke check, including
its local Git data and generated files; this fits the standing 250 GB cap.

## Execution and closure

The controller prepared and checked the project directly. A native subagent,
requested with max reasoning, independently researched the upstream source and
requirements without editing files. The delivered change is limited to project
setup and documentation with untouched upstream gameplay/assets; the small,
low-impact self-check/controller route from
[review responsibilities](AgentDevelopment.md#review-responsibilities) applies.
No Multica task, runtime or dispatcher was created or started.

The trial repository is committed as
`7a62ee63977298d5d5fb0193959b26e058aa3130` on `trial/ue58` and its working tree is
clean. The MeridianSquad task-scoped documentation/probe commit is made before
owner handoff. Existing owner changes to `Config/DefaultEngine.ini` and
`MeridianSquad.uproject` are excluded from that closure commit; all three recorded
preservation hashes match the initial snapshot. The final verification summary
is `Saved/Experiments/GASPALSUE58Trial01/verification.json`.
