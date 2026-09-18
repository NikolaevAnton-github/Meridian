# PurchasedArms04 controller review

2026-09-18. MSQ-64 passes its bounded implementation and controller review after
one presentation correction. Shift + Space now produces a higher, farther jump
with coherent airborne/landing presentation. This is technical and scoped visual
verification, not a new owner art acceptance or permission to resume paused work.

## Verified result

- Ordinary takeoff remains 320 cm/s. Established fast movement uses 352 cm/s;
  stationary Shift grants no boost. Actual horizontal momentum is retained without
  a dash, including when Shift is released in flight. Landing resets the settings.
- Controller analysis of the final existing recordings measures about 52.24 cm
  apex / 240.25 cm travel for ordinary movement and 63.20 cm / 392.14 cm with
  Shift held. Released Shift preserves 540 cm/s through flight, then a subsequent
  ordinary jump returns to 52.24 cm at 360 cm/s. Sampling explains centimeter-scale
  travel differences between takes. Alt shares the same vertical multiplier.
- Initial focused cases cover stationary Shift, airborne repeat input, busy and
  crouch gates. Only ordinary/held Shift/released Shift/Alt jump transitions were
  recaptured after the presentation correction. No full animation, action, ADS,
  shooting, reload or traversal matrix was repeated.

## Review correction and evidence

The first candidate passed physics but layered the idle-authored additive jump
over the lowered run pose, almost removing the rifle from view. Controller frame
inspection and an independent source/visual review identified this defect. The
initial captures and report remain preserved and do not count as visual passes.

The final native animation snapshot uses a compatible base until the actual jump
montage has no activity or blend weight, including paused flight and landing
blend-out. Seven AnimBP transition guards suppress fast poses and run-end overlap
only during that interval. Independent review reconstructed the saved pin links
and confirmed that inactive guards reduce to the original transition expressions.
Physical movement flags remain independent. The prior ADS basis conversion is
preserved and verified by the fresh-load graph contract.

Controller and independent reviewer inspected actual corrected flight/landing
frames. The rifle stays visible in the previously failing interval. The lower
recovered run pose matches the pre-jump run loop in existing evaluated data;
it is not residual jump stacking. This is sampled frame/evidence review, not a
claim of continuous-video or every-frame inspection. Full findings, actual
Astra/max/standard receipts, frame extracts and independently computed trajectory
summaries are under `Saved/PurchasedArms04/Controller/`.

Native build, warnings-as-errors AnimBP compilation and fresh editor load pass.
`Worker/Correction01/log-check.json` records no relevant runtime/load errors;
`editor-state-correction01-handoff.json` records the retained lobby, PIE stopped
and no dirty maps/assets. All 1,419 original preservation files remain present;
only four native files and the one adapted AnimBP differ in that preservation set.
The map, vendor source, original character sources and other Content are preserved.
The final worker inventory includes the small reused-capture adapters and report.

`Assets/Source/PurchasedArms04/source-manifest.json` records the new binary revision
over PurchasedArms03. Its separate registry manifest inventories this revision
without changing historical fingerprints. The changed asset retains Git LFS.
No profile changes were required; production concurrency remained one. The
nonessential source-audit notification run was cancelled before execution.

The owner's future focused-verification instruction is recorded in AGENTS.md and
`Docs/Approvals/FocusedVerification01.json`. Controller owns Multica closure and
the required local MSQ-64 commit; generated evidence stays outside Git.
