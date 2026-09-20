# PhysicsControlBalance01 (MSQ-87)

Experimental gradual instability and physical recovery on the retained six
Physics Control mannequins. This is an assisted prototype; the owner judges
weight and resistance. Independent review and owner play acceptance are separate.

## Behavior and controls

Rifle impacts retain the existing finite-flight/contact/damage path. A living
mannequin accumulates instability, buckles and leans, then recovers when impacts
are sufficiently spaced. A short repeated sequence can exceed its resistance
while it still has health. Leg hits temporarily remove the struck leg's usable
support. Losing both legs, losing floor support, excessive lean or pelvis drop
releases every Physics Control drive and leaves a continuous physical fall.

After measured settling, a living mannequin with a supported, clear recovery
area selects the back or stomach get-up. Targets blend from the actual fallen
body transforms through the complete animation and into standing at the recovered
position and heading. The visible body remains simulated throughout. Another
disturbance interrupts recovery. Blocked or unsupported recovery waits or returns
to the physical fall/down flow. Getting up never restores health; death is terminal.

- LMB, RMB, V and R retain firing, aiming, mode and reload behavior.
- F6 resets all mannequins to their home standing pose without refilling ammunition.
- F10 retains the six-fixture toggle.
- Y retains 0.25 world/body/bullet time and 0.65 player movement/firing time.

The reusable `ApplyExternalDisturbance(Impulse, WorldPoint, Bone)` applies one
bounded, non-damaging physical impulse through the same instability/fall response.
It is callable from Blueprint and Python. This is a development seam for later
push/explosion work, not a player ability.

## Tuning and assistance

All balance state is local to each instance. The existing six reaction profiles
remain; this task does not select a preferred profile or create another variant set.

| Property | Initial value | Meaning |
| --- | ---: | --- |
| InstabilityPerHit | 0.42 | Accumulation from each living rifle contact |
| FallThreshold | 1.0 | Accumulated instability that releases the drives |
| RecoveryDelay | 0.75 s | Quiet interval before instability decays |
| InstabilityRecoveryRate | 0.30/s | Decay in simulation time |
| LegDisableSeconds | 2.5 s | Temporary loss of a struck leg's availability |
| SupportReach | 26 cm | Foot-to-floor probe depth |
| MaxLeanDegrees | 48 degrees | Physical torso deviation limit |
| SettleSeconds | 0.85 s | Measured quiet interval before recovery |
| GetUpBlendSeconds | 0.8 s | Blend from actual fallen transforms |

Standing still uses distributed world-space pose springs and a pelvis spring.
They are elastic assistance, not autonomous locomotion or a force-based balance
controller. All 22 drives are disabled in falling/down and destroyed on death.
No detached world support can suspend the body after both legs become unavailable.
One remaining usable foot may retain assistance while the other leg recovers.

Recovery also uses distributed world-space assistance to follow the animation,
with static-floor footprint and standing-capsule clearance checks. It does not
perform obstacle-aware planning, stepping, moving-platform support or navigation.
All recovery, settling and temporary-leg timers use the actor's world-scaled delta.
F6 is the explicit reset/teleport exception; ordinary falls and get-up do not
replace the physical pose, momentum, bodies or collision geometry.

## Animation derivation

The original owner-selected FBXs and their exact provenance remain in
`Assets/Source/PhysicsControlBalance01/MixamoGetUp01/`. No source bytes changed.
`Scripts/PhysicsControlBalance01/unreal87.py` records the reproducible import and
retarget operations through the official Epic MCP transport.

UE 5.8.1's FBX importer uses Animated Key range and 30 FPS. This preserves the
`mixamo.com` motion instead of truncating to the generic 3.333-second timeline.
The back sequence contains 251 sampled frames (8.333 s); stomach contains 259
(8.600 s). Native XBot mesh/skeleton/animation assets, auto-characterized XBot and
Manny IK rigs, the IK retargeter and both Manny sequences are retained under
`Content/Development/PhysicsControlBalance01/` and covered by Git LFS rules.

The retargeter uses Epic's default operations and automatic target pose alignment.
The [batch retarget API](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/IKRetargetBatchOperation)
performs the sequence derivation. Every frame's principal transforms were sampled
in `Worker/motion-audit01.json`. Gameplay adds a physical start blend and a final
idle handover; neither source animation is trimmed or retimed.

The first source frames are aligned to the actual fallen head/pelvis axis and
pelvis location. The actual trunk/shoulder plane selects face-up versus face-down;
pelvis orientation alone was unreliable after a twisted leg fall. The final
idle heading follows the animation's thigh axis. These corrections are in
Candidate03 and later. Arbitrary side falls use the same bounded orientation
choice and start blend; there is no separate side get-up clip.

## Verification

