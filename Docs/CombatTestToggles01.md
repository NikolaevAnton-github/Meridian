# Optional combat test controls

Added 2026-09-20 at the owner's direct request, outside MSQ-88. This is a small
extension to the MSQ-87 owner-test build. MSQ-88 was still undispatched at this
addition; the later [separate start](Approvals/PhysicsControlRecovery01-OwnerStart01.json)
authorizes that task while preserving these controls.

| Shortcut | Toggle |
| --- | --- |
| Ctrl+F7 | Immortal Physics Control mannequins |
| Ctrl+F8 | Infinite rifle reserve ammunition |

Both default to off when a new play session starts. The HUD displays their state;
infinite reserve is also shown as `RESERVE INF`. Press the same shortcut to disable.

Immortality stops health loss while retaining physical hit impulses, instability,
falls and living get-up. It does not resurrect an existing corpse; F6 resets the
mannequins. Immortality survives F6 and F10 fixture recreation within the session.

Infinite reserve preserves the finite reserve count while enabled. The magazine
still loses one round per shot, can run dry and requires the ordinary reload
animation/commit. Reloading works even when finite reserve is zero. Disabling the
toggle resumes spending that retained finite reserve. Toggling during reload uses
the setting at its normal transfer event. F6 neither refills ammunition nor clears
either toggle. The spare-magazine presentation follows the infinite reserve state.

The retained animation assets, MSQ-87 Candidate05 manifest/report and MSQ-88 scope
are unchanged. Build and focused runtime evidence belong under
`Saved/CombatSlice01/CombatTestToggles01/`.

Verification: Development Editor build passed. Focused native-input checks passed
for both Ctrl chords in both directions, ordinary magazine depletion/dry fire,
reload at zero reserve, resumed finite reserve spending, F6 persistence, survival
of otherwise lethal hits and death after disabling immortality. Nonzero physical
impulses remain present. The HUD screenshot was inspected. The editor was returned
to its original map/camera with PIE stopped and no dirty map/content packages.
