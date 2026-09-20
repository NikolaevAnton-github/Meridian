# Optional combat test controls

Added 2026-09-20 at the owner's direct request, outside MSQ-88. This is a small
extension to the MSQ-87 owner-test build. MSQ-88 was still undispatched at this
addition; the later [separate start](Approvals/PhysicsControlRecovery01-OwnerStart01.json)
authorizes that task while preserving these controls.

| Shortcut | Toggle |
| --- | --- |
| Ctrl+F7 | Immortal Physics Control mannequins |
| Ctrl+F8 | Infinite rifle reserve ammunition |
| Ctrl+F9 | Prevent full balance-loss falls (added in CombatTestToggles02 below) |

All default to off when a new play session starts. The HUD displays their state;
infinite reserve is also shown as `RESERVE INF`. Press the same shortcut to disable.

Immortality stops health loss while retaining physical hit impulses, instability,
falls and living get-up. It does not resurrect an existing corpse; F6 resets the
mannequins. Immortality survives F6 and F10 fixture recreation within the session.

Infinite reserve preserves the finite reserve count while enabled. The magazine
still loses one round per shot, can run dry and requires the ordinary reload
animation/commit. Reloading works even when finite reserve is zero. Disabling the
toggle resumes spending that retained finite reserve. Toggling during reload uses
the setting at its normal transfer event. F6 neither refills ammunition nor clears
any test toggle. The spare-magazine presentation follows the infinite reserve state.

The retained animation assets, MSQ-87 Candidate05 manifest/report and MSQ-88 scope
are unchanged. Build and focused runtime evidence belong under
`Saved/CombatSlice01/CombatTestToggles01/`.

Verification: Development Editor build passed. Focused native-input checks passed
for both Ctrl chords in both directions, ordinary magazine depletion/dry fire,
reload at zero reserve, resumed finite reserve spending, F6 persistence, survival
of otherwise lethal hits and death after disabling immortality. Nonzero physical
impulses remain present. The HUD screenshot was inspected. The editor was returned
to its original map/camera with PIE stopped and no dirty map/content packages.

## CombatTestToggles02: three mannequins and optional fall prevention

Added 2026-09-20 at the owner's direct request before MSQ-92, outside the task
family. The active fixture now creates only profiles 1, 2 and 3 at their retained
first-row positions. Profiles 4-6 remain in source and historical evidence.
MSQ-92 and successors remain undispatched.

Ctrl+F9 toggles `prevent falls` in the HUD. While enabled, living standing or
stepping mannequins retain powered standing assistance when a disturbance, lost
support or failed step would otherwise release all balance drives. Physical hit
impulses, partial instability and feasible recovery steps remain active. This is
an experimental assistance override, not the later adaptive balance work.

The toggle defaults off, persists through F6 reset and F10 fixture recreation,
and turns off on the next new play session. It does not prevent death: use the
separate Ctrl+F7 immortality toggle for sustained shooting experiments. Enabling
it after a fall has begun leaves that fall/get-up sequence intact; use F6 for an
immediate standing reset.

Build and focused runtime evidence belong under
`Saved/CombatSlice01/CombatTestToggles02/`. Earlier candidate manifests and
evidence remain unchanged.

Verification: Development Editor build passed. The focused record confirms the
three original front-row profiles, native Ctrl+F9 in both directions, retained
22 powered drives under a strong external impulse and both-leg disturbances,
ordinary full fall after disabling, and F6/F10 persistence. The HUD was inspected.
Owner engine/project edits and retained map hashes match their pre-change values.
The automated rifle attempts emitted no shots, so they are not used as hit
evidence; the existing external-disturbance probe verifies the changed fall gate.
One D3D12RHI/Slate rendering crash during verification is preserved in Saved;
the editor was restarted without further source changes. This correction does
not claim an independent review or MSQ-92 acceptance.