Executor candidate: **Candidate05**, dated 2026-09-20. Evidence root:
`Saved/CombatSlice01/PhysicsControlBalance01/Worker/`. The immutable
`Candidate05/manifest.json` identifies source, DLL, derived assets and task tools.
The final native build passes in `build07.log`. `self-checks02.json` records 38
passing focused checks; independent technical review and owner feel acceptance
remain pending.

| Task row | Executor result on profile 1 | Continuous evidence |
| --- | --- | --- |
| 1. Recoverable versus accumulated instability | One rifle hit leaves 75 HP, about 6.68 cm pelvis drop and 7.41 degrees additional lean, then standing. Three rapid hits after reset produce a physical fall at 25 HP and instability 1.26. | `Candidate03-Core` |
| 2. Both legs and external disturbance | Two actual calf hits collapse the living body at 50 HP and instability 0.84, with all 22 drives disabled. A directional development impulse causes a separate fall at 100 HP without consuming ammunition. | `Candidate03-LegInterruptedDeath`, `Candidate03-FrontSlow` |
| 3. Physical recovery and failure paths | Back and stomach get-up complete without healing. An actual rifle hit interrupts get-up at 25 HP; a subsequent hit kills during retry and the corpse stays terminal for over 17 seconds. A physical ceiling prevents recovery until removed. Removing a real floor during get-up releases every drive and the body continues falling. | `Candidate03-Core`, `Candidate03-FrontSlow`, `Candidate03-LegInterruptedDeath`, `Candidate04-BlockedAndAnchors`, `Candidate04-UnsupportedView`; reset facts in `Candidate03-Unsupported` |
| 4. Reset and retained time scaling | F6 restores standing after recovery and after loss of support, preserving 26 and 30 rounds respectively. During active get-up, recovery advances 0.25000024 seconds per manager second at quarter world speed; effective player scale stays 0.65. | `Candidate03-Core`, `Candidate03-Unsupported`, `Candidate03-FrontSlow` |

Each named recording has a runtime JSON and an ordinary-speed `Video/*.mp4`
where listed as visual evidence. Windows Graphics Capture records the actual PIE
window with wall-clock timestamps; playback is not accelerated or interpolated.
The unsupported-view supplement follows the falling body outside the lobby on a
transient platform. The blocked-view supplement uses a wireframe material on the
real colliding ceiling so the down body remains visible. Both fixtures exist only
in PIE and are destroyed on reset/end play. No retained map was edited.

`Video/Candidate04-SixRendered.mp4` and its `002.0.png` inspection frame show all
six numbered fixtures. Runtime counts confirm profiles 1-6, zero legacy enemies,
one manager and one controller. No per-profile gameplay or subjective comparison
was performed. F10, the ammunition system, scheduler and projectile code are
unchanged; applicable retained evidence in `Docs/PhysicsControlVariants01.md`
is reused. The earlier grounded-trajectory discrepancy and low-FPS recoil
limitation are not claimed fixed by this task.

Candidate03 behavior and Candidate04 visual evidence apply to Candidate05:
subsequent native changes are confined to `GetDummyState` diagnostics; behavior,
physics settings and asset bytes are identical. `Candidate05-JointAnchors` checks
the final diagnostic through a complete get-up. `evidence-reuse01.json` records
this comparison. Earlier candidates, failed captures, the obstructed overview,
the compile diagnostic in `build05.log`, and their manifests remain preserved.

The original `self-checks01.json` contains one failed joint-gap check. Diagnosis
found two existing calf-to-pelvis constraints with all linear axes **free**. Their
anchors separate by up to 81 cm during folding, which is permitted by those
constraints. Applying a positional coincidence requirement to them was incorrect.
`joint-acceptance01.json` reconstructs the actual anchors from recorded body
transforms: all 21 position-locked joints stay within **1.059 cm** across the
focused recordings, including death. The final native metric agrees with that
reconstruction. The raw all-joint measurements remain exposed and preserved;
no joint or asset was modified to obtain this result.

## Preservation and handoff

`preservation-after01.json` confirms 695 existing inventoried files unchanged;
only the two intended existing native dummy files differ. The controller's owner
configuration, project descriptor, retained map and both original FBX fingerprints
match exactly. New binary assets use the existing Git LFS rules. The measured
73.30 GB project baseline plus all task outputs/assets remains below 75 GB,
within the 250 GB budget.

`handoff-Candidate05.json` confirms UE 5.8.1 on the retained lobby, no PIE, no
dirty map/content packages and no leaked probe actors. The executor releases
the editor writer lease. Controller-owned status, profile, registry, commit and
closure work are untouched.

The prototype retains visible pose-spring assistance and possible foot sliding.
Foot availability is a static-floor proximity test plus temporary injury timers,
not measured contact force or a dynamic balance solver. Recovery clearance is a
bounded footprint/capsule test, not swept whole-body path planning. These are
limits for owner experimentation, not claims of production locomotion or final
animation quality.
