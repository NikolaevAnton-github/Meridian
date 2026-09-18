# PurchasedArms05 controller review

2026-09-18. MSQ-65 passes focused implementation and controller review after two
bounded corrections. Ordinary and Shift jumps accept ADS and shooting immediately
after takeoff. Alt tactical sprint rejects jumping. Landing presentation follows
physical floor contact. See [implementation and evidence](PurchasedArms05.md).

## Verified behavior

- The original clip's contact sound at 0.392494 seconds and impact dip around
  0.40-0.50 previously played before the 0.65 hold. The new 0.30 flight hold and
  collision-triggered 0.38 recovery preserve airborne presentation, including
  a measured 1.24-second extended fall. Actual selected frames show the impact
  after contact. Ordinary/Shift takeoff settings remain 320/352 cm/s; measured
  apex rises remain about 52.24/63.21 cm. Shift flight retains 540 cm/s after release.
- Input-driven ADS and shots were observed on the next sampled game frames,
  about 8.3-12.2 ms after airborne requests. Ammo decrements, firing presentation,
  casings/effects and evaluated poses support actual action execution. Automatic
  fire continues through contact; ordinary, held/released Shift and aim-only
  cases retain usable alignment and recover naturally after input release.
- Alt rejects Space on initial press, its activation boundary and established
  sprint. The subsequent ordinary and Shift jumps work after release. A later
  ordinary jump resets the boost. Extra airborne Space does not add a jump.
  A shared busy-ownership check retains another weapon action's lock through landing.

## Independent findings and corrections

The initial candidate fired and aimed successfully, but actual held/released
Shift ADS frames showed the rifle tilting away from the sight line after contact.
Independent raw-sample review confirmed ADS and fire remained held while Run End
reached full blend weight. Correction01 protects the compatible pose through held
weapon actions and reconciles released/held movement intent after input callbacks.
The corrected actual views remain aligned; the identified Run End player's weight
is zero through those held actions. Running resumes after release, or walking when
Shift was released. Initial failed views are preserved and excluded from acceptance.

Source review also found that an input request canceled before movement could
leave presentation stuck on the ground. Correction02 starts presentation only
from confirmed `OnJumped`, with explicit pending-request cancellation. A real
same-frame Space down/up leaves running available with no takeoff, pending state
or jump montage. The next press produces a confirmed Shift takeoff about 58 ms
later, immediate airborne ADS/shot, physical landing and clean release. This one
focused case verifies the changed lifecycle; earlier passing cases were not swept
again. Independent source and raw-evidence review resolve the cancellation finding.

Read-only independent reports, source hashes and actual max-reasoning receipts
are under `Saved/PurchasedArms05/Controller/`: `source-audit.md`,
`code-review-initial.md`, `visual-evidence-review.md`, `correction01-review.md`
and `correction02-review.md`. The controller also inspected the actual initial
and corrected contact sheets. These are sampled visual checks, not an every-frame
or hardware-latency guarantee; silent recordings are about 12 fps and clock
quantization limits frame/sample matching precision.

## Preservation and closure

Correction02 builds and loads in a fresh editor. The existing seven graph guards
and heading-independent ADS conversion remain intact. The scoped editor-log check
finds no relevant script, Blueprint or load errors. The retained lobby is left
open with PIE stopped and no dirty content/maps.

All 1,419 starting preservation files remain present. Only three native source
files differ in that set: the character implementation/header and the animation
telemetry implementation. All Content packages, the retained map, original/vendor
sources and configuration retain their starting hashes. No binary revision or
registry rebaseline is needed. New task scripts reuse the existing input/MCP/capture
utilities; generated recordings, telemetry and rollback data remain under Saved.

The Multica executor's configured/native settings are Astra/max/default with fast
mode disabled. Actual turn context confirms Astra/max; its tier field is null,
so native arguments are not presented as proof of stronger server routing. No
profiles changed and production concurrency stayed one. Both comment-triggered
follow-up runs were canceled before execution after their findings were incorporated
into the original run; there was no redundant production run.

The controller owns Multica closure and the required task-scoped local commit.
This is scoped technical and visual verification, not owner art acceptance or
authorization to resume paused character/environment work.
