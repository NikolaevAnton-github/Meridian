# GASPALSEnemy01 controller acceptance

Date: 2026-09-23. Related existing task: MSQ-98. This direct follow-up creates no
Multica issue or runtime and follows the [owner request](Approvals/GASPALSEnemy01-OwnerStart01.json).

**PASS for authorized delivery, candidate identity, applicable evidence and
registry inventory. Owner motion/play judgment remains separate.**

## Delivered scope and evidence

The [implementation handoff](GASPALSEnemy01.md) supplies controls and limits.
All three existing fixtures receive the selected rifle presentation, independent
aim/movement and actual crouch. Current physical transitions and owner corrections
remain in place. Autonomous combat, firing, disarming, wound gestures and the
deferred terrain/balance tasks retain their separate scope.

The [sole primary technical review](GASPALSEnemy01Review.md) passes with R1-R4
closed. The controller accepts its focused build, actual-view and transition
evidence without a second technical review or redundant gameplay runs. The
reviewer inspected extracted actual frames; continuous playback and subjective
motion approval are not claimed.

Candidate01 identity SHA256:
`6fe8152f99de22dc832c6c5b5259f670e8f326a51bfaa1060a87c07c7e7d5e32`.
Controller checks match all 26 candidate/current entries and all 16 active
package identities in the revision manifest. Evidence is
`Saved/CombatSlice01/GASPALSEnemy01/Controller/identity-acceptance01.json`.
The reviewer separately matched 42 source/candidate/archive/preservation entries.
The post-freeze authoring-script docstring correction is explicitly reviewed;
it changes no behavior or candidate asset/native bytes.

## Registry and preservation

[Registration input](../Scripts/AssetRegistry/manifests/GASPALSEnemy01.json)
contains 19 artifacts: 15 new derivative packages, the plugin descriptor, exact
pre-edit AnimBP archive, rejected copied-class archive, and the
[revision manifest](../Assets/Source/GASPALSEnemy01/source-manifest.json).
Registration, inspection and validation pass in the existing local
`meridian_assets` database. Reports are under the same Controller evidence folder
as `registry-register.json`, `registry-inspect.json` and `registry-validate.json`.

The registry's old canonical AnimBP fingerprint remains historical. It is not
replaced with the new bytes; its current revision is recorded through the new
manifest and separately verified identities. Validation of this new inventory
does not claim that the old canonical fingerprint still matches the edited path.
No database rebaseline or historical evidence rewrite was performed.

All 15 imported source fingerprints remain unchanged. The pre-edit archive
matches the historical accepted fingerprint
`4be002ac82435201716c18fbe6e1ec83624515dbe823548c2bcfcc2131b8b963`.
Owner `Config/DefaultEngine.ini`, `MeridianSquad.uproject` and retained lobby map
match their initial hashes. The two already-modified owner files are excluded
from the closure commit. Original failing experiments and recordings remain
preserved. Binary assets use Git LFS; generated evidence stays under Saved.

## Execution and handoff

One native writer owned production and the editor. The independent reviewer and
bounded source helper used read-only evidence. Native turn contexts confirm
Astra/max. Local configuration selects the default service tier and no fast
override was requested; native turn context does not expose a response tier.
Execution metadata and native logs are preserved in the Controller folder.
Only administrative Multica database/API/web services were started for registry
access; the task runtime remains stopped.

Build11 is loaded in the lobby editor with Play stopped and no dirty packages or
transient fixture/controller leftovers, as recorded in `final-editor-state.json`.
The source plugin is not mounted and the targeted fresh-editor error scan is
clean. The owner can start Play and use the documented console controls. A
shipping cook, replication and autonomous enemy combat were outside this scope.
