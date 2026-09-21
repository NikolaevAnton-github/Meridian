# Upper-torso fall rotation accent

Date: 2026-09-22. Direct outside-task extension of
[ImpactBoost02](GASPEnemyImpactBoost02.md), following the
[owner's leg-countermotion request](Approvals/GASPEnemyImpactRotation01-OwnerScope01.json).

Upper-torso hits that cause committed living falling or newly lethal damage can
now add a single physical impulse couple. Both calves receive mass-weighted
impulses opposite the horizontal bullet direction and upward; `spine_05` receives
their exact opposite sum. The added net impulse is zero. Existing local x4/x6
impulses remain intact; joints and body velocities are not overridden.

Eligibility is limited to `spine_03`, `spine_04`, `spine_05` and the clavicles,
from standing, disturbed balance or stepping. The torso must still be reasonably
upright (at least 20 cm vertical chest-to-pelvis separation and an upward axis
component of 0.5), with valid simulated calf/chest bodies. Steep shots with less
than 0.5 horizontal direction magnitude are excluded. Head, arm, lower-torso
and leg hits do not receive the accent. Ordinary hits do not receive it either.

Initial tuning uses 75 percent of the transition impulse magnitude, bounded by
300 cm/s added velocity for both the combined calves and chest. The leg impulse
direction is normalized `-horizontalShotDirection + 0.65 * worldUp`. These are
controller-selected starting values for owner motion testing. Editable settings
are `UpperBodyFallRotationRatio` and `UpperBodyFallLegSpeed`; runtime bounds are
0-1 and 0-400 respectively.

The request reuses the existing recent-hit fall attribution and is consumed at
the next pre-physics update, after derived GASP drive/simulation transitions.
It applies once per collapse. A lethal hit supersedes a still-queued living
accent; death after an already-applied accent keeps x6 without another leg kick.
Getting-up/down/corpse hits do not start a new accent. Reset and external pushes
discard pending accents. Contact diagnostics record the combined leg impulse
and the three additional physical impulse applications separately from the hit.

UE 5.8.1 Development Editor build passes: 19 actions, exit code 0.
No firing, gameplay probes or motion verification were run under the continuing
owner instruction. Build/editor logs and preservation hashes are under
`Saved/CombatSlice01/GASPEnemyFoundation01/ImpactRotation01/`.
The owner evaluates the resulting leg lift and fall quality in Play.
