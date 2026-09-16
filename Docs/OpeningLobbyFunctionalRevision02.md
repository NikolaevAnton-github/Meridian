# LobbyFunctional-Revision02: owner-approved drawing package

The owner approved this latest package and instructed us to start on 2026-09-14.
The [external decision](Approvals/LobbyFunctionalRevision02-Production01.json)
binds that approval to the unchanged manifest below, including all dimensioned
room/door/roof, column/sightline, checkpoint/elevator and route deltas. Follow
[the separate neutral 3D task](Tasks/OpeningLobbyFunctionalBuild01.md).
The following drawing-stage handoff is historical; its pending-owner wording
does not override this later decision. Resulting 3D quality awaits walkthrough.

**LobbyFunctional-Revision02/Candidate01 passed fresh MSQ-19 visual and technical
review. No required correction remains. The named 2D package awaits owner approval
of the proposed dimensions and their visual result before separate 3D production.**

The owner's yellow markup corrected the rejected FunctionalRevision01 interpretation.
See [the owner record](Approvals/LobbyFunctionalRevision02-OwnerMarkup01.json) and
the [unchanged marked plan](../Assets/Concepts/OpeningLobby/FunctionalRevision02Inputs/OwnerMarkup01.png).
MSQ-18 built this focused revision; its earlier draft camera issues were corrected
within the initial run. MSQ-19 formed an image-first judgement in a fresh context
and required no additional correction. Both used Astra/high/standard, existing
subscription authentication and concurrency one. Assigned analysis/review skills
were explicitly applied; the prior local drawing and verification tools were reused.

## The five sheets

- [Corrected plan alongside the owner's markup](../Assets/Concepts/OpeningLobby/FunctionalRevision02/01-plan-markup.png)
- [Rooms, door orientations and roof closure](../Assets/Concepts/OpeningLobby/FunctionalRevision02/02-rooms-closure.png)
- [Retained checkpoint and elevator proposals](../Assets/Concepts/OpeningLobby/FunctionalRevision02/03-retained-functions.png)
- [Four ceiling-height columns and passage dimensions](../Assets/Concepts/OpeningLobby/FunctionalRevision02/04-columns-passages.png)
- [Entrance, inner end, full hall and service-door approach](../Assets/Concepts/OpeningLobby/FunctionalRevision02/05-spatial-context.png)

[Full dimension schedule and reproduction](../Assets/Concepts/OpeningLobby/FunctionalRevision02/README.md),
[independent verdict](OpeningLobbyFunctionalRevision02Review.json), and
[complete review](../Saved/OpeningLobby/FunctionalRevision02/Review01/report.md).

Four corner rooms now extend to the outer walls, with proposed gross footprints
10.2 x 6.4 m. The old terminal aisle bypass is closed. Entrance service doors
are in transverse caps X=-19.8 facing the remaining corridors; inner stair-access
doors face the hall and inner caps are blind. No obsolete partition remains at
|Y|8. Existing terminal piers are integrated into the room boundaries.

Four new columns are proposed at X=+/-12.6, Y=+/-2.4, section 2.4 x 2.4 m and
height 18 m to the main ceiling. They leave a 2.4 m axial passage and 2.0 m gaps
to the original shafts. Their strong narrowing of the axial view is visible on
sheet 05C and remains an owner design judgement. Existing floor strips stay in
place beneath the new shafts. The original hall scale and remaining A architecture
are retained. Two 1.5 m checkpoint lanes and the 3.6 x 4.2 m elevator/opaque upper
wall remain carried-forward proposals; they have not acquired separate approval.

## Exact identity and verification

Manifest: `Assets/Concepts/OpeningLobby/FunctionalRevision02/manifest.json`. SHA-256:
`440064e9a1df1180cec92cc3e43be78034b7de30a6e94ef94d0a9d0534b0ecd1`. All 35 entries match. The original markup and all
377 controller-protected baseline files remain byte-identical, checked after
runtime restoration and before these administrative documentation changes.

Independent review passed 256 checks, 15 analytic routes / 12,041 samples,
actual full-height ceiling contact and source consistency. An in-memory audit
reproduced all five SVGs plus drawing bounds and related outputs exactly. These
are drawing/analytic checks, not Unreal player movement or collision evidence.
New package plus worker evidence occupy 7.37 MB.

Native MSQ-18/19 usage, excluding controller/helpers: 225,410
uncached input, 2,196,352 cached input, 31,526
output; 4,361 reasoning tokens are included in
output once. Evidence lives under Saved/OpeningLobby/FunctionalRevision02/.

No Unreal/DCC mutation, new 3D asset, configuration/default-map change, registry
update, commit or push occurred. The ReworkA01 map hash remains
71cfc087c80510313054255d784d1b43c45395d6400c9e0b75e9f64d7be944d0.
Profiles were restored and no run remains active. MSQ-18 is in review; MSQ-19 is
done. MSQ-16 is cancelled as the owner-rejected interpretation superseded by this
revision; its package and MSQ-17 review remain historical and unchanged.

The concrete next gate is approval of this named package, including regularized
room/door dimensions, column thickness/spacing and visual density, roof junctions
and retained function dimensions. No room/stair interiors, cab/shaft, operation,
branding or final atmosphere are designed. Follow
[the revision task](Tasks/OpeningLobbyFunctionalRevision02.md) after that decision.
