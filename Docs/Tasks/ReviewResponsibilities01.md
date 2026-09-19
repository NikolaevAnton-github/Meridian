# ReviewResponsibilities01

Date: 2026-09-19. Multica issue: **MSQ-83**.

The owner requested clearer responsibilities and less duplicate work. See the
[exact decision](../Approvals/ReviewResponsibilities01.json). The standing
[review workflow](../AgentDevelopment.md#review-responsibilities) is authoritative.

## Result

- The executor implements, self-checks and supplies candidate-specific evidence.
- One primary independent reviewer owns technical review for substantive changes;
  additional specialists cover distinct criteria only.
- The controller accepts scope, evidence applicability and finding closure,
  coordinates corrections, closes, commits and hands off without a second full
  technical review or automatic reruns of passing checks.
- Rechecks require a recorded relevant change, evidence gap, contradiction or
  uncovered risk and cover only affected criteria and related transitions.
- Small obvious low-impact changes can use executor self-checks and controller
  acceptance unless independent review is explicitly required. Existing visual,
  owner and protagonist concept gates remain intact.

AGENTS.md, ProjectState, AgentDevelopment and the CombatSlice01 parent guidance
now reference this workflow. The live MSQ-67 description received only the two
corresponding review-guidance replacements with `--no-start`.

Six existing Multica profiles now point to the standing workflow: Code, Unreal,
Concept Art, Spatial Designer, Visual Reviewer and Environment Artist. All previous
instructions were retained. Pilot and Asset Benchmark remain unchanged.

## Verification and closure

This low-impact administrative task uses direct controller implementation and
acceptance. A bounded read-only helper located dependent policy wording; it did
not perform a second review of these edits. No production or independent review
run was dispatched for this task.

Profile readback verified the exact instruction additions and preservation of all
other fields except update timestamps, including Astra/max/default, native max
arguments, disabled fast mode, tool configuration and concurrency. This verifies
saved settings; no new model execution is claimed. MSQ-67 readback verified the
exact description and preservation of its other fields except revision/timestamps.
The task runtime remained stopped. Evidence is under
`Saved/ReviewResponsibilities01/` outside Git.

Documentation links and the approval JSON were checked, and the task diff passed
whitespace validation. No gameplay/build tests are needed for these policy-only
changes. Existing `Config/DefaultEngine.ini` owner changes are excluded from the
task commit. Historical reports and evidence are unchanged. Closure is recorded
in Multica; the controller creates the local MSQ-83 commit before owner handoff.
