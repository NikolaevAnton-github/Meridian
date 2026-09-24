# EnvironmentDestruction01 task preparation

Date: 2026-09-24. Parent: MSQ-74. Authority:
[copied-lobby owner request](Approvals/EnvironmentDestruction01-LobbyLab01.json).
Plan and child routes: [EnvironmentDestruction01Plan](Tasks/EnvironmentDestruction01Plan.md).

Created MSQ-140..147 as eight sequential children, ED-00..07. Before first dispatch,
all eight were verified backlog, unassigned, zero runs, with the correct parent,
stages and normalized description content. Dependencies follow the child sequence.
MSQ-74's old MSQ-72 prerequisite was replaced with delivered rifle foundations
MSQ-68/MSQ-82. Parent/AI plans and live descriptions record destruction-first order;
MSQ-131 still waits for actual new AI cover/navigation and destruction evidence.
No earlier task or accepted candidate was relabelled as newly complete.

The owner authorizes ED-00 copy/baseline now. Other children remain prepared without
automatic dispatch. Source map, owner configuration and shared assets are preserved;
no new structural destruction, art selection or general lobby reopening is implied.

Primary planning technical review by `destruction_performance` found three bounded
gaps: affected slow-time physics/lifetime checks, applicability of final effects to
dense-scene cost claims, and blocking technical findings at final handoff. The plan,
ED-06 and ED-07 now explicitly close these wording gaps. Final review confirmation
is recorded with controller evidence before dispatch.

Preparation evidence: `Saved/EnvironmentDestruction01/TaskSetup01/`. Original live
issues and preservation hashes are retained there. Source lobby, DefaultEngine.ini
and .uproject matched their before hashes at preparation verification. The latter
two already contained owner edits and are excluded from controller task commits.
Context guard passed at 7,404 combined AGENTS/ProjectState bytes.

Performance guidance is a measurement plan, not measured game performance. Local
hardware observed: Ryzen 7 9800X3D / RTX 5090. Record actual runtime settings and
separate intact, breaking and settled states; do not promise a universal fragment
count or FPS. CPU rigid-body cost, GPU effects/rendering and memory all matter.

Primary documentation consulted:
- [Epic destruction overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/destruction-overview)
- [Epic Niagara scalability](https://dev.epicgames.com/documentation/unreal-engine/scalability-and-best-practices-for-niagara)
- [Epic measuring Niagara](https://dev.epicgames.com/documentation/en-us/unreal-engine/measuring-performance-in-niagara)
- [Epic Chaos optimization, documented 5.6 controls to verify on installed 5.8](https://dev.epicgames.com/documentation/unreal-engine/chaos-destruction-optimization?application_version=5.6)
