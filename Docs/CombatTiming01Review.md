# CombatTiming01 / MSQ-82 controller review

Reviewed 2026-09-19. The scoped timing implementation and bounded corrections
pass technical/controller review, with the retained low-FPS visual limitation
described below. The final evaluator contains 446 passing checks and no failures.
Scope follows [the task](Tasks/CombatTiming01.md) and
[execution authorization](Approvals/CombatTiming01-OwnerStart01.json).
The [implementation report](CombatTiming01.md) defines clocks, sampling,
collision/history limits and the bounded overload policy. Owner play and visual
acceptance remain separate. No successor is dispatched by this review.

## Calculation and runtime evidence

Evidence is under `Saved/CombatSlice01/CombatTiming01/`, divided into worker
captures and controller/independent review. Controlled frame schedules and actual
input/video observations are identified separately. The controller's independent
Decimal calculation in `Controller/independent-cadence-birth01.json` checks the
85 ms timestamp lattice and analytic residual flight without reusing the native
scheduler recurrence. All nine cadence/hitch/clamp schedules agree. The largest
recorded timestamp error is about 20.6 ns against a 1 microsecond tolerance.

Across controlled 10/30/60/120/144 FPS windows, `[0,2)` contains the same 24 shots
and consumes 24 rounds. At 10 FPS, some frames contain two births. The 50 ms
minimum interval produces 20 shots in `[0,1)`. Exact 150/250 ms hitches and jitter
preserve the schedule. Births at 0/.085/.170 in a 250 ms interval receive only
.250/.165/.080 seconds of flight, with quarter and zero bullet-time variants.
Moving/turning launch poses, near and 2 mm cover, absolute contact ordering and
simultaneous-substep foreground shielding have focused long/fine-step evidence.

Actual captures independently reach the expected 24 shots at all five requested
caps. The observed distinct world-sample rates are approximately 9.99, 30.01,
60.04, 118.59 and 143.37 samples per wall second. These are measured game-sample
rates, not proof of presentation/display FPS; the external videos sample about
12 frames per second. Actual injected hitch deltas were 139.909 and 225.089 ms;
the exact 150/250 ms assertions belong to the controlled probes. A 500 ms wall
stall is delivered as 400 ms by the engine and follows the explicit overload
policy without firing debt.

Independent source and evidence reviews found and closed these bounded defects:

- The post-camera fire montage helper's temporary busy flag suppressed valid
  automatic rounds at 10 FPS. The initial actual result was 20 rather than 24.
  Fire-owned busy state is now cleared without clearing reload/action locks;
  corrected actual footage records 24 shots and 20 bounded presentations.
- A delivered press/release inside one coordinator interval lost its initial
  shot. A timestamped pending press now survives release while later automatic
  intent is cancelled. Same-sample edges cannot bypass minimum spacing. Actual
  Enhanced Input quick-pair observations and native same-interval edge probes
  are separate evidence, not interchangeable claims.
- Reset erased the last accepted shot's cooldown. Correction02 preserves it:
  a reset/new press at .010 after a shot at zero next accepts at .085 or .050,
  depending on tuning. Semi rejects the early tap and accepts the later .090 tap.
- An empty attempt after the last accepted round played a dry montage first and
  suppressed the valid fire presentation. Accepted fire now takes priority in
  that frame. The real 10 FPS montage path changes from one shot/zero fire
  presentations to one shot/one fire presentation, with recoil and a muzzle
  component. A later empty press still plays one dry response.

Capacity recovery accepts only future slots at 0/.510/.595/.680 and conserves
ammunition. Backward in-frame birth probes exclude pre-birth self contact; an
older frozen bullet retains its history through a later birth and hits its
shooter once at .155. The actual clear-space stop/self-contact capture moves the
player 118.89 cm at up to 360 cm/s while stopped bullets keep zero age, travel and
drift. Attribution, quarter/normal resume and reset cleanup pass. Reload transfer,
action/mode barriers, depleted ammunition and reset-safe callbacks are covered
only along affected paths; the complete animation/reload matrix was not repeated.

