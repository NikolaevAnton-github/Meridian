# MSQ-92 owner-test handoff

Candidate06 delivers adaptive recovery steps on static flat support and the
owner-requested faster response. Ordinary adjustable `RecoverySpeed` is **1.25**;
assistance multiplies it to 1.5 within the retained bounds. The comparable actual
rifle-hit step takes **0.667 s instead of 0.833 s**, with reaction timing 0.08 s
instead of 0.10 s. This implements approximately 25 percent faster recovery,
with final tuning and motion/play judgement remaining with the owner.

Execution follows the [owner start and tempo request](Approvals/PhysicsControlAdaptiveSteps01-OwnerStart01.json)
and [task](Tasks/PhysicsControlAdaptiveSteps01.md). The [executor report](PhysicsControlAdaptiveSteps01.md)
is preserved as part of the immutable candidate; its pending-review wording
describes the original handoff and is superseded by this controller acceptance.

One Multica Unreal executor, run `01a0c101-540e-7aa8-8bb5-302f6dad38f1`, delivered
Candidate06 with Candidate05 native code and Development Editor build06. Build
and **208/208 focused assertions across 1,606 states** pass. One independent
MeridianSquad Code reviewer, run `01a0c12d-0f8f-7ea6-be47-c3fc3e704974`, passes
**all six scoped criteria with no blocking findings**. Both saved profiles,
native process arguments and actual session contexts confirm Astra/max/default,
fast mode disabled. No profile changes or restoration were necessary.

The review is recorded in
`Saved/CombatSlice01/PhysicsControlAdaptiveSteps01/Controller/Review/primary-review01.md`.
The reviewer inspected relevant source and evidence, verified all 438 current and
frozen manifest entries, and directly inspected 267 consecutive video frames on
17 sheets plus full selected views and the three-mannequin overview. Applicable
passing checks were reused; no duplicate gameplay matrix or new runtime check
was required. The controller accepts owner scope, evidence applicability,
preservation and finding closure without a second technical review.

The candidate manifest SHA-256 is
`73092ced355d983d126627b5fee6bc69e002f47fe73fefdad65b84fddc9e1719`.
Evidence and the immutable archive remain under
`Saved/CombatSlice01/PhysicsControlAdaptiveSteps01/Worker/`.

The two disturbance records move the first foot 12.25 and 19.50 cm, with measured
peak sole heights 5.85 and 7.61 cm. Replanning is filtered, limited to two updates
and 6 cm total travel, and never restarts the step clock. Whole-arc reach/joint
checks and bounded shortening reject infeasible steps. Twelve real torso hits
produce three completed steps and settling at 3.867 s with assistance off.
Blocked landing releases the drives into physical falling. Relative slowdown,
F6/reset and F10 recreation clear or advance the changed state correctly.

The exact Candidate03-to-final applicability mapping supports six reused records;
final native Candidate05 supplies the pair, mid-step replan and torso episode.
Unchanged MSQ-97 support/effort, death, inter-leg contact and get-up evidence keeps
its original identity. Historical failed attempts and manifests remain intact.

This remains assisted prototype recovery on static flat support. The roughly
16 FPS footage cannot exclude brief sub-frame artifacts; the minimum sampled
swing sole estimate is 0.122 cm, not a continuous skinned-mesh clearance proof.
Final sole gaps are 0.283-0.471 cm and peak planted-foot drift is 0.428 cm.
These limits are retained explicitly; owner motion acceptance is separate.

Owner engine/project edits and the retained lobby match dispatch fingerprints.
No Content or Assets file changed, and no registry operation was needed. The
executor released its editor writer lease with the final build loaded, no PIE,
dirty packages or transient probe actors. The reviewer and controller made no
editor changes. Unreal is ready for owner Play based on that handoff snapshot.
MSQ-93 and later tasks remain undispatched. The controller closes MSQ-92 and
commits only its verified task-scoped changes locally before owner handoff.
