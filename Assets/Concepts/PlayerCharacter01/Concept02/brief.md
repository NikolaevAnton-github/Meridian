# PlayerArt-Concept02 / Candidate01

MSQ-51 artist preparation, 2026-09-16. Ten new proposals, IDs 16-25, continue
the owner's preference for Concept01 01 (Cutline) and 08 (Overlap). The owner
alone evaluates the resulting art; this direction does not approve modeling.

## Sources and visual observations

Read `Docs/Tasks/PlayerArtConcept02.md`, `Docs/Design/StoryCanon.md` and
`Docs/Design/GameBrief.md`. Inspected both actual images with `view_image`:

- `Assets/Concepts/PlayerCharacter01/Concept01/01.png`: segmented rounded crown,
  broad opaque visor, separate angular jaw, clipped rectangular front/back
  carriers, graphite clothing with subdued olive panels and compact belt storage.
- `Assets/Concepts/PlayerCharacter01/Concept01/08.png`: faceted crown, narrower
  opaque visor, diagonal overlapping jaw and breastplate, an offset lower torso
  flap, olive jacket, dark trousers and restrained belt storage.

Both show athletic human proportions, textile space around joints, closed gloves
and boots. Continue their construction language with added protective surfaces;
do not copy either reference unchanged or borrow another property's character.

## Fixed constraints and proposal boundaries

- Original MERIDIAN operative, 2043, realistic dark near future. Face, eyes and
  skin remain concealed in every external view. Keep the silhouette human and
  mobile, with compact shoulders and shallow plate thickness.
- Make added armor legible on chest, back, flanks, abdomen, outer shoulders,
  forearms, thighs, knees and shins. Preserve textile flex zones at neck,
  armpits, elbows, waist, hip creases, knees, wrists and ankles. Leave a clear
  rifle-stock seat at each shoulder; hands are empty in these sheets.
- Graphite composite, muted olive/ash fabric, dark gloves and practical boots.
  Sparse low belt storage, readable large plate forms, subtle wear. Avoid bulky
  shoulder caps, rigid limb tubes, armor skirts, exoskeletons and powered armor.
- The owner specified a helmet computer that displays the local interface.
  Integrate it into a small temple or occipital volume, with recessed service
  seams and display optics protected behind the visor. No exposed cables,
  external holograms, luminous face or conspicuous electronics boxes.
- Abilities belong to the protagonist; equipment does not explain them.
  Command remains unreachable after isolation. Do not invent target detection,
  anomaly sensing, mission orders, telemetry, performance or UI mechanics.
  All construction details and HUD layouts below are exploratory proposals.

## Ten-design matrix

Every row inherits the complete coverage and mobility requirements above.
Differences are helmet construction and major armor architecture, not palette.

| ID / name | Reference emphasis | Helmet and integrated computer | Armor architecture and articulation |
| --- | --- | --- | --- |
| 16 / Datum | Cutline | Broad visor under a separate central crown strip; paired shallow jaw panels; flush temple service pocket. | Cropped octagonal breast/back plates, three separate abdominal bands, sliding flank leaves; single tapered thigh plates and separate knee/shin pieces. |
| 17 / Traverse | Overlap | Offset crown seam, narrow visor and diagonal overlapping closed jaw; computer inside the thicker rear temple. | Two broad diagonal breast leaves, staggered abdominal tabs and diagonal back overlap; oblique forearm shells and short outer thigh shields. |
| 18 / Laminate | Both | Overlapping front brow cap and rear crown shell, straight visor and one-piece jaw; recessed nape service strip. | Four broad transverse torso/back lames with staggered side ends; horizontal thigh overlaps, divided forearm guards and isolated knee/shin caps. |
| 19 / Splitline | Cutline | Left/right crown shells meet along a recessed seam; squared visor with paired cheek returns; shallow paired temple housings. | Two long breast halves with a covered central lap, independent scapular halves and paired abdominal plates; longitudinal outer limb panels over textile. |
| 20 / Mantle | Both | Shallow brow hood, recessed panoramic visor and separate closed jaw cradle; integrated rear horseshoe service seam. | Short pectoral yoke over independently suspended rib shields and a belly plate; upper back yoke with two lumbar leaves, short segmented hip/thigh guards. |
| 21 / Keel | Cutline | Compact angular dome, trapezoid visor and short central jaw wedge; computer recessed behind one cheek return. | Narrow sternum insert between two swept rib plates, converging abdominal segments; paired back planes around a tapered center, tapered limb shells. |
| 22 / Course | Both | One-piece faceted cap with a visibly separate visor/mask cassette; small rectangular occipital access hatch. | Two broad offset courses of torso plates, staggered flank joints and a two-plus-one lumbar arrangement; offset thigh tiles above separate knee/shin guards. |
| 23 / Offset | Overlap | Continuous brow, lateral shell closure and horizontal chin seam; one flush temple access slab. | Broad wraparound breast shell with lateral overlap, three offset belly leaves and a side-closing back shell; compact unequal shoulder articulation and short hip leaves. |
| 24 / Facet | Both | Three-plane opaque visor, quadrilateral crown panels and a shallow three-facet mask; inset rear service panel. | Four low-relief kite panels across the torso, flexible flank wedges and four broad rear triangles; diamond-cut limb guards with blunt edges and open flex zones. |
| 25 / Chevron | Overlap | Low central crown cap overlapped by side shells, shallow chevron brow and closed horizontal jaw; recessed twin rear service seams. | Three broad nested blunt chevrons through chest/abdomen and matching articulated back; sliding flank ends, paired oblique thigh shields and separated knee/shin pieces. |

## Sheet and rendering handoff

For each ID: one landscape sheet with a dominant full-body front three-quarter,
smaller matching full-body rear, enlarged closed helmet detail and a compact
subjective HUD study. Keep both full-body heads and soles inside generous margins.
Neutral warm-gray background; controlled material painting. Use `MERIDIAN / 2043`,
the stable ID/name, and `HUD STUDY / PROPOSAL`. The HUD inset has no human face:
only sparse peripheral marks around an unobstructed forward view.

Controller renders ten independent images using `common_prompt` plus the matching
variant `prompt`, with both original PNGs passed as explicit local references on
every call. Controller preserves exact submitted prompts, source paths and image
bytes, then creates the gallery and immutable manifest. Keep Concept01 unchanged.
Artist delivery ends with validated prompts and source hashes; image delivery,
packaging and profile restoration belong to the controller. No art ranking or
visual acceptance is asserted here.
