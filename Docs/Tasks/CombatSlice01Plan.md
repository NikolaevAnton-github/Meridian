# CombatSlice01: sequential combat and opening episode plan

Prepared 2026-09-18 from the owner's request to prepare tasks for the proposed
gameplay progression and proceed sequentially. See the
[exact task-creation record](../Approvals/CombatSlice01-TaskCreation01.json).

Multica issue: **MSQ-67**.

The MSQ-68 execution instruction authorized that child and fixed the
[projectile/time/self-hit policy](../Approvals/CombatFoundation01-OwnerScope01.json).
All bullets have finite flight and follow world slowdown/stop; player movement
remains normal and own bullets can injure the player. Build these seams in stage 1;
player health and the ability remain in their later stages. The original task
creation record and setup evidence remain historical, unchanged.

Stage 1 implementation and bounded corrections are verified on 2026-09-19; see
[CombatFoundation01 controller review](../CombatFoundation01Review.md).
MSQ-69 and successors remain undispatched. This parent remains coordination for
the unfinished stages; it is not a request to start the whole family.

On 2026-09-19 the owner requested **MSQ-82 / CombatTiming01 next**, immediately
after MSQ-68 and before MSQ-69. See the [exact order decision](../Approvals/CombatTiming01-NextTask01.json).
The inserted stage 2 addresses the remaining FPS-dependent firing limit and
correct per-bullet timing. Stages 3-15 retain the former relative order, and
MSQ-69 depends on MSQ-82. Task preparation creates no new production run.

## Outcome and starting point

Build a reviewable first combat slice in the retained lobby, followed by a
bounded opening episode: meaningful rifle fire, enemies and player survival,
a short encounter, body/environment damage, three abilities, and local narrative
interaction. This is the first representative implementation of the product
goals, not completion of full-game AI, extensive destruction or a whole mission.

Read [ProjectState](../ProjectState.md), [GameBrief](../Design/GameBrief.md),
the relevant child task and its prerequisite handoff. Read
[StoryCanon](../Design/StoryCanon.md) for episode work. The original starting
baseline was PurchasedArms02 with PurchasedArms03-06 corrections. Verified
MSQ-68 now adds finite-flight damage, ammunition and reload accounting. MSQ-82
refines their timing before enemy work. Player health and abilities remain later
stages; other vendor gestures are not working mechanics.

## Ordered tasks

Multica owns live status. This table defines order and scope, not a parallel
task database. Every child has a unique native stage and a recorded predecessor.

| Stage | Multica | Task | Reviewable result |
| --- | --- | --- | --- |
| 1 | MSQ-68 | [CombatFoundation01](CombatFoundation01.md) | Rifle hits, damageable target and real ammunition/reloads. |
| 2 | MSQ-82 | [CombatTiming01](CombatTiming01.md) | Stable firing cadence and correctly timed bullets across FPS changes and bounded hitches. |
| 3 | MSQ-69 | [EnemyPrototype01](EnemyPrototype01.md) | Audited reusable enemy prototype, rig and damage-region contract. |
| 4 | MSQ-70 | [EnemyCombat01](EnemyCombat01.md) | One enemy senses, moves, shoots, reacts and dies. |
| 5 | MSQ-71 | [PlayerSurvival01](PlayerSurvival01.md) | Player health, death and reliable fight restart. |
| 6 | MSQ-72 | [LobbyEncounter01](LobbyEncounter01.md) | A small encounter with cover, completion and reset. |
| 7 | MSQ-73 | [EnemyBodyDamage01](EnemyBodyDamage01.md) | A bounded regional damage and dismemberment sample. |
| 8 | MSQ-74 | [EnvironmentDestruction01](EnvironmentDestruction01.md) | Selected destructible objects with correct cover and debris behavior. |
| 9 | MSQ-75 | [TimeSlow01](TimeSlow01.md) | World slowdown/stop, normal player movement and reliable restoration. |
| 10 | MSQ-76 | [ForcePush01](ForcePush01.md) | Directional push with explicit eligibility and recovery. |
| 11 | MSQ-77 | [Telekinesis01](Telekinesis01.md) | Acquire, hold, release and throw suitable objects. |
| 12 | MSQ-78 | [CombatIntegration01](CombatIntegration01.md) | The encounter works with damage, destruction and abilities together. |
| 13 | MSQ-79 | [OpeningEpisodeDesign01](OpeningEpisodeDesign01.md) | Named beat sheet, route and surveillance storyboard for owner selection. |
| 14 | MSQ-80 | [OpeningEpisode01](OpeningEpisode01.md) | The selected exploration, combat, recording and progression sequence. |
| 15 | MSQ-81 | [GameplaySliceReview01](GameplaySliceReview01.md) | Independent integrated review and owner-ready playable handoff. |

## Sequential execution and gates

- The original setup prepared tasks only. It created the parent and all children as
  **backlog, unassigned**, with no production run. The parent is a coordination
  issue, not a worker instruction to execute the whole plan.
