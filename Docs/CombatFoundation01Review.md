# CombatFoundation01 / MSQ-68 controller review

Reviewed 2026-09-19. The scoped implementation and bounded projectile corrections
pass technical/controller and independent review. The retained lobby loads in a
fresh controller-owned editor, with stopped PIE, clean packages and no leaked
prototype actors. Owner play and visual acceptance remain separate. No successor
is authorized by this review.

The [implementation report](CombatFoundation01.md) gives controls, tuning and
evidence paths. Scope follows the [task](Tasks/CombatFoundation01.md) and
[exact owner decision](Approvals/CombatFoundation01-OwnerScope01.json). The rifle
now has finite-flight swept bullets, collision-time damage, finite magazine and
reserve accounting, one validated reload transfer, resettable prototype targets,
and bounded hit feedback. PurchasedArms06 presentation remains the baseline.

## Verification and corrections

Evidence is under `Saved/CombatSlice01/CombatFoundation01/`, with `Worker/`
for implementation/runtime records and `Controller/` for independent reviews
and controller checks. Initial verification passed 138 assertions over 14,387
samples, followed by 957 samples for the smaller impact appearance. These records
cover ammunition, R/Q/E reload variants and interruption, dry fire, near/thin
cover, capacity, reset/expiry, movement, ADS and airborne firing. They were not
replaced by an unrelated full animation matrix.

The independent early source review found three concrete projectile defects.
One bounded Multica correction run addressed all three:

- Damage callbacks now run after the bullet query loop. Reset generations cancel
  pending delivery safely; callback-created bullets wait until the next step.
  The focused listener-reset test conserves five launches as three hits and two
  retirements, with no obsolete-array access or stale damage delivery.
- New bullets sample character capsules at their own birth. Backward movement
  before launch cannot produce a retroactive self-hit, while older suspended
  bullets retain their movement history and later genuine re-entry hits once.
- All collision queries finish before callbacks can remove a shared obstruction.
  Both bullet insertion orders preserve the rear target behind a one-hit front
  target. This is a conservative simultaneous-step rule, not a continuous-time
  destruction solver; a blocker can consume both rounds in that step.

`Worker/corrections-Correction01.json` has 13 successful focused checks.
`Worker/ballistics-Correction01.json` reconfirms finite travel, collision once,
the 2 mm high-speed wall, normal/quarter/zero clocks, freeze/resume, capacity,
launch clearance, moving-capsule contact and attributed own-shot damage.
`Worker/Correction01/build01.log` records a successful UE 5.8.1 native build.

`Worker/Correction01/verification02.json` passes 70 checks, including the native
correction results and narrow input/cadence/airborne checks. At measured 59.97 fps,
a two-second burst launches 24 rounds with an 85.51 ms average interval. Reload
blocks firing and held intent resumes without an overdue-shot burst. Ammunition
is conserved and releasing the trigger stops firing.

The original synthetic input refresh order was reproduced: it left actual RMB
down despite an empty scheduled-key list. The corrected order clears the actual
key and aim state. The intermediate analyzer also inspected some camera samples
before the retained aim curve had settled. Its preserved failing result is
`Worker/Correction01/verification.json`; the corrected evaluator separates
immediate input/fire eligibility from full ADS after the approximately 0.37 s
blend. Raw data and video-derived frames support this distinction. Gameplay
aiming parameters were not changed to make the evaluator pass. The interrupted
cadence capture remains preserved; its successful retry supplies telemetry.

Independent read-only reviews are `Controller/rifle-and-visual-review01.md`,
`Controller/projectile-correction-review01.md`, and
`Controller/correction-input-evidence-review01.md`. They identify the exact
source and evidence hashes. Rifle reservation precedes the single ammunition
decrement; hands mesh, montage instance and once-only validation guard reload
transfer. Airborne input observers remain installed after native rifle bindings.
The controller also inspected actual final ready/impact and corrected hip/ADS
frames. Prototype ammunition and target labels are readable; stone flecks and
metal sparks are small and distinct. Targets remain gray prototype blocks:
their material has no Color parameter, so hit response is provided by the health
label, HUD, impact feedback and destruction, not an asserted mesh-color flash.

## Preservation, execution and limits

The initial and corrected direct inventories check 1,419 starting files, including vendor and
original protagonist sources: none are missing, and only the intended magazine
Blueprint and seven existing native/build files changed. New native components,
task adapters and documentation are separately inventoried. The controller
verified the unchanged owner `Config/DefaultEngine.ini`, retained lobby map,
PurchasedArms06 muzzle system, vendor magazine source, rollback and base manifest.
See `Controller/revision-preservation-check01.json`.

`Controller/final-handoff-file-check.json` verifies all 31 delivered task paths
against `Worker/Correction01/handoff-manifest.json`. The corrected preservation
report measures 28,345,146,479 project bytes, about 0.175 GB above the task start
and below the 250 GB cap. After the Multica run completed, its editor process was
no longer running. The controller reopened the saved project and retained map;
official Epic MCP `Worker/handoff-ControllerFinal01.json` confirms the final clean
state. The controller process ID is in `Controller/editor-final.pid`; its log is
`Saved/Logs/CombatFoundation01-ControllerFinal.log`. No gameplay rerun or asset
resave was required for this fresh-load check.

The only changed existing binary is the magazine Animation Blueprint, final
SHA-256 `bc96bc6301e42e72a07815fd4a91117eea649577d3f4d9b094d833694ee5c824`.
It remains under Git LFS. The new
[revision manifest](../Assets/Source/CombatFoundation01/source-manifest.json)
records the vendor, prior active and delivered identities. The separate registry
input registers this revision manifest rather than replacing an old package
fingerprint. Task-scoped Git attributes preserve the revision and review text
bytes used by the registry. Registration does not confer owner acceptance.

Multica implementation run `01a0b64f-61f3-7dde-8e3a-7e7eab995c07` and correction
run `01a0b65f-b37d-74b0-9e2b-5aca8e64d9b1` used one production worker.
Controller native records verify Astra/max, subscription login, explicit default
service tier and disabled fast mode for both runs. The independent reviewer also
used Astra/max/default. No profile restoration to an older effort, new service,
purchase or separately billed API was required. A redundant queued notification
run was canceled before execution and is not an additional production run.

Player health and the player-facing world-time ability are later tasks. This
foundation proves exact bullet stop with normal player movement and eligible
own-shot collision; it does not yet expose an ability binding or reduce player
health. The later ability must preserve a ticking collision coordinator and
avoid applying time scaling twice. All bullets, including the player's, follow
the selected world-time policy. Straight flight, no penetration/ricochet, default
128 active bullets and a disclosed 120-real-second safety retirement remain
prototype limits. Safety retirement also applies to stopped bullets and does
not refund ammunition. F6 resets targets/feedback without supplying rounds;
Stop/Play restores 30/90. No enemies or permanent lobby gameplay actors were added.
