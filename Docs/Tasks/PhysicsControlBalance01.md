# PhysicsControlBalance01: gradual instability, falling and getting up

Prepared 2026-09-20. Multica issue: **MSQ-87**, an unstaged child of
CombatSlice01 / MSQ-67. The owner authorized a trial implementation under
[the start decision](../Approvals/PhysicsControlBalance01-OwnerStart01.json).
The original [planning request](../Approvals/PhysicsControlBalance01-TaskCreation01.json)
remains preserved. Verify live Multica for execution status.

Candidate05 is now handed to the owner for testing. The
[later owner decision](../Approvals/PhysicsControlBalance01-OwnerTesting01.json)
waives independent review for this task and supersedes the original review route
below. See [controller handoff](../PhysicsControlBalance01Handoff.md) and the
[preserved executor report](../PhysicsControlBalance01.md). No independent verdict
or owner play acceptance is claimed.

Source preparation, 2026-09-20: the owner subsequently selected Mixamo's
Getting Up From Back and Getting Up From Stomach and requested their download
with project-appropriate settings. Both original FBXs are now preserved in
[MixamoGetUp01](../../Assets/Source/PhysicsControlBalance01/MixamoGetUp01/README.md),
with exact settings and fingerprints in its provenance record. This is source
intake only; the later start decision now authorizes Manny retargeting and
bounded gameplay integration in this task.

## Selected behavior

The mannequin resists disturbances with visible weight: knees buckle, the torso
leans and the body tries to recover its standing pose. A recoverable disturbance
settles back to standing. Repeated or excessive impacts, or insufficient leg
support, cause a physical fall. A living mannequin can subsequently get up when
it has settled and has usable support. This extends the owner's earlier request
for leg-hit, future push and explosion reactions; it is not just a stronger twitch
or an immediate fall on every hit.

## Bounded implementation proposal

- Build on the retained MSQ-85 six-mannequin baseline and Physics Control. Use a
  shared behavior with instance-local state and tunable resistance/recovery values;
  preserve the six fixtures and let the owner compare feel. Numeric thresholds and
  the exact controller design remain implementation choices, not owner decisions.
- Track actual support/leg availability and body deviation together with recent
  disturbances. Accumulated instability should recover between sufficiently spaced
  hits; rapid or strong disturbances can exceed the recovery capacity. Expose the
  useful tuning values without creating another broad variant experiment.
- Use a bounded standing / losing balance / falling / down / getting up flow.
  Audit both pelvis and distributed body drives; replace or limit the baseline's
  world-space supports so that a body cannot stay
  suspended after both legs lose support. Disclose any remaining assistance and
  ensure it cannot prevent the requested fall. Do not claim the old supported
  fixture already demonstrates autonomous balance.
- Keep falls physical and continuous. Getting up must start from the actual fallen
  position and orientation, blend back into control and tolerate a new disturbance.
  Getting up does not restore health. Death remains terminal; a dead body never
  enters get-up. Unsupported or blocked
  recovery must remain down or retry coherently, without snapping upright.
- Existing rifle/leg hits drive this behavior through the retained damage/contact
  path. Provide one reusable external-disturbance entry point for later force push
  and explosion work, demonstrated with a bounded development impulse if needed.
  Do not implement the full push ability, explosives, dismemberment or AI here.
  Temporary loss of usable support is sufficient for this experiment; permanent
  injury/regrowth rules are not selected by the owner.
- Animation sourcing has two owner-selected Mixamo source candidates for back
  and stomach get-up. Inspect their full motion ranges and retarget them to Manny
  during implementation. Kimodo remains an optional experiment; its first real
  generation is recorded in [KimodoGetUp01](../KimodoGetUp01.md), superseding the
  earlier installation-only generation blocker for that session. Neither source
  route is yet integrated or accepted in gameplay. Any provisional get-up must
  be labelled; a missing transition is not a completed get-up feature. No new
  paid service, asset purchase or art task.
- Preserve the single hit/damage path, living/dead distinction, corpse impacts,
  F6 reset without ammunition refill, F10 fixture toggle and retained relative
  slowdown. Use the appropriate simulation clock so recovery does not silently run
  at normal speed during world slowdown. Preserve owner sessions and asset sources.

## Focused acceptance and review ownership

Verify only the changed behavior and its transitions on one representative
mannequin, plus continued rendering of the six-fixture set. Use ordinary-speed
continuous footage with concise state/support evidence; no per-profile matrix or
independent subjective comparison of the six variants.

1. A moderate disturbance visibly buckles/leans the body and it recovers without
   falling. A short repeated sequence accumulates instability and can cause a fall.
2. Loss of both legs' usable support causes collapse while the mannequin is still
   alive; world supports cannot hold it upright. A bounded directional impulse
   exercises the same fall path intended for future push/explosion integration.
3. After settling, a supported living mannequin gets up from its actual fallen
   pose, covering front/back orientation as needed. A new hit can interrupt recovery;
   absent support does not produce an upright snap. Death prevents further get-up.
4. F6 restores a usable standing state. Check the affected recovery transition once
   under the retained slowdown and reuse applicable passing hit/death/timing evidence.

The original dispatch selected one existing Multica Unreal production executor and one primary independent
technical reviewer, the existing Multica `MeridianSquad Code` profile in its
task-local review role, at Astra/max/standard, with actual
native settings verified. The primary reviewer owns all four rows and directly
inspects the applicable implementation and actual continuous visuals, reusing
credible passing self-checks. The owner judges subjective weight and resistance.
The controller accepts scoped evidence and closes findings without a second full
technical review. MSQ-70, the full force-push ability and other successors remain
undispatched by this record.

## Execution handoff

The executor owns native code/assets, focused self-checks and the sole editor
writer lease. Confirm the live project, retained map, PIE and dirty packages via
official Epic MCP before mutations. Preserve any owner PIE session; continue
independent source work if the editor is occupied. Existing owner edits at dispatch
are `Config/DefaultEngine.ini` and `MeridianSquad.uproject`; do not revert or include
unrelated bytes in task changes. Keep one heavy build/import/render at a time.

Deliver `Docs/PhysicsControlBalance01.md` with behavior, controls, tuning, assistance
and limits. Store candidate hashes, concise acceptance results and continuous
ordinary-speed footage under `Saved/CombatSlice01/PhysicsControlBalance01/Worker/`.
Preserve full Mixamo motion ranges: the `mixamo.com` stacks contain 8.333/8.600 s,
whereas generic `Take 001` metadata ends at 3.333 s. Any animation derivation must
retain the original FBXs/provenance and record the reproducible import/retarget path.
Use Git LFS for new binary assets and keep generated logs outside Git. Workers do
not commit, change profiles/status/registry, dispatch successors or duplicate the
primary review. The controller owns verified task closure and commit.

The direct-chat sub-agent `/root/msq87_primary_review` performed only bounded
read-only acceptance/source-intake preparation. Formal candidate review was
subsequently dispatched through Multica and cancelled under OwnerTesting01.
Completed executor self-checks and controller scope/preservation acceptance are
the handoff basis; the owner performs play testing.
