# MSQ-119 / CAI-T02: weapon-aware cover fire

Executor handoff, 2026-09-24. **Candidate01/build04** implements protected lateral
step-outs, low-cover stand/burst/crouch, useful rifle range and short response
gates on MSQ-104 Candidate03. Native Development Editor build and **71 focused
assertions over 49 extracted production methods PASS**. Independent technical
review is **PENDING controller dispatch**. Motion, cover usefulness, reaction
feel, difficulty and performance remain **PENDING OWNER PLAY**.

No agent PIE, simulation, gameplay, firing probe, gameplay screenshot or performance
probe ran. The deterministic C++ fixtures substitute engine boundaries; their
launch counter is a policy test boundary, not an observed engine projectile.

## Identity and preserved inputs

Baseline HEAD: `29dfdfad682311df9cf5649e0d4f655bc554c69a`.
Engine: UE 5.8.3-58210709, Win64 Development Editor.
Final DLL SHA256:
`ee173c3b9416592a1ae4d66e1d08f1f014a583fa4e1b9f94ea28a840e2869b34`.
Evidence: `Saved/CombatAI01/CAI-T02/Worker/Candidate01/`.
`candidate-manifest.json` and `CAIT02-Candidate01-frozen.zip` freeze the source,
scripts, this report, DLL/modules and checks. Changes after freezing require a
new candidate; the original manifest must not be rebaselined.

Configured profile, actual native process arguments and native turn context
verify Astra/max, explicit default tier and fast mode disabled. No profile,
issue-status, registry or commit administration was performed. No other executor
or reviewer was dispatched. Controller owns review, acceptance and closure commit.

Owner configuration, project and retained map bytes match the captured inputs.
All 249 prior worker-evidence files match their pre-change hashes. Character,
player rifle, projectile and sensory producer sources remain unchanged. Controller
documentation can evolve during this run; the executor did not edit it. No assets
were edited, saved, removed or generated.

## Engagement and timing

The active rifle profile contains capability bits, effective/preferred range,
maximum cautious step, reaction/aim timing, cadence, finite burst and rest. The
current held rifle supplies this profile; future weapons can supply the same
value contract without weapon/ally-combination branches.

| Parameter | Default |
| --- | --- |
| Effective / preferred range | 5500 / 2800 cm |
| Cautious advance | At most 450 cm per request, walking; 5 s request deadline; .8 s between completed steps |
| Reaction / aim settle | .08 / .10 world seconds, paid concurrently |
| Known / new-direction contact gate | 0 / .08 world seconds |
| Sight sampling | .12 world seconds, unchanged |
| Burst / cadence / rest | 3 rounds / .18 s / .45 s |
| Magazine / reload | 12 rounds / 2.6 s; retained unlimited reserve |

A visible target already inside effective range causes braking and aiming at the
existing position. The old obstruction transition to an 85 cm chase goal is gone.
An obstructed muzzle requests a bounded cover/lane scan while holding position.
Out-of-range advancement uses a committed local step toward preferred range,
never the player's feet. Low self-health favors protection over an exposed advance.

**Source-level eligible-shot target:** first contact is eligible within .22 world
seconds plus at most two decision ticks (.12 sight polling + max(.08 reaction,
.10 aim)). Known contact adds at most .10 s plus sight polling and decision ticks;
continuous/brief retained contact adds no second acquisition cycle. Achieved
exposure takes an immediate sight sample, then launch samples sight again. An
eligible, settled repeat shot launches on the first decision at or after the
existing maximum contact/aim/rest/reload/cadence deadline. The former unconditional
one-second enable delay and stacked .65/.65 waits are removed.

These are policy deadlines, not measured visual reaction. Turning, animation aim
alpha, achieved stance, braking, travel, blocked geometry, ammunition and reload
can delay or veto fire. Such delays are explicit gates. Bullet flight, real muzzle
and torso-to-muzzle sweeps, spread, physical authority and world-time slowdown
remain. No real-time clock or missed-frame burst repayment was introduced.

