# EnemyCombat01 controller acceptance

Date: 2026-09-23. Task: **MSQ-70**. Delivery: **Candidate01/build03**.

Accepted for the owner's testing under the
[direct implementation and testing decision](Approvals/EnemyCombat01-OwnerStart02.json).
Native build, source review, candidate identity and preservation pass. Runtime
gameplay, navigation, physical handover, visual quality and performance remain
pending owner testing. No Multica task execution or status change was performed.

## Scope and evidence

The [handoff](EnemyCombat01.md) implements one autonomous opponent on the retained
GASP/Mover and GASPALS armed foundation, with sight, bounded pursuit/search/return,
finite-flight bursts, magazine/reload state and physical recovery/death/reset
handover. The three original passive profiles remain available by console command.
Player point-damage counters and HUD feedback prepare MSQ-71 without player
health/death. Weapon/hand state prepares MSQ-99/100 without implementing those tasks.

The [sole independent source review](EnemyCombat01Review.md) closes EC70-R1's
potential endless close-cover Aim/Pursue cycle through a persistent obstruction
budget. The controller accepts that source review and the executor's applicable
build evidence without a second full technical review or gameplay runs.
`Saved/CombatSlice01/EnemyCombat01/build03.log` reports Development Editor success
on UE 5.8.3 in 9.37 seconds. The final correction is included in that build.

`editor-after.json` reports the retained lobby, stopped Play and no dirty packages.
`editor-load-check.json` records an empty targeted load-error scan for the final
ordinary editor launch. This is editor-load evidence, not gameplay acceptance.
The owner controls and limits are in the implementation handoff. Local navigation
covers one bounded floor layer; reserve is unlimited, reload uses Ready pose and
enemy cadence is frame-quantized without catch-up.

## Identity and preservation

Candidate manifest SHA256:
`819c58d5f9faf218c6667cc22d5887ee284ae4de2343e4c88dd8aa570843438b`.
Controller checks match all 14 native source/build files and the resulting DLL.
The pre-existing owner config, project descriptor and lobby-map hashes also match.
Evidence: `Saved/CombatSlice01/EnemyCombat01/Controller/identity-acceptance.json`.
The source baseline was commit `e45fbfd0ffbb7e67959e98d86b6451a3182b1dab`.

No content packages, asset sources, historical evidence or immutable candidate
manifests were changed. Generated logs, identity records and temporary editor
lifecycle tools remain under Saved. The closure commit excludes the owner's
pre-existing `Config/DefaultEngine.ini` and `MeridianSquad.uproject` modifications.

## Execution

One production writer owned native code, editor lifecycle and build. One
independent reviewer inspected source and existing evidence only. Native turn
contexts verify Astra/max for both; no fast override was requested. The native
contexts do not expose a response service tier. See
`Controller/execution-settings.json` under the task evidence root.

No agent Play, automated gameplay input, shots, recordings, screenshots or runtime
acceptance matrix were executed. MSQ-71 onward, MSQ-93 through MSQ-96 and
MSQ-99/100 are not started by this delivery. The controller owns the local
task-scoped closure commit and final owner handoff.
