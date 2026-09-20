# PhysicsControlRecoverability01: physical balance recovery under hits

Multica issue: **MSQ-97**.
Stage 2 of [PhysicsControlRefinement01](PhysicsControlRefinement01Plan.md).
Predecessor: [PhysicsControlLegPose01 / MSQ-91](PhysicsControlLegPose01.md).
Next: [PhysicsControlAdaptiveSteps01 / MSQ-92](PhysicsControlAdaptiveSteps01.md).

## Owner direction and authorization

The owner selected this as the next task after discussing displaced-leg
replanting, successive steps under torso fire, different enemy capabilities and
physically unrecoverable loss of support. See the [exact request and scope](../Approvals/PhysicsControlRecoverability01-NextTask01.json).
This preparation creates the next task and updates its dependencies; it does not
dispatch implementation. Keep the issue in backlog, unassigned, with zero runs.
Earlier review waivers remain attached to their original tasks.

Use MSQ-91 Candidate07 plus the three-mannequin/control adjustment in
[CombatTestToggles02](../CombatTestToggles01.md#combattesttoggles02-three-mannequins-and-optional-fall-prevention),
commit `37af4b8`, as the retained implementation baseline. Preserve their exact
sources and evidence. The owner finds ordinary reactions generally usable but
rejects the unlimited fall-veto toggle as the requested continuous recovery.
This feedback does not establish final motion acceptance.

## Scope

Establish a physically bounded recovery controller on static flat ground. Base
recovery decisions on actual body motion and usable support, not only hit counts,
bone names, a fixed leg-disable timer or a two-step counter. Estimate the center
of mass and momentum, body lean/rotation, usable foot contact/footprint and
slip/contact feasibility, reachable clear placement, response time and available
actuator effort. Choose and document a practical approximation and its limits;
an exact general proof of inevitable falling or a prescribed robotics solver is
not required. A nearby floor ray alone must not establish weight-bearing support.

Bound the strength/effort of the physical drives and connect assistance to valid
support and recovery progress. Existing world-space springs, including pelvis
support, must not keep an unsupported or unreachable pose suspended. A transient
foot lift during a feasible step is not itself a failure. Distinguish recoverable
motion, active recovery and loss of recoverability with stable transitions;
avoid frame-to-frame state oscillation and unlimited retries without progress.

A leg hit applies the physical disturbance and any configured temporary strength
reduction. The displaced leg may land at a new reachable position while the
other leg supports; coordinate pelvis and trunk motion with this placement.
Do not automatically invalidate the entire leg and then fall because stepping
requires two undamaged legs. Use actual displacement/impulse direction rather
than a canned directional snap. Neither every hit nor every simultaneous
two-leg hit is automatically unrecoverable; support and recovery capacity decide.

Permit successive reactive steps under sustained torso hits while useful support,
reach, effort and progress remain feasible, including more than two completed
steps. Incoming hits may update future placement without indefinitely restarting
the step or requiring a gap longer than the rifle's hit cadence. When hits stop,
settle if recoverable, otherwise release into the retained physical fall/get-up.
Loss of recoverability can cause a fall during the burst. Do not guarantee
standing until the last bullet or force a fall solely because firing stopped.
Health depletion retains terminal death; this task does not defer death for a
cinematic sequence. Ctrl+F7 remains separate immortality for owner experiments.

Expose reusable enemy recovery settings for strength, reaction/step speed, reach
and recovery persistence. They alter the body's available recovery capacity;
they must not bypass collision, joint limits or missing support. Keep the three
existing mannequin identities and hit-reaction profiles. Do not add enemy AI or
new character variants. Necessary adaptation to make this controller work belongs
here; MSQ-92 subsequently refines step length/lift/timing and filtered replanning,
reusing applicable evidence. Expanded torso/arm counter-motion remains MSQ-93.

Verify relevant inter-leg self-collision pairs in the actual candidate Physics
Asset. A struck leg must be able to contact and displace the other through
collision, with resulting support loss evaluated by the same controller. Do not
fake this case with a separately injected impulse on the second leg. Preserve
selective self-collision and use a scoped asset derivative if bytes must change.

Replace Ctrl+F9's unlimited fall veto with a clearly labelled bounded recovery
assistance test preset. The preset may increase recovery capability within
declared limits, but must still fall when recovery is infeasible. Keep its HUD
state explicit, default it off, retain it across F6/F10 within a session and clear
it on a new session. Ordinary mode also uses the new recoverability rules.

## Focused acceptance

1. Reproduce the baseline one-leg-hit failure, then show a real rifle hit on one
   representative mannequin displacing and replanting that leg with coordinated
   body adjustment. Preserve anatomical knee/foot alignment and calibrated sole
   contact. Supply ordinary-speed continuous motion and the deciding measurements.
2. Show a real sustained torso burst with more than two successive completed
   recovery steps. Verify cessation and one resumed burst before settling; new
   hits must not starve step initiation or perpetually restart a swing.
3. Demonstrate a recoverable disturbance and one genuinely unrecoverable loss of
   support involving both legs. Record support, body motion, reachable placement
   and effective effort limits explaining the different outcomes. Falls release
   the drives instead of hidden suspension, teleportation or forced placement.
4. Demonstrate one struck-leg-to-other-leg collision and its effect on support.
   Identify the participating bodies/contact and transferred motion. A controlled
   impulse on the first leg is allowed for isolation; contact must drive the second.
5. On the same representative mannequin, make one bounded settings change that
   measurably changes recovery capacity. Check Ctrl+F9 on/off and its infeasible
   fallback; leave subjective comparison of the three profiles to the owner.
6. Check the changed transitions only: settle/fall into retained living recovery,
   death during active recovery, F6/F10 cleanup/persistence and one affected
   relative-slowdown episode. Confirm three mannequins render. Reuse unchanged
   rifle, ammunition, other animation and earlier get-up evidence.

Reuse existing input, disturbance, recorder and measurement tools. Failed
simulated fire that emits no bullets is not real-hit evidence. One primary
independent reviewer owns technical review on execution, reusing applicable
self-checks under [review responsibilities](../AgentDevelopment.md#review-responsibilities).
The controller accepts scope/evidence/finding closure; the owner judges motion
and play. Do not expand to a per-profile or full animation matrix.

## Boundaries and handoff

The projectile currently stops at its first contact. One penetrating bullet
crossing both legs requires a separate future projectile-penetration change;
it is not an implementation dependency for this task. Multiple timed impacts may
verify the balance response, clearly labelled as such, but cannot establish
penetration. Preserve this future integration scenario without creating or
dispatching an additional projectile task here.

No navigation/pursuit/general walking, uneven or moving terrain, new get-up clips,
new art, AI expansion, damage-system rewrite or automatic successor dispatch.
Use the existing Multica executor at verified Astra/max/standard, one production
writer and one heavy workload. Preserve the owner editor session, map, engine/
project edits, original sources and immutable candidate manifests. Register any
scoped binary derivative under the existing asset workflow; no registration can
silently accept overwritten baseline bytes.

Deliver `Docs/PhysicsControlRecoverability01.md` and an identified candidate with
focused evidence under `Saved/CombatSlice01/PhysicsControlRecoverability01/`.
Record actual recovery limits, approximation limits, enemy settings and final
Ctrl+F9 behavior. The controller owns the verified local closure commit and
Multica status; completion does not start MSQ-92.