## Presentation boundary

The controller and independent reviewer inspected actual normal/low-FPS hip/ADS
frames. PurchasedArms06 assets and 90-degree hip / 78-degree ADS tuning remain
unchanged. Multiple accepted rounds share one frame's fire presentation, so
visual recoil/sound/effect counts are intentionally bounded independently of
authoritative ammunition and projectile counts.

Low-FPS held-ADS recovery still has a visible transient receiver/sight displacement
after trigger release. The retained Blueprint clamps recoil-target interpolation
to 16 ms per frame. New pose telemetry measures the predicted target multiplier
of approximately .648 each update at both 10 and 60 FPS: reaching one tenth takes
about .600 versus .100 seconds. Aim remains requested, FOV stays 78, ADS offsets
remain stable and shot counts do not increase after release. This identifies a
retained frame-dependent recoil contribution; it does not prove every visible
difference predates MSQ-82. Random recoil, montage phase and the new post-camera
presentation order also limit a causal pixel comparison. No unrelated arms
retuning or claim of identical low-FPS visuals is part of this acceptance.

## Preservation and final handoff

`Controller/final-source-review01.md` closes the last cooldown and final-round
findings against exact source/evidence hashes. `Controller/final-evidence-review01.md`
independently checks capacity, birth/history, actual input, stopped own bullets,
final-round presentation and the ADS diagnosis. Earlier reviews and failed
captures remain preserved. Unchanged paths reuse earlier labelled candidates;
the final correction is not misrepresented as a fresh run of the entire matrix.

`Controller/final-handoff-file-check.json` verifies 376 candidate, evidence,
native binary, owner-config and manifest entries with zero mismatches. The
worker's final source/report manifest is unchanged. Its preservation inventory
checks 1,427 starting paths: no missing files, and only four existing native
rifle/projectile files changed. The controller separately confirms that the
owner's `Config/DefaultEngine.ini` still has its starting SHA-256. Content,
retained lobby, PurchasedArms06 presentation, original character sources and
MSQ-68 reports/evidence remain unchanged. No binary asset or registry revision
is needed. Storage measured 28,481,030,612 bytes, below the 250 GB cap.

`Worker/Correction02/build01.log` records a successful UE 5.8.1 build.
`Worker/editor-state-Correction02FreshLoad.json` and `handoff-Complete02.json`
verify the retained lobby, clean packages, stopped PIE, no leaked prototype
actors and restored performance settings. The worker editor ended with the run.
A separately launched owner editor then opened this project; the controller's
read-only official Epic check observed active PIE. That owner session was left
untouched; no duplicate editor was launched and no gameplay reset/stop was sent.
See `Controller/post-run-editor-observation01.json`.

Multica run `01a0b6b7-4d8f-79ca-ab7f-8ed19fa960d1` completed with one production
worker. Saved profile/native arguments and actual execution verify Astra/max,
default service tier, disabled fast mode and subscription login. Independent
reviewers used Astra/max under the standard-speed configuration; their native
turn contexts report no separate service-tier override. The final worker profile
and arguments match the starting settings, retaining max. Three queued comment
notifications were cancelled after their work was incorporated into the active
run; none executed. The issue is unassigned for administrative closure, and
successors remain undispatched. The controller closes MSQ-82 and makes its
task-scoped local commit; the owner config edit stays outside that commit.

The supported reconstruction interval is at most 250 ms. Work caps are 32
substeps, six birth attempts, the retained maximum 256 active bullets and one
fire presentation per frame. An unsupported interval or detected history barrier
retires old bullets, drops the interval, disarms fire and requires a new press;
it neither applies skipped damage nor refunds ammunition. Endpoint interpolation
cannot reconstruct arbitrary moving geometry, out-and-back motion or unseen
topology changes. These documented limits are part of the prototype contract.
Player health, a player-facing time ability and enemy work remain later tasks.
