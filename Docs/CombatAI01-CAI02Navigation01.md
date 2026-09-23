# MSQ-104 / CAI-02: bounded navigation correction

Candidate02/build01, 2026-09-24. Executor self-check delivery; primary independent
review, controller acceptance and owner gameplay judgement remain pending.

The controller integration note was read after Candidate01/build04 was frozen.
Its handoff explicitly retained the 28 m home radius, so the requested integration
was not covered. The original handoff, scripts, manifest, archive and evidence are
preserved unchanged. This correction supersedes only its navigation-domain and
pursuit-deadline statements. Read [Candidate01](CombatAI01-CAI02.md) for the delivered
senses, protected movement, audio and evidence-memory implementation.

## Bounded change

The actual one-enemy spawn/home is `(-950, -320, 0)` cm in
`PhysicsControlDummyWorld.cpp`; `GASPEnemyFixture::ResetDummy` passes that home into
`ResetCombat`. Candidate01's read-only retained-map inventory records the floor
at XY origin with extents `(3040, 1240)` cm. Its farthest corner is **4284.12 cm**
from the home. The old 2800 cm radius rejected valid requests toward the east.

| Native change relative to Candidate01 | Before | Candidate02 |
| --- | --- | --- |
| `EnemyCombatComponent.h`: default home navigation radius | 2800 cm | 4500 cm |
| `EnemyCombatNavigation.cpp`: admission and expansion radius clamps | 400–4000 cm | 400–5000 cm |
| `EnemyCombatTactics.cpp`: supported tactical-point radius clamp | 400–4000 cm | 400–5000 cm |
| `EnemyCombatComponent.h`: pursuit action deadline | 12 world seconds | 24 world seconds |

The 45 m default contains the retained floor's full XY domain with margin from
the actual home. The 50 m hard ceiling bounds tuning overrides. Radius admission
does not confer support, clearance or access through closed geometry.

The preserved CAI-01 gait inspection reports a nominal 375 cm/s running default.
A floor-diagonal approach to the existing 820 cm stopping region takes about
15.3 seconds at that nominal speed, before planning and turning. The 24-second
deadline allows the existing five-second planning ceiling plus a modest margin.
This is a tuning rationale, not measured runtime travel. The existing 2–60 second
deadline clamp remains. No movement speeds, reaction clocks, damage, weapon cadence
or world/bullets/rifle 0.25 versus hero movement 0.65 slowdown values changed.

## Focused evidence

Evidence root: `Saved/CombatAI01/CAI-02/Worker/Candidate02/`.

- `build01.log`: native `MeridianSquadEditor Win64 Development` **PASS**, 16 actions,
  23.43 seconds. Only the retained StructUtils deprecation notices appear.
- `checks-check01.json`: **PASS**, 202 navigation assertions including returned
  path-strip checks, and 16 supporting compile/source/preservation checks.
- The runner reuses the preserved CAIT01 deterministic adapters and compiles
  verbatim production `PlanPath`, `ContinuePath`, `FollowPath`, `EnsureAction`,
  `FinishAction`, `ClearIntent` and the production pursuit-timeout expression.
  Tuning defaults are extracted from the current reflected struct.
- Candidate01 native bytes are compared directly: only the three files above
  differ. The two implementation files differ solely in their radius clamps;
  the header differs solely in the two defaults and explanatory comments.

The fixture includes the retained floor dimensions and capsule-expanded bounds
of the recorded piers/central columns. Support and strip queries are deterministic
callbacks, not Unreal collision or gameplay. It reproduces the old-radius veto,
then checks these representative routes:

| Start XY cm | Goal XY cm | Purpose / acceptance | Expanded nodes |
| --- | --- | --- | --- |
| `(-950, -320)` | `(2800, -400)` | Pursuit / 820 cm | 63 |
| `(-1850, 400)` | `(2800, 400)` | Pursuit / 820 cm | 49 |
| `(2800, 400)` | `(-1850, 400)` | Pursuit / 820 cm | 49 |
| `(2600, -400)` | `(2820, -300)` | Protected move / exact endpoint, 25 cm arrival | 3 |

The affected checks also cover unsupported starts/endpoints, an unsupported goal
inside the enlarged radius, blocked strips, invalid floor layers and out-of-radius
starts/goals. They exercise expansion clamps, per-update work, plan timeout, the
soft time boundary, replacement tokens, generation reset, actual intent cleanup,
changed destinations, two failed attempts, dead/physical authority rejection and
continued crouch walking. Fixture clock values are not performance measurements.

Candidate01's 66 pure sensory/tactical and 22 extracted consumer/policy assertions,
native build, audio audit, saved animation-class ancestry and read-only editor
inspection remain applicable to unchanged code/assets. Their exact identities
are retained in the prior manifest; they were not rerun. No new editor launch,
PIE, simulation, firing, gameplay screenshot or performance probe occurred.

## Identity and preservation

- Candidate02 DLL SHA-256:
  `cf138423924d3bc3a820de26c6d6f9970dc01879265bcc94ad00edbada8203aa`.
- New immutable `candidate-manifest.json`, `CAI02-Candidate02-frozen.zip` and
  `freeze-result.json` record source, script, report, DLL and evidence identities.
- Prior Candidate01 manifest SHA-256:
  `2bcaeec6171e97d117a718a18d6d87a3cadee21bc5a9f0a28a814212d768b2a2`.
- `source-delta-from-candidate01.patch` exposes the complete bounded native delta.
- A separate `execution-settings.json` verifies configured and actual native
  Astra/max/default, fast disabled, including both recorded turn contexts.
- All 90 snapshotted Candidate01 evidence/handoff/script files and 146 older
  evidence files remain unchanged. Owner config/project/map bytes and durable
  instructions remain unchanged; the existing Multica runtime append is preserved.
  No Content or Plugins asset bytes were modified.

The final DLL has been built but has not been loaded into an editor. The controller
owns its ordinary retained-lobby reload and identity check after the sole primary
review, along with acceptance, issue administration and the local closure commit.

## Retained limits and owner check

This remains one floor layer and a bounded local grid, not full topology/Recast.
Cells remain 80 cm by default; support/slope/step and swept-capsule checks are
unchanged. Planning retains 1200 default / 2000 hard-cap expansions, at most 16
expansions per update, a 1.5 ms soft boundary between expansions and five world
seconds total. Existing finite retries and progress timeout remain.

Fresh visible evidence can now request movement toward far-room destinations
without the old home-radius veto. Heard regions still redirect the existing
nearby protected investigation; they do not become exact hidden-player chase or
fire targets. Protected selection remains local, with its existing short route,
switch and travel limits. The larger domain does not guarantee access to every
room point through actual collision or completion within the finite action budget.

Owner gameplay remains open: establish distant visible contact toward the far
end, lose sight behind geometry, emit sound from a different region, then interrupt
movement physically or with F6. Judge useful pursuit, protected repositioning and
slowdown/deception alongside the original Candidate01 owner route. These are
pending observations, not agent-tested outcomes.
