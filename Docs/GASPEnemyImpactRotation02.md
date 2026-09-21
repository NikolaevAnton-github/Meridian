# Whole-leg upper-torso fall rotation correction

Date: 2026-09-22. Direct outside-task correction following the owner's report that
[Rotation01](GASPEnemyImpactRotation01.md) was barely noticeable, under the
[one-shot diagnostic authorization](Approvals/GASPEnemyImpactRotation02-OwnerScope01.json).

The recorded lethal `spine_04` contact activated the previous rotation accent:
its three extra impulse applications were present. The local x6 hit magnitude
was 10,200, but the 5 kg chest body capped the calf pair's requested 7,650 at
1,500. Only 817.48 of this was upward. Both whole legs weigh 20 kg, so that
upward momentum corresponds to just 40.87 cm/s whole-leg mean velocity change
before joint and contact response. Recorded maximum rendered foot lift was
8.20 cm left and 1.41 cm right relative to the last prehit sample. These values
describe the previous implementation, not the corrected motion.

The accent now distributes momentum by mass over both complete legs
(`thigh`, `calf`, `foot`) and distributes the equal opposite reaction over the
pelvis and five spine bodies. All twelve bodies must be simulated and have
positive finite mass before any impulse is applied. Each leg body receives the
same added velocity. The complete pair is capped using the smaller total group
mass, preserving zero net added linear impulse without clipping either side.

`UpperBodyFallRotationRatio` changes from 0.75 to 1.5, and
`UpperBodyFallLegSpeed` from 300 to 500 cm/s, with runtime/editor bounds of
0-2 and 0-600. The leg direction becomes normalized
`-0.75 * horizontalShotDirection + worldUp`. For the recorded 20 kg leg and
30 kg trunk groups and 10,200 hit, the new calculation would command a 10,000
leg impulse: 300 cm/s backward and 400 cm/s upward added leg velocity. This is
an analytical initial impulse budget, not a measured post-solver result or a
guarantee of the resulting lift.

Upper-torso eligibility, upright/shot-angle checks, deferred pre-physics timing,
one accent per collapse, reset handling, living/death attribution and existing
x4/x6 local impacts remain unchanged. Contact evidence now also records leg and
trunk group mass and commanded leg delta speed; the impulse count is twelve.

Rider LLDB attached, but both source breakpoints remained unbound with
"No executable code is associated with this line"; the paused frame was unknown.
The diagnostic conclusion therefore uses the existing runtime contact/motion
recorder, not debugger frame inspection. Agent breakpoints were removed, the
debugger detached, and the eight pre-existing user exception breakpoint flags
were retained. The preliminary background-throttled input attempt launched
zero shots. The subsequent recording used one round and produced exactly one
shot, one hit and one death across all three fixtures. Background throttling
was restored, PIE stopped, and the editor reported no dirty assets.

Diagnostic recordings remain under
`Saved/CombatSlice01/GASPEnemyFoundation01/Worker/ImpactRotation02-Diagnostic*.json`.
Build, loaded-default checks and preservation evidence are under
`Saved/CombatSlice01/GASPEnemyFoundation01/ImpactRotation02/`.
The UE 5.8.1 Development Editor build passes (19 actions, exit code 0).
The restarted editor loads ratio 1.5 and speed cap 500 on both native dummy and
GASP fixture defaults, with the lobby open and no PIE or dirty packages.
SHA-256 comparisons preserve the owner's config, project descriptor and lobby map.
Post-correction firing and motion acceptance remain with the owner.