- Native stages and `metadata.depends_on` describe the sequence; the installed
  Multica version does not enforce a dependency scheduler. The controller checks
  the predecessor's evidence and closure before explicitly dispatching the next
  task within the owner's authorized execution scope. Do not build another
  dispatcher or start the entire family from the parent.
- Use the existing project in place, production concurrency one, one editor
  writer and one heavy workload at a time. Use Astra for difficult work; all
  executors and reviewers use **max reasoning, standard speed**. Verify saved
  profiles, native arguments and actual execution. Restore task-local settings
  while retaining the standing max requirement.
- A technical task advances after focused checks, controller review, bounded
  corrections and a local task-scoped closure commit. Owner play feedback and
  visual acceptance remain separate; technical success never invents acceptance.
  Do not introduce an owner approval step for each routine implementation choice.
- Concrete owner decisions are needed where the existing rules require them:
  new art/model production and architectural changes; unavailable asset/budget
  choices; and unresolved story staging in the named episode design package.
  Prepare reviewable evidence before presenting such a decision.
- Prototype balance, ranges, health, damage and ability costs are configurable
  working values, not fixed canon. Record the chosen values and reasoning in
  handoffs. Keep the user's established movement/ADS feel unless directly
  affected behavior requires a documented bounded adjustment.

## Shared preservation and implementation constraints

- Retain `/Game/Maps/L_OpeningLobby_PainterStone01`, its dimensions, owner edits,
  material bindings, lighting and atmosphere. Use removable gameplay actors and
  bounded rollback snapshots. No duplicate Unreal checkout, replacement lobby,
  vendor arena, renewed architecture, glass-refinement or original-protagonist
  production is part of this plan. Keep bodyless purchased arms shadowless.
- Reuse audited existing assets where suitable. Do not assume purchased FP arms
  provide an enemy body. Enemy and destruction tasks must establish editable
  sources, usage rights, compatibility and limits. Built-in primitive debug actors
  may prove mechanics but cannot establish final enemy art or body-damage quality.
  Reuse may include bounded technical adaptation under the selected asset contract;
  a source need not already have separable limbs or a native DCC project.
  No purchases, paid APIs,
  top-ups or implicit extension of the protagonist AI3D allowance. New model
  production requires its own identified concept and required owner approval.
- Preserve accepted assets, rejected candidates, archived sources and exact
  evidence. Native source art belongs with project asset sources; register new
  accepted assets through the existing registry workflow without silently
  replacing accepted fingerprints. Keep binaries in Git LFS and generated
  evidence outside Git. Measure growth within the total 250 GB project cap.
- Confirm the live project, map, PIE and dirty packages through official Epic
  MCP before editor changes. Coordinate with any owner session; never discard
  its unsaved changes. Verify installed capabilities when a bridge is needed.
- Keep one authoritative shot/damage/ammunition path, and document how paired
  animation notifies commit gameplay changes. Traces and physics use gameplay
  world coordinates, not the scaled first-person presentation. Avoid duplicate
  events, unbounded actor spawning and permanent map damage during playtests.
  Rifle bullets use finite-flight simulation with swept collision, world-time
  motion/aging and collision-time damage. Preserve normal player movement during
  future slowdown/stop, contact with suspended bullets and self-hit eligibility;
  shooter attribution is not permanent immunity. See the fixed owner policy above.
- Audit current bindings before adding abilities or interactions: Q/E/F/X/T/U/G
  already trigger vendor actions. Document intended remaps in a single controls
  table. Do not silently remove unrelated functioning controls or imply demo
  melee, grenades, syringe or interaction gestures are complete systems.
- Windows single-player prototype only. Multiplayer, inventory/loot systems,
  new weapons, progression trees, full save games and a packaged release are
  outside this slice unless separately requested.

## Evidence and acceptance

Each task produces `Docs/<TaskName>.md` with baseline, exact changes, controls,
configurable values, focused results, sources, disk growth and remaining limits.
Keep full logs, comparisons, captures and rollback under
`Saved/CombatSlice01/<TaskName>/`. Reviewers inspect actual comparable gameplay
views for visual claims and report independently without editing the candidate.

Follow [FocusedVerification01](../Approvals/FocusedVerification01.json): test
changed behavior and related transitions only. Use appropriate compile/load and
saved-package checks, but no repeated full animation matrix or new benchmark
harness. Explicit integration tasks exercise only newly coupled risks. On a
failed check, diagnose with new evidence; after two equivalent failures change
the approach. After controller closure, commit only verified task files with the
Multica ID before owner handoff. Leave the retained lobby ready for Play with no
unsaved task edits, while preserving owner-owned state.

The final review distinguishes: implemented prototype mechanics, technical
verification, independent visual/gameplay findings, and owner acceptance. The
parent cannot be closed merely because this task family has been created.
