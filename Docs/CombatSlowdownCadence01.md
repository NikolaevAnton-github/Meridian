# CombatSlowdownCadence01: rifle cadence follows world slowdown

Date: 2026-09-21. Small direct controller follow-up to MSQ-92, authorized by
the [owner's exact request and clarification](Approvals/CombatSlowdownCadence01-OwnerScope01.json).

The owner likes assisted retreat with Ctrl+F9, but reports fewer recovery steps
under sustained fire in slow motion. Bullet flight already used the 0.25 world
clock; rifle firing still used the hero's 0.65 clock. That delivered 2.6 times
as many shots per world second. The owner explicitly assigns mechanical firing
to world time while retaining faster hero movement.

`Source/MeridianSquad/PhysicsControlDummyWorld.cpp` now assigns the firing clock
to the requested world slowdown. Hero movement remains at 0.65; world simulation,
bullet flight and rifle cadence use 0.25. Hands and attached weapon/magazine
presentation retain their shared hero clock for manual actions. Shot debt is
not rebased during transitions, and normal-time restoration remains intact.

The native Development Editor build passes. A focused live PIE burst records
five native shots with four intervals of 0.340000004 seconds, matching the rifle's
0.085-second interval divided by 0.25. The captured world, projectile and firing
scales are 0.25, and effective player dilation is 0.649999976. All return to 1.0
after slowdown is disabled. The check captures 97 frames, restores temporary
editor performance settings and ends its test-owned PIE session. The editor is
left open on the retained lobby for owner Play.

Generated evidence is under `Saved/CombatSlice01/CombatSlowdownCadence01/`:
`build.log`, `runtime-check.json`, `summary.json` and preservation hashes.
The runtime export preserves a corrected delegate-handle serialization error
in `capture_export_error`; the original shot/state records were exported without
repeating the burst. Runtime assertions pass. Owner config/project edits and
the lobby map are preserved byte-for-byte.

This bounded clock correction uses controller self-checks without a new executor,
independent reviewer or full gameplay matrix. Recovery code is unchanged; final
slow-motion retreat judgement remains with the owner. MSQ-92 Candidate06 and
earlier manifests/evidence remain unchanged. This follow-up does not rebaseline
their binary identity or dispatch MSQ-93 or later tasks.
