# PurchasedArms01 controller review

MSQ-61, 2026-09-18. The owner's temporary scope replaces active original-protagonist
production with purchased first-person arms, one rifle, walking, aiming and reloads
in the retained lobby. The implementation report is [PurchasedArms01](PurchasedArms01.md).
Owner visual acceptance remains separate from this technical handoff.

## Scope and preservation

The old MSQ-54 run was canceled and its Blender calculation ended. MSQ-50/54 are
parked in backlog, and MSQ-55 through MSQ-60 remain undispatched. Original artwork,
owner exports, experiments, source helpers and exact review evidence are preserved
as inactive history. The exact preceding project-state snapshot is archived.

Independent preservation review verifies the 87-package hard dependency closure,
zero missing hard references, and the mapping of 125 archived packages to their
baseline hashes. These comprise 26 original-character development packages, 44
template audit packages and 55 unused purchased packages. All archived bytes remain
under Assets/Archive/PurchasedArms01; the source vendor project is untouched.
Five optional preview soft references remain documented. Existing native registry
rows are historical and have not been rewritten to accept different bytes or paths.

The lobby map SHA-256 is unchanged:
`b28fa0f6e8bb80dcc71b4789df9c3e2375a3cf8b1da67021225584e4560fd92f`.
Targeted comparison also confirms the owner's original FBX and unrelated Config
files unchanged. The controller stages only this task's changes; pre-existing
working edits and untracked original-character work remain outside the closure commit.

## Verification

Technical and independent scoped review: **PASS**. Build05 compiled the final
native correction. The initial implementation blended the visible replacement
magazine toward its stored reference position during the last 0.15 seconds.
The correction preserves its authored seated transform through this fade, then
returns visibility to the seated main magazine.

The final `Worker/Correction03` run passes five reload scenarios: hip, aimed,
queued aim, moving hip and moving aimed. Independent review recomputed 37 distinct
active sample times inside the fade across those cases, with maximum seated
position error 0.02034085 cm, rotation difference 0.00039847 degrees and zero paired
animation-clock difference. The latest hip sample reaches 3.666081 seconds, just
before completion. Recovery has one seated main magazine. Actual idle, ADS,
handling, late-fade and recovery images show coherent framing and no new issue.
The magazine is mostly outside the camera at late fade; the transform comparison
is the decisive R1 evidence, not the screenshot alone.

The changed native code did not require repeating the previously passed route,
pruning or broad preservation tests. Correction01/02 are preserved incomplete
capture attempts; their scripted results are not used to certify fade coverage.
Independent findings and exact reviewed identities are in
`Saved/PurchasedArms01/Controller/final-review01.md` and
`preservation-review01.md`. The controller separately viewed final hip/aimed
late-fade captures. This closes the concrete review finding without broadening
the walkthrough scope.

The fresh-editor load passed for all 87 retained packages. Actual controller input
verified walking, looking and wall collision; action tests cover ordinary/aimed
reloads, queued aim changes, repeated R suppression and moving recovery. All seven
presentation components have dynamic, static, hidden and contact shadow flags
disabled. There is no body or vendor combat/inventory/showcase gameplay.

The worker used Astra/max/standard, confirmed from the native session and actual
process flags. The independent reviewer was configured for Astra/max/standard;
its own native process/session receipt was not exposed in the collaboration
interface, so that assignment is not independently verified speed evidence.
Generated logs, native
telemetry and screenshot evidence remain in Saved/PurchasedArms01.

This is local PIE/editor validation; no packaged-build or multiplayer acceptance
is claimed. It does not accept any paused original-protagonist candidate.

## Inventory and final state

The exact runtime/configuration, active package and archive identities are bound
by Assets/Source/PurchasedArms01/runtime-manifest.json. The PurchasedArms01 registry
manifest covers new runtime/report files and archived package locations. Existing
active art and project-descriptor registry identities retain their previous owners;
cross-asset graph revision is outside the existing registry CLI. The new manifest
documents these limits instead of silently rebaselining old rows.

Registration, inspection and validation outputs are retained under
`Saved/PurchasedArms01/Controller/registry-*.json`; the exact manifest is
`Scripts/AssetRegistry/manifests/PurchasedArms01.json`. Registration is inventory,
not owner visual acceptance or acceptance of archived protagonist candidates.

The final editor evidence names the retained lobby, PIE stopped, no dirty content
or map packages and the native OpeningLobbyGameMode. Temporary test timing and
background-throttling settings were restored. The editor is left ready for Play.
Task execution/profile cleanup and the local task-scoped closure commit are owned
by the controller; Multica remains the source of current task status.
