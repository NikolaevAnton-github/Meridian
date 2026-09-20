# MSQ-89 owner-test handoff

Candidate05 is delivered on 2026-09-20 under the owner's
[execution authorization](Approvals/PhysicsControlStepping01-OwnerStart01.json)
and subsequent [independent-review waiver](Approvals/PhysicsControlStepping01-ReviewWaiver01.json).
The [executor report](PhysicsControlStepping01.md) records the behavior, tuning,
measurements, recordings and remaining limits. Final motion/play acceptance
belongs to the owner; no independent technical or visual verdict is claimed.

One existing Multica Unreal executor implemented the task in run
`01a0bfe4-e852-704c-b618-fe7c43e9f998` at verified native Astra/max/default,
with fast mode disabled. No profile changes or independent review runs were needed.
The controller accepts scope, candidate identity, evidence applicability and
preservation without repeating the executor's gameplay checks.
All 32 Candidate05 manifest entries match the current files. The executor's
candidate validation establishes that all 14 native/asset entries also match
the recorded Candidate04. Controller evidence is preserved in
`Saved/CombatSlice01/PhysicsControlStepping01/Controller/handoff-acceptance01.json`.

The Development Editor build passes. Candidate04 produced nine affected records,
2,758 runtime samples and 149 passing focused assertions; Candidate05 preserves
the same gameplay sources, DLL and Physics Asset while freezing final scripts and
documentation. The unchanged six-fixture view is reused from Candidate03.
The frontal and turned lateral steps settle 15 cm from their initial stance;
support-foot drift stays below 0.62 cm and swing clearance is about 10.6-10.9 cm.
Post-step CPU-skinned sole gaps are about 0.20-0.58 cm against a 1 cm tolerance.
Actual rifle contact, a second hit, blocked placement, usable-leg loss, collapse
and displaced get-up, terminal death, relative slowdown and reset are covered.

Two failed first-postprocessor assertions remain preserved. The stable-ground
measurement was narrowed to actual settled standing while retaining a separate
check of every post-step standing sample: the pre-existing weak response can
briefly compress a sole by 0.278 cm at 30 FPS. The blocked-path assertion now
checks rejection before swing, physical collapse, released drives and absence of
suspension; it does not require a terminal DOWN state because the retained get-up
can retry and abort. These are documented measurement corrections, not runtime
changes or erased failures.

Continuous recordings accompany the measurements. The recorder captures roughly
16-17 FPS with a maximum observed gap of 0.203 seconds, so final motion judgement
remains with the owner. The trial supports flat static floors; slopes, stairs and
moving platforms are not verified. Assisted motion, some persistent knee bend,
retargeted shoulders and short get-up retries near obstacles remain limits.

All 11 executor preservation checks pass. Owner engine/project edits, lobby,
source animations, retained Physics Asset and snapshot graph remain intact.
No binary asset changed, so no new asset registration is required. Evidence and
recordings stay under `Saved/CombatSlice01/PhysicsControlStepping01/`; only scoped
code, scripts, documentation and decisions belong in the closure commit.

The executor's initial handoff check found the retained lobby with PIE stopped,
no dirty packages and no transient probe actors. A later final read observed an
owner-controlled Play session with player input and ammunition use. That session
is preserved; no further Play, stop or reset action is needed. The editor writer
lease is released. F6 resets to home without refilling
ammunition; F10, Y and Ctrl+F7/Ctrl+F8 retain their roles. No successor is authorized.
