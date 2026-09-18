# PurchasedArms03 / MSQ-63 controller review

2026-09-18. Controller technical handoff accepted for the owner's
[heading-dependent aiming report](Approvals/PurchasedArms03-OwnerScope01.json).
The [implementation report](PurchasedArms03.md) records the cause, fix, focused
checks and exact worker inventory. Owner visual acceptance remains separate.

The ADS translation alone was applied in world space. The native camera-attached
mesh rotates with the player, so the source vector produced 12.649081 cm of
opposite-heading gun error. The adapted AnimBP now converts that vector through
the inverse of the mesh's -90-degree anchor and applies it in component space.
ADS rotation, spring, recoil, crouch, hand IK and source offsets are unchanged.
One runtime binary changed; no C++ build or movement regression suite was needed.

Independent read-only review checked the actual graph settings, implementation,
active/rollback hashes and the recorded numerical evidence. It independently
reproduced every phase-matched count and maximum from the existing traces.
Post-fix gun/hand/sight residuals are at most 0.000721 cm / 0.001095 degrees.
The original-heading pose is preserved within 0.000384 cm / 0.000846 degrees.
All named stationary headings (0, +90, 180, -90, return to 0), aim re-entry,
canted aim and +25-degree pitch comparisons pass. The single aimed shot recovers.

The controller directly inspected actual before/after 0/180 views, the after
90 view, and re-entry, pitch and canted-pitch views. The reproduced large lateral
shift is absent after the fix; the supplied canted presentation is retained.
These are actual gameplay captures, not fabricated previews. Natural idle motion
and different environmental lighting prevent treating them as pixel-identical.

The offline coverage supplement found no paired state mismatch or invariant
violation, with identical compared FOVs. There are 791 phase-matched held-turn
samples, but matching is nonuniform: six of twelve yaw bins are populated.
The result supports the named headings and sampled turns, not uniform numerical
coverage of every angle. No extra runtime test was requested to fill those bins.
Duplicate evaluation IDs were excluded; this is not a performance certification.

Fresh UE 5.8.1 loading confirmed the saved conversion and component-space setting,
an up-to-date generated class, the retained lobby open, PIE stopped and clean
packages. The 1,419-file preservation check reports only the authorized AnimBP
changed and no missing files. The lobby map retains SHA-256
`b28fa0f6e8bb80dcc71b4789df9c3e2375a3cf8b1da67021225584e4560fd92f`.
The source bundle, native code, configuration, paused character work and historical
manifests are preserved. Temporary editor settings were restored.

Evidence is under `Saved/PurchasedArms03/`: the worker records listed in its report
and controller `ads-source-audit.md`, `fix-review.md`, `metric-coverage-review.json`
and `check_metric_coverage.py`. Production used one Multica Astra/max/standard
executor; the independent reviewer also used Astra/max. Configured and actual
native settings are recorded, with fast mode disabled for production. The
comment-created duplicate queue was cancelled before execution.

The new source revision manifest records the changed binary without replacing
historical registered fingerprints. The controller registers that manifest as
the PurchasedArms03 inventory. Validation of older inventories can still report
the intentionally revised active binary; that is expected history, not permission
to silently rebaseline it. Registration does not imply owner visual acceptance.
