# Subsystem routes

Open only the map relevant to the current task. These maps identify source entry
points and contracts; they are not an additional startup reading list or task queue.
Current direction and authority remain in [ProjectState](../ProjectState.md).

| Work | Map |
| --- | --- |
| Enemy decisions, senses, action ownership | [AI](AI.md) |
| Paths, spatial queries and movement commands | [Navigation](Navigation.md) |
| Rifle, reload, projectiles and world time | [Weapons](Weapons.md) |
| GASPALS locomotion, aim pose and physical reactions | [Animation](Animation.md) |

Keep maps short, with actual entrypoints, invariants and focused check routes.
Update affected paths/contracts when implementation changes. A source path in a
historical handoff does not prove it is still active. Read the selected source and
applicable decision before a change; follow only the dependencies needed for it.
