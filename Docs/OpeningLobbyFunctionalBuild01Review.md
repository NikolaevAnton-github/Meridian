# LobbyFunctional-Build01: verified production and owner edit

**The MSQ-20 worker candidate passed fresh MSQ-21 visual and technical review.
All ten criteria passed; no required correction remains. The owner subsequently
edited the current map and confirmed authorship in direct chat. That edit is
preserved. The review applies to the prior worker bytes, not the edited map.**

The current map is `/Game/Maps/L_OpeningLobby_FunctionalBuild01`. The controller
reopened it after the worker process ended; the owner then made the recorded edit.
No controller operation overwrote that edit or reset the editor. See the
[owner-edit record](Approvals/LobbyFunctionalBuild01-OwnerEdit01.json).
Its observed SHA-256 is a dated snapshot, not a restriction on further owner edits.

Implemented from the approved FunctionalRevision02 package: four terminal rooms
to the outer walls, transverse entrance service doors and hall-facing inner doors,
stepped room roofs, four 2.4 x 2.4 x 18 m columns, two 1.5 m checkpoint lanes and
a 3.6 x 4.2 m elevator with opaque upper wall. Remaining ReworkA01 architecture
and the 60 x 24 x 18 m hall scale were preserved in the reviewed worker version.

## Reviewed version and evidence

- [Whole hall and four new columns](../Saved/OpeningLobby/FunctionalBuild01/Worker/context-90.png)
- [Entrance and checkpoint](../Saved/OpeningLobby/FunctionalBuild01/Worker/entrance-90.png)
- [Inner end and elevator](../Saved/OpeningLobby/FunctionalBuild01/Worker/inner-90.png)
- [Service-door approach](../Saved/OpeningLobby/FunctionalBuild01/Worker/aisle-90.png)
- [Independent verdict](OpeningLobbyFunctionalBuild01Review.json) and
  [complete review](../Saved/OpeningLobby/FunctionalBuild01/Review01/report.md)
- [Frozen worker handoff](OpeningLobbyFunctionalBuild01.md)

These captures document the worker version before the owner edit. It has 17
editable modules and 20 new assemblies. Verification covered 201 construction/
import checks, 65 schedule comparisons, 66 actual profile traces, 13 native
1920 x 1080 captures and 2,267 real movement samples across the full route and
focused elevator recheck. The reviewer independently audited images, source,
measurements, movement and exact identity. Geometry received a 2 mm elevator
meeting-edge refinement during author QA; no post-review geometry correction
was required.

The inner end seam was examined in detail. Actual retained bands are 2 cm thick,
X29.97..29.99. A 1 cm rear cavity and the 3 cm rear space behind the new aisle
cap lie outside the closed room envelope and create no room opening or walking
bypass. The inner shell component is 10.17 m long after a concealed back-face
trim; 10.2 m is the gross assembly datum. This clarification supersedes the
imprecise prose in the unchanged frozen worker handoff.

| Reviewed artifact | SHA-256 |
| --- | --- |
| Worker manifest, 116 entries | `63b7d7030310d948d64efbe453b4016edb41e62b8987154da257da5f1380654f` |
| Worker map before owner edit | `9990d2ca10a62a32fcb7d7e38fb324e84d6f52e406601b74ce9689c6b6d08894` |
| Historical archive | `b4eea02a7bdd7785548d6c0bd930d2279a96c76b4c0315dc57d19da2c4f2b48b` |

The exact reviewed files, including the original map and manifest, are retained
in `Saved/OpeningLobby/FunctionalBuild01/Controller/WorkerCandidate01.zip` (31.61 MB). The active manifest
is historical for the map: its map entry intentionally differs after the owner's
edit. Do not rebaseline it or copy the old map over the current one. The other
115 entries still match, and all 408 controller-protected original files matched
before these final administrative documentation updates.

Both runs used Astra/high/standard with the assigned production/review skills,
existing subscription authentication and Multica concurrency one. Profiles are
restored; no run remains active. Native usage excluding controller/helpers:
628,327 uncached input, 7,349,760
cached input, 54,804 output; 11,812
reasoning tokens are included in output once. Worker-reported storage growth was
36.3 MB, plus the controller's 31.61 MB historical archive; project storage remains
well below 250 GB.

MSQ-20 is in review for the owner; MSQ-21 is done. The FunctionalRevision02 drawing
gate (MSQ-18) is closed. MSQ-6 remains incomplete and MSQ-7 backlog. Confirmation
of the owner's edit does not grant final 3D/atmosphere acceptance. No further
geometry run, registry update, commit, push or default-map change was dispatched.
