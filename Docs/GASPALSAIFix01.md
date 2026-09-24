# GASPALS AI correction

Date: 2026-09-24. Existing work reference: MSQ-121.
Authority: [direct owner correction](Approvals/GASPALSAIFix01-OwnerStart01.json).
Baseline: audit commit `84a8423`, with [audit findings](GASPALSAIAudit01.md).
Execution is direct, outside Multica, without a new task.

Status: implementation and focused verification complete; primary review closure
is recorded in the linked report.

## Corrections

| Finding | Implementation |
| --- | --- |
| F1: clear sight/full aim but 13-15 degree barrel error | The existing final spine control aligns the actual rifle axis and muzzle with the observed target. It removes the last evaluated correction before recalculating, limits correction to 35 degrees, leaves large turns to source locomotion and freezes calibration during localized physical hits. The original six-degree launch gate remains. |
| F2: stationary until the first shot; weapon actions stop movement | Contact acquisition starts supported movement before any shot. Short successful mobile legs hand off without an intentional rest. Movement, finite bursts and timed reload now advance independently. Reload retains its token and deadline across ordinary tactical replacements and sight loss. Failed physical aim has a bounded reorientation retry. Source walk and run are eligible for grounded fire. |
| F3: enemy step producer still requires Mover | The producer accepts CharacterMovement and its actual grounding/displacement. It queues gameplay sound events; source animation remains the audible foley owner. An explicit event counter makes this observable. |
| F4: reset destroys controls while iterating their owning array | Teardown copies the control names before destroying them. |
| F5: missing physical bone pose data on hits | Source `PreCMCTick` actually defaulted to DuringPhysics, promoting CMC, animation and physical drives into the wrong phase. The adapter pins this upstream producer to PrePhysics. The post-source helper manually updates PhysicsControl only from a fresh, complete, nonparallel animation pose before physics blending. Unavailable samples retain a bounded cache; stale controls are explicitly disabled and updated to zero their drives. |

Moving cover scans also revalidate travel policy using the current route length,
not distance from the old scan origin. The primary reviewer identified this
secondary defect and verified its correction.

## Source anatomy for cover proposals

The measured source standing aim pose has a head height near 134 cm and a spine
pivot near 88 cm. Legacy lean proposals assumed 170 and 95 cm: at 32 degrees,
they overestimated lateral head travel by about 15 cm. Actual lean/launch gates
prevented unsafe shots, but the bad proposal could commit an unusable cover lane.

The active source adapter now caches measured neutral anatomy after completed
animation evaluation. Coordinates use feet and horizontal heading. Standing
exposure records full aim; crouched protection records the lowered rifle pose
used by that state. Caches survive reload and invalidate with pawn replacement.
Before both stances have been observed, paired source pose measurements provide
an explicit per-point opposite-stance estimate. Capsule shrink alone was rejected:
it is 26 cm, while the source head drops about 43 cm. No first cache means no source
cover proposal. Actual crouched protection, lean arcs and launch geometry remain
authoritative. Historical non-source fixtures retain their original proposals.

## Focused evidence

Evidence root: `Saved/GASPALSAIFix01/`. Raw failed candidates are retained.

| Check | Result |
| --- | --- |
| Build03 clear-lane combat, 12.002 s | 26 shots, two completed reloads; 115/115 samples have movement commands. Both pre-first-shot samples already move. All 50 reload samples retain movement commands. Full-aim error 0.0035-0.2986 degrees. |
| Build05 after source anatomy integration, 12.006 s | 26 shots, two completed reloads; 114/114 movement commands, including both samples before the first shot and all 50 reload samples. Full-aim error stays below 0.255 degrees. |
| Turned target, Build03 and Build05 | Build03 reacquires and fires through actual lean at 32 degrees, with measured barrel error below 1.575 degrees. Build05 produces 24 shots over 12 seconds after target relocation; corrected geometry does not offer a lean in that placement. The bounded lean watcher times out and is retained as an unexercised final lean transition, not a pass. |
| Reload with lost sight, Build02 | Same reload action 103 completes once, count 10 to 11, magazine refills to 12 after visibility becomes false. |
| Manual source aimed run, Build03 | Gait 1 reaches 500 cm/s, ground fire eligibility remains ready, measured barrel error at speeds above 250 cm/s is at most 0.046 degrees. AI was disabled for this isolated command; this proves run eligibility/alignment, not autonomous running shots. |
| Local physical hit, Build03 | 47 valid local pose frames, zero invalid/deferred frames, 15 active drives during the hit, zero active drives/regions after recovery; five additional shots in the two-second capture. Actual body/helper groups are PrePhysics. |
| Physical body response, Build03 | A separate one-second capture records 17 simulated spine samples, peak body velocity 289.74 cm/s, and return to non-simulated locomotion with zero local drives. |
| Enemy step producer, Build03 | 78 queued enemy step events at the captured world status. No other enemy exists to receive them; delivery count is not used as producer evidence. |
| Real launch socket, Build06 | 11 shots in 3.004 seconds, 29/29 movement commands; full-aim error 0.0060-0.2551 degrees across 26 samples, measured from the actual `Muzzle` socket. |
| Final anatomy comparison, Build06 | Standing cache projects back to all five actual points within numerical precision. Initial crouch estimates differ from the later achieved ready pose by 0.98-1.30 cm; head height 90.421 cm estimated versus 89.844 cm achieved. The achieved stance replaces the estimate. |
| Reset/end-play, Build06 | Reset returns ready, clears local drives/regions and both anatomy caches; no teardown or missing-bone-data errors. PIE is stopped, dirty package list empty, background throttling restored and editor normally closed. |
| Native builds | Build01 through Build07 compile successfully. Build01/02 remain failed intermediate runtime candidates for F5; zero warnings in Build02 was correctly rejected because controls never activated. |

Build01-Build05 sample series retain the audit's local fallback muzzle point.
Their angular measurements are approximate; movement/reload evidence remains
applicable. Build06 explicitly records the real socket and closes the numeric
alignment criterion. Historical captures were not rewritten.

The final anatomy, turn/reacquisition, reset/end-play evidence and binary
identity are recorded in the final closure below and the
[sole primary review](GASPALSAIFix01Review.md).

## Scope and limits

Weapon actions no longer command an open-lane enemy to stop. Collision, absent
supported routes, contact/authority changes and intentionally anchored cover can
still stop travel. Direction reversals also naturally reduce velocity; constant
nonzero speed through every obstacle/turn is not the movement contract.

Reload retains the source ready-pose presentation and finite magazine/timing
logic. This correction does not add a new magazine-handling animation. Source
locomotion assets, historical candidates and owner configuration/project edits
are preserved. These measured checks establish the affected technical behavior;
owner judgement of combat feel and motion remains separate.

## Final closure

Build07 is the final installed Development Editor binary. It differs from the
Build06 runtime candidate only by limiting the live crouched-protection override
to source anatomy users (preserving legacy fixture behavior) and a calibration
provenance comment. The active GASPALS runtime path is unchanged, so its passing
focused evidence is reused. The build guard initially refused while the editor
was still exiting; compilation ran only after normal exit and passed in 8.469 s.

`Saved/GASPALSAIFix01/final-identity.json` records source/binary identity and owner
file preservation. `evidence-manifest.json` fingerprints the retained raw results.
The paired stance calibration and provenance are tracked in
`Scripts/CombatAI01/GASPALSFix01/source-anatomy-calibration.json`.

The controller accepts the authorized correction scope, evidence applicability
and primary finding closure. No production assets or owner configuration/project
bytes were changed by this correction. No new task or external service was used.