## Geometry and cover lifecycle

Cover consumes the existing local tactical scan and navigator. Discovery now
samples eight directions at 60 and 100 cm, including low cover. The same bounded
53-candidate surface/column/probe set supplies protected anchors. A coordinate
offset or component bound never grants protection on its own.

An anchor requires supported feet and a clear crouched capsule. Three static
visibility rays at 60/85/100 cm must hit nearby vertical geometry that also blocks
pawns. Each lateral side independently evaluates 80/160/240/360/480/600 cm step-out
distances; a failed side does not suppress the other. The upward option stays at
the anchor. Each firing pose needs supported standing volume, an eye ray, a
120 cm weapon-space sweep and a line toward captured permitted evidence. Both
outbound and return strips require supported capsule clearance.

Proposed capsule dimensions come from the same original capsule and Mover stance
settings used by native crouch/stand. Nominal probe heights propose a pose; actual
Mover stance, animation, head sight and barrel corridors authorize a shot.

The selected action owns a generation/revision token and proceeds through:

1. Walk/crouch to the protected anchor through the checked existing route.
2. Confirm actual feet, crouch and stopped movement; remain protected during rest
   or a guarded one-time reload.
3. For a lateral peek, actually move crouched to the selected side. At the firing
   point request stand and wait for achieved stand and stopped movement. Low
   cover requests stand at the same horizontal position.
4. Seek fresh sight, satisfy current weapon gates, fire a finite burst.
5. Cancel pending rounds, crouch and follow the validated return strip. Verify
   actual protected feet before another exposure.

Cover runs during engagement as well as recent evidence-based observation. Its
own ducking occlusion cannot trigger Acquire/Search cancellation. Proposals use
captured permitted ground/aim evidence; concealed pawn transforms are absent from
the cover adapter. Small successfully observed movements refine that evidence
and force geometry revalidation, including at launch. New sounds remain in
Knowledge while the cover action owns execution. Fresh observed displacement
over 180 cm, evidence age over 6 s, loss
of useful exposed sight, interruption or deadline initiates bounded return and
reassessment. Every launch rechecks current visibility, stance, actual pose,
capsule/support/return, evidence applicability and real muzzle safety.

Stand refusal cannot authorize a shot. If the protected return is no longer
possible, stop at actual feet, reject that anchor and replan. Reset, death,
disable, weapon loss and living physical interruption clear action ownership,
pending rounds and stance requests. Living recovery retains sensory memory and
rebuilds at actual displaced feet without stale obstruction intent.

## Context extension contract

`TacticalContext` is consumed by existing position scoring, cover eligibility and
range choice. Self health is actual `Health / MaxHealth`, with invalid values
explicitly unknown. Player health is **unknown** in this slice. Future trusted
producers can call `ReceiveTargetHealth` with a matching generation, known identity,
nonzero evidence ID, finite fraction and an observation lifetime of at most 5 s.
Invalid or expired observations cannot become known target health.

Available allies are counted from the friendly fixture roster, excluding self,
disabled/dead/unready/physical-authority members and never counting an adopted
foundation pawn as another member. Three possibly overlapping composition counts
describe direct fire, cover fire and cautious movement capability. Missing manager
or an over-limit roster is explicitly unknown; a complete one-enemy roster is
known zero. This is information for policy, not live cooperation or group commands.

Examples exercised by fixtures: damage from full to 20% health increases protection
preference, permits a farther protected transfer and suppresses an exposed distant
advance; known favorable health can retain a useful firing range instead of
taking distant cover; an 800 cm weapon requests a different bounded advance from
the 5500 cm rifle; available armed versus unarmed support changes capability
summaries and cautious preference. No context can make an unsafe pose eligible,
grant a missing direct-fire capability or authorize charging through obstruction.

## Bounds, diagnostics and checks

The existing scan performs one surface or candidate assessment per work tick,
at most 40 ticks/world second, with a 4 s scan deadline. Cover candidates add up
to 13 independently bounded options; short routes retain the existing 26-sample
strip and bounded four-corner preview. This bounds work by operation count, not
by measured milliseconds. No performance acceptance is claimed.

