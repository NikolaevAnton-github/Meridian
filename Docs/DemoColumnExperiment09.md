# DemoColumnExperiment09

[Owner direction](Approvals/DemoColumnExperiment09.json): raise the shared retained
debris limit to 80 and distribute it flexibly around the column. Baseline
`c0c53b7` preserves the preceding candidate. Direct implementation without tasks,
Multica, agents or independent reviewers under the continuing owner waiver.
The owner accepted the result and requested the local commit.

## Behavior

Correction08 keeps its existing assets, large-piece size, outward scatter,
protected core and matching ceramic fractures. Only retention allocation changes.

Four sectors use settled positions in column-local XY space (+X, +Y, -X, -Y).
Each has a soft share of 16 pieces, with 16 further places shared. Empty sectors
lend all unused places. The cap is 80, including pending concrete freezes; at
most 48 pieces are ceramic, leaving 32 places available for concrete. The active
ceramic cap remains 32 and unretained debris still expires after 12 game seconds.

When the relevant cap is full, a settling piece may replace a retained piece
from a more populated sector. Donors keep at least their 16-piece base share; the
exchange must reduce the population difference. Ceramic-only saturation also
requires improving ceramic distribution. Shared places therefore follow actual
settling debris instead of being permanently assigned to the first impacts.

Within eligible donor sectors, selection prefers pieces behind the camera,
ceramic over concrete, and smaller pieces. At most two replacements happen per
quarter-second poll. Grounding rays against each proposed victim protect retained,
pending and loose debris resting on it. If no safe victim exists, replacement
waits for another opportunity rather than deleting a support. Old pieces are
removed; this is neither geometry merging nor an opacity-fade implementation.
Before a ceramic piece is frozen, a penetration check against retained ceramic
rejects deeply overlapping near-parallel plates. Rejected pieces remain dynamic
to settle again or expire normally, instead of preserving an intersecting pose.

## Verification

Build, probe evidence and fingerprints are stored under
`Saved/DemoColumnExperiment09/` (excluded from Git).

- Development Editor build `compile03` passed and was loaded in a fresh editor.
- `distribution02` fired 150 real rifle shots with no dry fires. A sector borrowed
  up to 49 places. The shared budget reached 80 and later-side impacts rebalanced
  it to `[20, 20, 20, 20]`, including 48 ceramic and 32 concrete pieces.
- The distribution probe performed 69 replacements and recorded 130 rejected
  deletion attempts that would have removed a support. No sampled retained
  bodies lost support or resumed dynamic simulation. Core movement, debris
  inside the core, unsupported wall facing, facing remaining on landed carriers,
  invisible retained concrete and deep retained ceramic overlaps all stayed zero.
- Both the 80-piece shared cap and 48-piece ceramic cap passed, with at most 32
  active ceramic pieces. Sector sums also matched retained plus pending bodies.
- F6 cleared loose, carried and retained debris, reset allocation counters and
  restored all 1,560 facing instances.

An earlier focused negative-Y probe found one deeply intersecting retained tile
pair. Retention had checked stillness and support without checking penetration;
the new admission guard rejects that pose. The early long probe also exhausted
its stock ammunition; the reusable helper now explicitly provisions its 150-shot
loadout and checks that planned presses became actual shots. Earlier evidence is
preserved separately, including `probe-notes.json`.

`distribution02-analysis.json` and `distribution02-balanced-pile.png` record the
final distribution checks and view. These are functional probes, not an FPS
benchmark. Increasing stationary debris from 50 to 80 still adds rendering and
collision/query work; it does not increase the active ceramic simulation cap.

Supplemental isolated probes after the passing distribution run did not reliably
produce their requested shots and are excluded from acceptance. Native debugging
reached `CombatRifleComponent.cpp:183` through Enhanced Input with `bFrameCanFire`
true, `bReloading` false and 55 recorded shots; a subsequent read reported 56.
The missing supplemental inputs were not reproduced at that stop, so their cause
remains unproven. No weapon code was changed. The temporary breakpoint was removed,
the debugger detached, and all eight original exception breakpoints (five enabled)
were preserved. Evidence: `debug-rifle-input.json`. Acceptance uses the successful
150-shot distribution probe and its complete reset, not these supplemental runs.
