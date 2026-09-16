# LobbyFunctional-Revision01: reviewed drawing handoff

**LobbyFunctional-Revision01 / Candidate01 passed independent visual and technical
review. No required correction remains. The identified 2D package awaits the
owner's approval before a separate 3D task.**

The owner walked through the ReworkA01 neutral lobby and requested the bounded
changes recorded in [Walkthrough01](Approvals/LobbyArchitectureReworkA01-Walkthrough01.json).
MSQ-16 prepared the focused proposal; fresh MSQ-17 independently reviewed the
actual references and all candidate images before designer conclusions. Both
used Astra/high/standard, existing subscription authentication and concurrency one.

## Drawing package

- [Whole plan and circulation](../Assets/Concepts/OpeningLobby/FunctionalRevision01/01-plan-circulation.png)
- [Entrance checkpoint](../Assets/Concepts/OpeningLobby/FunctionalRevision01/02-entrance-checkpoint.png)
- [Elevator and opaque inner wall](../Assets/Concepts/OpeningLobby/FunctionalRevision01/03-inner-elevator.png)
- [Four room-face arrangements](../Assets/Concepts/OpeningLobby/FunctionalRevision01/04-room-faces.png)
- [Entrance, inner end and whole-hall spatial drawings](../Assets/Concepts/OpeningLobby/FunctionalRevision01/05-spatial-context.png)
- [Dimensions, deltas and reproduction](../Assets/Concepts/OpeningLobby/FunctionalRevision01/README.md)
- [Independent verdict](OpeningLobbyFunctionalRevision01Review.json) and
  [complete review](../Saved/OpeningLobby/FunctionalRevision01/Review01/report.md)

Four terminal colonnade infills preserve the 60 x 24 x 18 m hall, six pier pairs,
11.2 m central width and 4 m longitudinal aisles. Inner-end closed doors face the
hall; entrance service doors face the aisles. Reverse faces are blind. Doors are
proposed at 1.2 x 2.4 m with 0.24 m recess. Enclosures occupy the 2.4 m column
band and close to the beam underside; usable interiors and stair fit are deferred.

The entrance checkpoint spans the central 11.2 m passage, with two opposite-side
1.5 x 2.4 m net lanes and a joined low central body. The 3.6 x 4.2 m elevator
opening has a 0.6 m reveal. The inner high window and its grid are replaced by
an opaque wall, with an annotated 6 x 6 m future sign reservation. No name/logo
or cab/shaft is designed. Old terminal crossovers X +/-27 are deliberately closed;
the adjacent open bays provide alternative crossings at X +/-16.8.

## Verified identity and limits

Manifest: Assets/Concepts/OpeningLobby/FunctionalRevision01/manifest.json.
SHA-256: `c7828c0bfdebd05705d2a47194b10bd44db437b2c02adc80971d82166c3196eb`. All 29 entries match. Candidate
README/footers retain their immutable pre-review status; this external report
records the later independent PASS without modifying reviewed bytes.

Review confirmed 201 technical checks, 11 analytic route polylines / 9,865 samples,
96 reproduced source bounds and all 347 protected baseline files. Text and actual
image inspection passed after the author's in-run drawing corrections. Routes are
2D calculations, not in-engine movement or collision evidence. New drawing/source
and worker evidence total approximately 12.8 MB, including retained temporary
browser data. No candidate correction run was required after independent review.

Unreal remains on /Game/Maps/L_OpeningLobby_ArchitectureReworkA01, PIE stopped and
no dirty packages, confirmed through official Epic MCP. Its saved hash remains
`71cfc087c80510313054255d784d1b43c45395d6400c9e0b75e9f64d7be944d0`.
No 3D production, default-map/config changes, registry updates, commits or pushes
were performed. Designer/reviewer profiles were restored; no run remains active.

Native MSQ-16/17 usage, excluding controller/helpers: 221,667
uncached input, 2,492,032 cached input, 35,528
output. Reasoning is 4,992 of that output, counted
once. Full evidence is in Saved/OpeningLobby/FunctionalRevision01/Controller/.

The concrete owner gate is approval of this named package and its new dimensions,
central-only checkpoint with open side aisles, deliberate crossover closures and
opaque sign reservation. No optional clarification reply was received during
preparation, so central-only remains the stated proposal, not a confirmed owner
choice. A later owner response supersedes that assumption. MSQ-16 remains in
review; MSQ-17 is done; full materials/atmosphere and milestone acceptance remain
pending. Follow [the task](Tasks/OpeningLobbyFunctionalRevision01.md).