Cover uses two anchor transfers per 12 s budget window, eight-entry per-side
spatial failure histories with 5 s expiry, a 2 s no-option rescan interval and a
12 s commitment limit. Phase limits are 8 s to anchor, 3 s to expose/stand, 2 s
to aim/fire and 4 s for final return; absence of exposed sight gets .45 s to
reacquire. At most three completed bursts share a commitment. A stale or expired
commitment can use the bounded final return, not renew itself indefinitely.

`msq.EnemyCombat status` and the existing 64-event trace now use schema 5, adding
cover phase/side/token/anchor/pose, context, range intent, timing and gate reason.
Trace exports go to `Saved/CombatAI01/CAI-T02/Traces/`. Session tuning retains the
existing keys and accepts `range`, `preferred`, `advance`, `reaction`, `aim`,
`interval`, `pause` and `reload` through the same command parser.

`checks-09.json`, `compile-09.log` and `run-09.log` record 71 passing assertions
over 49 exact production methods and production headers/tuning. Cases include
both independently obstructed sides, low/high cover, ceilings, unsupported feet,
static-only evidence, real scan-to-selection wiring, achieved stance, finite
bursts/rest, no current sight, stale/moved evidence, return failure, reload,
death/disable/physics/weapon loss, source-level latency, range/context effects
and retained scan progress during repeated sounds. The extracted real `Fire`
method rechecks fresh sight and all deadlines against an inert launch boundary.
Movement and engine animation remain explicit adapter boundaries.

The same checks preserve owner inputs, historical evidence, physics/player/
projectile/senses sources and the unchanged success-only direct sight producer.
Build04 passes 17 actions in 12.79 s. Earlier failed build/test attempts remain
preserved: a private Mover access was corrected to component lookup; fixtures
identified a lost crouch request at reload entry and an exposure sight-sampling
delay, both fixed before final verification. No broader gameplay matrix ran.

## Files and owner handoff

New native files: `CombatAICover.h`, `EnemyCombatCover.cpp`.
Changed native files: `CombatAIAction.h`, `CombatAIObservation.h`,
`CombatAITactics.h`, `EnemyCombatComponent.h/.cpp`, `EnemyCombatPolicy.cpp`,
`EnemyCombatNavigation.cpp`, `EnemyCombatTactics.cpp`, `EnemyCombatSenses.cpp`,
`EnemyCombatObservation.cpp`, all under `Source/MeridianSquad/`.
Task scripts are under `Scripts/CombatAI01/CAIT02/`; this is the sole worker report.

Official Epic MCP confirmed the retained project/map, stopped PIE and clean
packages before build and after reload. Remote Python bootstrap discovery was
unavailable in the initial editor; it made no editor change. The initial editor
was closed gracefully after the MCP guard, with no forced termination or asset
save. The final correction reload used the guarded MCP close tool. The ordinary
owner editor now runs with matching build04 DLL and no live coding replacement
modules. PID **43124**, durable log `editor-final02.log` and cleanup instructions
are recorded in `editor-launch02.json`. Close the editor
normally when finished; persistence is best effort without a supervisor. Its
live log is excluded from the immutable manifest.

Owner route: Play the retained lobby with one enemy, remain visibly at rifle
range, then use existing columns and low cover. Observe both step-out sides and
the stand/burst/crouch cycle. Block one side, relocate while concealed, reappear
from another angle, interrupt with a hit, and compare normal time with **Y**
slowdown. Use **F6** during exposure or reload and inspect status/trace when a
pose is refused. Player ammunition is not refilled by F6. Judge actual movement,
position utility, reaction feel and difficulty; these results are still pending.

The retained one-floor, home-bounded navigator and conservative static collision
assumptions remain. There is no new topology, moving/destructible-cover planning,
authored lean animation, player health/death, new weapon, live group behavior,
suppression or art/map work. Full CAI-03/04/05 and successors remain separate.
