# PurchasedArms02 / MSQ-62 controller review

2026-09-18. Scope: the owner's [purchased-rifle integration and reload report](Approvals/PurchasedArms02-OwnerScope01.json).
Implementation and controls are in [PurchasedArms02](PurchasedArms02.md).
This is controller technical review, separate from owner visual acceptance.

## Disposition

**Controller technical handoff accepted.** Reload recovery, source action coverage,
retained-lobby traversal, corrected crouch collision and the authored-camera option
pass the reviewed checks. The retained lobby is ready for Play with PIE stopped.
Original protagonist production and deferred lobby architecture remain paused.

## What changed and why

The minimal native pose sampler reconstructed reloads over static poses, obscuring
locomotion during the late action and using a different ADS pose composition at
handover. Baseline evidence measured approximately 2.107 cm left-hand lateral
change and 2.217 cm moving hip-gun drop. Clock synchronization alone missed these
defects; the old verifier also released movement at completion.

The integrated source character now uses its supplied animation graph, continuous
locomotion, action slots, procedural offsets, hand IK and synchronized weapon and
magazine logic. Native CharacterMovement provides actual traversal, crouch,
jump/landing and wall-stop behavior. The source was a stationary animation demo.
The retained map and owner art are preserved.

The source audit distinguishes actual controls from absent gameplay. Shooting,
recoil, effects, sound, casing/magazine physics, grip changes, ordinary/quick/empty
reloads, inspection, canted aim and auxiliary actions are retained. The source
counter wraps after depletion and reload does not refill it. No damage, health,
finite ammunition economy, functional grenade, inventory or unsupported prone
system is claimed. Arena, tutorial UI and full-body showcase cameras are excluded.

## Verification and independent review

Evidence is under `Saved/PurchasedArms02/`; full generated records remain outside Git.

- `Controller/reload-audit.md` and `baseline-review.md` establish the original
  cause from source and evaluated runtime data, including held movement after the
  old action cleared. No fabricated debugger session is claimed.
- `Controller/recovery-matrix-review.md` independently checks eight ordinary/empty
  reload cases: stationary/moving, hip/held ADS. Both hands, gun and sights return
  to their phase-matched controls, including the first 0.25 seconds after action
  completion. Moving recovery lasts at least 4.325 seconds at 360 cm/s. Maximum
  immediate left-hand residual is 0.007202 cm. The former nearly static tail now
  retains locomotion; the final-tail gun motion/control ratio is 0.9984-1.0036.
- `Controller/final-visual-review.md` inspects actual comparable PNGs and decoded
  MP4 frames from four completed reload takes and hip/ADS/canted firing. No lasting
  left drift, hip dip, detached weapon/hand, visible extra body or tutorial was
  observed. Muzzle smoke/light follows the barrel. The controller also inspected
  the stationary hip/ADS and shooting comparison images directly.
- `Worker/build07.log` and cold-load receipts establish a successful UE 5.8.1
  build and 400 loadable active packages, with no missing or forbidden arena/UI
  dependencies. `Worker/final-graph-contract.json` records the actual parent,
  arms mesh, inputs, disconnected demo startup/tick and camera configuration.
- `Worker/Walk02/runtime-verification.json` passes the actual PlayerStart,
  entrance collision, elevator approach and return route using real input and
  CharacterMovement. `Controller/final-targeted-review.md` supports the long-fall
  hold, landing-driven recovery and cessation of run/sprint loops at a wall.
- Feature and interaction takes exercise short/held input, repeated/locked actions,
  changed aim/direction, grip and action variants. Firing and prop takes record
  dynamic first-person effects, shadowless casings/magazines/syringe and non-silent
  mixer output. The documentation identifies these as source demonstrations.

The independent clearance review caught a further defect that the initial worker
summary missed: uncrouch restored the vendor Blueprint CDO's 5 cm radius, despite
the spawned pawn starting at 34 cm. The saved Blueprint default is corrected to
34/88 cm and verified after a cold editor load. In `Correction01-Capsule`, all
1,270 samples retain radius 34; open and obstructed crouch/stand transitions use
half-heights 56/88 and agree with source stance. The final standing camera returns
to 82 cm above the capsule center. Prior failing evidence remains preserved.

The first L camera action pair exposed inverted source-flag semantics: true locks
the head to reference pose. The native selection now matches that source behavior,
with motion disabled by default. `Controller/camera-correction02-review.md` checks
the corrected action pair: the enabled returned camera matches the authored source
camera and reaches 5.209330 degrees; disabled view and off-return stay fixed.
The saved branch mask affects only `head` and descendants, so this correction does
not change the previously verified arm/gun reload composition. Flag-only and
walking-only records are not used as camera-motion acceptance proof.

## Evidence limits

External videos capture approximately 11-12 frames/s; they support composition,
not exact single-frame timing or the peak geometry of a transient muzzle flash.
Evaluated gameplay records provide the separate continuity evidence. Instrumented
records contain occasional long engine intervals and a few duplicate evaluation
rows, excluded from fresh-pose comparisons; this is not a hitch-free performance
certification. Mixer recordings do not certify physical speaker output. Owner
visual acceptance remains separate from build, numerical and independent reviews.

## Preservation, metadata and execution

The map retains SHA-256
`b28fa0f6e8bb80dcc71b4789df9c3e2375a3cf8b1da67021225584e4560fd92f`.
The immutable vendor bundle, original character sources, accepted history and all
125 archived files are preserved. The 400-package active set has 314 new packages;
six copied packages are adapted. Sources and current copies are linked by
`Assets/Source/PurchasedArms02/source-manifest.json`. Rollback and excluded staging
are preserved under Saved. Binaries use existing Git LFS rules; no owner assets
were removed for space and the project remains below 250 GB.

Registry closure uses a separate PurchasedArms02 inventory and new path identities.
Earlier registered fingerprints are not replaced: previously registered code/config
paths retain their historical PurchasedArms01 identities. Their current authorized
revision is recorded in `Assets/Source/PurchasedArms02/integration-manifest.json`.
Historical validation can therefore report the expected changed code paths; this
does not silently accept new bytes under an old immutable identity. Registry
registration is inventory, not owner visual acceptance.

Production used one intended Multica MSQ-62 run and one editor writer. Independent
reviewers only read source and saved evidence. Configured and actual native
Astra/max/standard settings were checked in `Controller/native-settings.json` and
reviewer execution receipts. Comment-created duplicate queues were cancelled before
execution; they performed no production work. The controller owns final status,
profile cleanup, registry validation and a task-scoped local Git commit. Unrelated
owner edits and paused-character work remain outside that commit.
