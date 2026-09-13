# MSQ-3 controller acceptance

Accepted on 2026-09-13. One Multica Astra worker implemented the registry and
completed one review follow-up, using subscription authentication, medium
reasoning and standard speed. No DCC connections, asset regeneration, new
services or paid APIs were used. The controller reviewed and verified the
result; one bounded independent reviewer inspected the code.

The separate PostgreSQL database `meridian_assets` contains 3 assets,
48 artifacts and 59 dependencies: PipelineProbe (12/13), BenchA (18/23),
and BenchB (18/23). Inspect returns source files, exported maps, Unreal package
paths and relationship evidence. Dependencies retain verified, declared or
unverified status. See [usage and limitations](AssetRegistry.md).

## Verification

The controller ran `Scripts/AssetRegistry/acceptance.py`,
`Scripts/AssetRegistry/review_regressions.py` and the saved read-only privilege
audit after both Multica runs finished. All passed:

- Repeated migrations and seed registration preserve inventory counts.
- All three accepted assets validate successfully.
- Changed/missing temporary files identify downstream paths; uncertain edges
  and stale evidence preserve uncertainty. Accepted hashes cannot be silently
  replaced by registering a new fingerprint.
- SQL quotes/dollar tags remain data. Both PostgreSQL clients discard inherited
  libpq parameters. Case variants, hard links and junction aliases are rejected;
  a second migration prevents case-only path duplicates without changing IDs.
- All 46 protected asset/config files and the Multica application schema match
  the pre-task baseline. The asset role cannot write Multica schemas/tables,
  create objects in that database, or inherit another role's permissions.
- An asset-only custom-format backup was created and its archive listing read.
  Full disaster recovery has not been tested; same-disk dumps are local copies.

Full evidence is ignored under `Saved/AssetRegistry/Acceptance`, including
`controller-acceptance.log`, `controller-regressions.log`, `results.json`,
`review-regressions.json`, `isolation.json`, and `protected-result.json`.
Temporary fixture files and database rows were removed by the checks.

## Worker usage

Native response records were counted once per response, assigned to each run
by the native turn's start time. This avoids counting the resumed follow-up
again through a shared session and a tolerant timestamp window. Both totals
reconcile with Multica's adapter representation.

| Run | Wall time | Input including cache | Cached input subset | Output including reasoning |
| --- | ---: | ---: | ---: | ---: |
| Implementation | 11m 54s | 937,408 | 875,008 | 17,757 |
| Review corrections | 4m 20s | 874,358 | 849,152 | 6,734 |
| Total | 16m 14s | 1,811,766 | 1,724,160 | 24,491 |

Uncached worker input was 87,606 tokens. Native total was 1,836,257 tokens;
3,445 reasoning tokens are already included in output. Cached input must not
be added to input again. Multica 0.4.43 adds reasoning again in its output field,
so its displayed output is not the canonical native output.

Complete worker-run evidence is in `Saved/AssetRegistry/Multica/native-usage.json`
and `native-usage-details.json`. These counts exclude controller/reviewer work
and cannot be converted into exact subscription dollars or quota consumption.
The earlier worker-created acceptance usage snapshot is a partial cutoff and
is superseded by these completed-run totals.

The controller and reviewer snapshot at 13:16:01 UTC covers this user request
from 12:54:51.503 UTC: 5,292,803 input tokens, including 5,100,288 cached;
192,515 uncached input and 26,232 output tokens. This is separate from worker
usage and is a lower bound while final documentation/publication continues.
Evidence: `Saved/AssetRegistry/Multica/controller-usage.json`. Controller context
and verification are a substantial part of this task's usage; worker usage
alone would understate the cost of the accepted result. Future routine tasks
should use shorter controller context and fewer status reads while retaining
the acceptance checks.

The first version required review corrections; this is one accepted task with
rework, not evidence of a general Multica efficiency advantage. The next stage
is to use this registry during real asset work and measure acceptance/rework
across 10-15 bounded tasks using existing validators.
