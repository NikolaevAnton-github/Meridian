# Bounded leg motion during GASP falls

Date: 2026-09-22. Direct outside-task follow-up to
[ImpactRotation02](GASPEnemyImpactRotation02.md), under the
[owner's more natural fall request](Approvals/GASPEnemyAnatomicalFall01-OwnerScope01.json).

The artificial leg accent is reduced from ratio 1.5 / added-speed cap 500 cm/s
to ratio 0.75 / 220 cm/s. Its normalized direction changes from
`-0.75 * horizontalShotDirection + worldUp` to
`-horizontalShotDirection + 0.25 * worldUp`. At the cap, this commands about
53 cm/s upward leg velocity instead of 400 cm/s. These are input calculations,
not measured post-solver velocities. Whole-leg distribution and the equal
opposite trunk reaction remain; ordinary damage and local x4/x6 impacts remain.

Inspection confirmed that recovery steps can widen leg limits, but GASP's
Ragdoll profile also writes the default constraint profile. Existing recorded
falls already show authored limits; persistent widening is not established as
the cause of the owner's latest motion complaint. The strong artificial upward
accent and the permitted angular envelope are addressed separately.

Fall limits act only in Falling, Down and Dead, after the adopted sample and
PhysicsControl updates and before Chaos. They preserve the original constraint
frames and offsets, avoiding assumptions that a named swing/twist axis directly
equals an anatomical axis. Knee and ankle ranges use the authored limits:
knee 5/5/60 degrees and ankle 10/10/20, in swing1/swing2/twist constraint space.
The hip cone narrows from 60/30/20 to 50/25/20. Saved prehit standing observations
reach 39.35 degrees in hip swing1 and moving observations reach 48.34 degrees;
these are per-axis observations, not full cone-admissibility verification.
The smaller cone is owner-test tuning, with limited margin during movement.
Existing stricter limits remain stricter. Each limited axis closes at at most
120 degrees per game second, with at most 12 degrees per frame after a hitch.
No pose, body transform or velocity is overwritten, and no world-height lock or
support spring is added.

The original per-instance leg envelope is retained across Falling/Down/Dead
transitions and restored when leaving ragdoll, before the get-up entry call.
Reset clears the cache before replacing the foundation. Existing GASP profile
writes remain authoritative for locomotion/get-up; the new narrowing is inactive
in those states. Diagnostic state adds `gasp.ragdoll_leg_limit_count`; effective
joint limits continue to appear in `step.leg_joints`.

This is conservative gameplay tuning, not a validated biomechanical model.
The owner evaluates motion and the affected fall/get-up transition in Play.
No new diagnostic shot or gameplay run is made under the continuing build-only
instruction. Evidence is under
`Saved/CombatSlice01/GASPEnemyFoundation01/AnatomicalFall01/`.
The UE 5.8.1 Development Editor build passes: 19 actions, exit code 0.
The owner's config, project descriptor, lobby map and derived Physics Asset
match their pre-change SHA-256 hashes.
The restarted editor loads ratio 0.75 and speed cap 220 on the native dummy and
GASP fixture defaults; the lobby is open with no PIE or dirty packages.
