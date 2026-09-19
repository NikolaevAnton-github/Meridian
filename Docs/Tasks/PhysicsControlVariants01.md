# PhysicsControlVariants01: six stronger reactions and relative player slowdown

Prepared 2026-09-19. Multica issue: **MSQ-85**. Authorized follow-up to verified MSQ-84 under
[the exact owner instruction](../Approvals/PhysicsControlVariants01-OwnerScope01.json).
This is one unstaged child of CombatSlice01 / MSQ-67, preceding any MSQ-70 dispatch.

## Later owner instruction: narrowed verification

[OwnerVariantTesting01](../Approvals/OwnerVariantTesting01.json) supersedes the
verification/review campaign below. The owner will compare the six reactions.
Check only that six mannequins render and one receives real rifle hits. Stop the
per-profile, limb/death/joint/performance and independent visual-review campaign.
Reuse the successful build and applicable existing timing evidence. The active
executor run and reviewer were stopped; the controller owns the bounded smoke,
documentation and commit. The original criteria below remain historical task
context, not an active execution queue or prerequisite to this owner play handoff.

Candidate04 is handed off under this narrowed acceptance. See
[implementation and controls](../PhysicsControlVariants01.md). The owner-opened
PIE session was preserved; no full independent candidate verdict is claimed.

## Authorized outcome

The owner likes and adopts the Physics Control prototype. Replace the active
old-enemy/one-dummy comparison with exactly six numbered Physics Control Manny
fixtures, offering increasing and visibly different hit reactions. Remove the
legacy enemy from active spawning/reset paths, preserving all original code,
assets and evidence. Preserve the retained lobby and purchased rifle presentation.

During the Y slowdown preview, player movement AND rifle shot cadence must slow
somewhat, while bodies, environment and all bullets slow substantially more.
Initial adjustable values: world/body/all-bullet scale 0.25; player movement and
firing scale 0.65. At normal time all use their original rate. These are controller
tuning defaults, not exact owner-selected numbers. Keep full stop out of this task;
its previous policy remains until the later MSQ-75 ability work.

## Implementation boundaries

- One existing Multica Unreal executor owns implementation, native builds and all
  editor writes. Read ProjectState, this task, its owner decision and the MSQ-84
  handoff. Use Astra/max/standard, fast mode disabled, concurrency one. Reconfirm
  the live project, retained map, PIE and dirty packages through official Epic MCP.
- Six transient mannequins, total, with consistent readable labels 1 through 6.
  Choose reachable, clearly separated firing positions using existing open floor;
  no lobby changes and no automatic spatial redesign. Record positions and each
  profile's actual impulse/drive/softening/recovery values. All use the same health
  and rifle damage for meaningful comparison. Keep F6 reset without ammo refill;
  F10 may toggle the entire fixture set, with exact-six recreation and restoration.
  Retire the inactive old-enemy F7 preview cleanly and document its disposition.
- The former living torso/limb response is too weak. Tune six profiles from clearly
  stronger through pronounced physical reactions; a set of nearly identical tiny
  twitches does not meet the request. Use bounded impulses AND appropriate motor
  compliance/recovery rather than unsafe force escalation. Demonstrate a matched
  living torso hit for all six and limb hits on representative low/high profiles.
  Record an objective local response metric alongside actual ordinary-speed video.
  Ordered measured response should support the visibly increasing profile labels;
  choose justified numerical tolerances before claiming pass. Preserve stable idle,
  finite recovery, joints, death continuity, corpse hits and sleep/wake.
  Inspect effective clamps (old 0.2 softening, 0.6 s recovery and 300 cm/s impulse
  velocity limits); authored values alone must not collapse to identical profiles.
- Keep one authoritative finite-flight shot/contact/damage path. Multiple fixtures
  require nearest-contact selection, no duplicate impulses/damage and independent
  health/state. Six mannequins must not share mutable reaction/history state.
- Separate player action time from the compensated projectile-manager clock. Shot
  births and residual flight must remain consistent when entering/exiting slowdown,
  without overdue-shot bursts or lost/duplicate ammo. The normal 85 ms schedule is
  retained; a 0.65 player firing rate implies about 130.77 ms per shot in real time.
  All bullets including player-fired ones use 0.25 world speed during preview.
  Audit the purchased animation notify/reload timing seam; keep presentation and
  gameplay coherent under the declared player clock, with no double scaling.
- Restore saved player/world/projectile/animation overrides on Y exit, F6, fixture
  disable and EndPlay. Repeated toggles do not compound scales. Mouse look should
  remain usable. Do not implement ability cost/UI, full stop, AI, balance/get-up,
  new art, Mover migration, new weapon mechanics or deferred lobby work.

## Focused acceptance and review ownership

The sole primary independent reviewer is
`/root/physics_variants_primary_review` at Astra/max/standard. It owns technical
and actual gameplay visual review for all rows below. Executor self-checks first;
controller accepts scope, applicability and closure without a duplicate full review.

| Criterion | Evidence |
| --- | --- |
| Active adoption and six fixtures | Fresh retained-lobby PIE has exactly six numbered Physics Control actors and zero legacy enemy. Clear playable placement, independent health, F6 and F10 exact counts, no actor/controller leaks. Original source/assets preserved. |
| Useful reaction comparison | Comparable living torso-hit/settling clips for all six at normal speed, actual profile values and measured local displacement/rotation. Reactions visibly stronger than old weak behavior, meaningfully ordered/distinguishable, with representative arm/leg low/high checks and stable recovery. Strongest profile has no explosions or sustained jitter. |
| Contacts and death | Focused multi-target nearest-hit/occlusion and one-hit/one-impulse checks. Representative low/high impulse-extreme death/falling and settled corpse hits preserve one death, drive release and wake. Reuse unchanged MSQ-84 history/zero-scale evidence where applicable. |
| Relative slowdown | Actual movement and sustained-fire cadence measurements at normal and 0.25-world/0.65-player preview; actual bullet/body slowdown. Quantify wall vs simulation clocks; do not claim old grounded-trajectory discrepancy fixed. Toggle while firing/reloading, verify no burst/duplication or ammo commit leak and one slowed low-FPS interval. |
| Reset, restoration and cost | Y exit, F6, F10, fresh PIE/teardown restore all saved overrides; F6 leaves ammo unchanged. Bounded six-fixture performance sample and incremental disk growth, not a new benchmark suite. |
| Candidate and preservation | Appropriate native build/fresh load, exact candidate identity, actual comparable visual evidence, unchanged owner config/map/assets and historical candidates. Leave retained lobby ready for Play. |

Reuse existing probes, transports and foreground capture tools. Run only affected
checks and related transitions. Choose acceptance metrics before checking; preserve
failed candidates. Do not fabricate a pass from executor text or slowed playback.

Deliver `Docs/PhysicsControlVariants01.md`, concise tuning/control/limits tables,
changed-file list and candidate evidence under
`Saved/CombatSlice01/PhysicsControlVariants01/Worker/`. Full logs stay in Saved.
Workers do not commit, alter profiles/status/registry, or dispatch successors.
Controller owns task administration and verified task-scoped local closure commit.
