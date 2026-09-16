# LobbyMaterials-Complete01: finish every existing lobby surface

On 2026-09-15 the owner explicitly accepted the current materials and requested
all remaining materials together, expecting the lobby fully covered with materials.
See `../Approvals/LobbyPainterMetal01-Acceptance01.json`. This supersedes the
earlier one-family-at-a-time gates and deferrals of broad stone, entrance metal,
ceiling/soffit and glazing material completion. Do not pause for separate family
approvals. Deliver one complete batch, then fresh independent review and required
bounded correction/recheck. Candidate `LobbyMaterials-Complete01/WorkerCandidate01`.

Execute through Multica Environment Artist, Astra/high/standard, existing
subscription/project, concurrency one. The direct controller remains active
through completion. All internal content is English.

## Current authority and preservation

Read AGENTS.md, Docs/Design/GameBrief.md, Docs/PainterWorkflow.md and the accepted
Stone01, Floor01 and Metal01 records. Inspect both actual OwnerReferences01 PNGs.
The current map is `/Game/Maps/L_OpeningLobby_PainterStone01`. Edit in place after
an exact bounded rollback snapshot outside Content. No additional lobby map.
Accepted Metal01 manifest SHA-256:
`d056461ecf7bdaed92cb8ee463d6514c5b76218ef91fee3bdbf50c2c54b36035`.
Current saved map SHA-256 at acceptance:
`abc72118717b8333a109fdeeaf1583485a3e7b35badced84204e9fcc130ebc92`.
Preserve immutable old manifests and all source/assets/evidence. Resolve old map
entries against exact archives, never rebaseline history.

Recheck actual project/map/PIE/dirty state and bytes before editing phases.
Preserve subsequent owner work; never discard dirty state or load old snapshots
over the current map. One writer owns the entire Unreal/Painter operation.
Painter currently has accepted Metal.spp open: inspect unsaved state and preserve
that source before changing projects. No writes to accepted source/material bytes.

Preserve all 17 accepted component bindings (4 stone, 3 floor/strips, 10 metal).
Preserve every nonmaterial actor/component/world property: geometry, mesh
defaults, transforms, dimensions, owner checkpoint X -2090 cm, collision,
lighting/exposure, renderer, gameplay, routes and opaque blank future logo field.
Material overrides on remaining visible components are authorized, including
glazing. Logo field stays opaque and blank, with a coherent surface finish.
No new geometry, panels, decals, props, text, exterior scenery or final atmosphere.

## Complete batch coverage

Rebuild a live explicit actor/component/slot census before authoring. The latest
`PainterMetal01/Worker/RestoredFinal/inventory.json` records 107 visible one-slot
mesh components: 17 accepted and 90 remaining old proxy bindings: Stone 24,
Wall 16, Ceiling 9, Metal 35, Glazing 6. Confirm identities and classify each
by actual architectural role; an old material name alone does not decide finish.
Invisible collision/support objects remain exact and are listed separately.
Any live count differences require investigation and a recorded explanation.
Read-only audit found no invisible mesh exclusions in that inventory. Expected
final distribution is 44 stone, 3 floor/strips, 45 metal, 9 ceiling and 6 glass.
All 35 remaining metal slots are entrance collar/mullions/transoms/meeting stile.
The 16 Wall slots should share accepted stone with the 24 Stone slots; in
particular RA01_Shoulder_-1 must match its accepted +1 counterpart. A separate
wall texture family is unnecessary unless actual inspection establishes a need.
The six panes are RA01_UpperGlazing, RA01_LowerSidelight_-1/+1,
RA01_DoorLeaf_-1/+1 and RA01_LowerOverlight. Their current material is an opaque
emissive proxy, so inherited settings do not establish valid glazing optics.

- Extend accepted Painter stone to columns, piers, beam/portal architecture,
  wall/room cladding and returns according to the references. Existing accepted
  pixels and native sources are the approved palette, reusable read-only. New
  graph/instance variants for physical projection scale or quieter wall response
  may reference them, under the new task namespace only. Keep mineral scale
  credible, continuity coherent and repeated broad fields free of conspicuous
  identical motifs. Do not alter the four accepted samples or their bindings.
- Extend accepted charcoal Painter metal to remaining entrance frames, mullions,
  door hardware/recess frames and other actual metal details. Reclassify proxy
  recess walls or the blank logo field thoughtfully; do not blindly metal-coat
  architecture solely because a proxy used M_RA01_Metal.
- Author a new genuine native editable Painter ceiling/soffit finish as needed:
  restrained dark green-grey mineral/plaster surface with fine-scale response,
  calm large fields, distinct from polished floor and architectural stone.
  Apply it to the existing ceilings, room roof undersides and appropriate
  overhead/recess surfaces. Preserve the reference hierarchy and depth.
- Replace all six old glazing proxy bindings with dedicated editable native
  Unreal optical materials, with explicit fixed-pane versus entry-leaf mapping.
  A subtle neutral/cool diffusing fixed-pane and less diffuse entry-leaf hierarchy
  is an authorized working interpretation of the references. Use real
  transmission/reflection with believable roughness and optical parameters.
  Verify the installed UE/Substrate capabilities; reuse technical bridge code,
  not old experimental candidate assets. No opaque/emissive pane substitute,
  fake painted reflections, colored checker patches, hidden backing or lights.
  This task closes material coverage including glass; assess actual pane/leaf
  readability under the existing lighting and report material-level problems.

Every visible surface must end on accepted Painter families or new complete-batch
materials, with zero old RA01/prototype/default/checker/error material bindings.
Audit effective slot values, not only override arrays. Produce the complete 107-row
coverage table with old/new paths, family and preservation/change reason.
Materials alone must carry this pass; retain existing light and geometry.

## Native authorship and technical verification

New source: `Assets/Source/OpeningLobby/MaterialsComplete01/` (.spp and recipes).
New UE assets: `/Game/OpeningLobby/MaterialsComplete01/`.
New helpers only `Scripts/OpeningLobby/materialscomplete01_*.py`.
New evidence: `Saved/OpeningLobby/MaterialsComplete01/Worker/`, canonical exports
in `Worker/Exports/`. Document `Docs/OpeningLobbyMaterialsComplete01.md`.
Reuse guarded property, capture, channel, storage and manifest validators with
new paths; never run old hardcoded mutations or overwrite old evidence.

Advanced native Painter tools and task roots are enabled through temporary
profile arguments. Verify live schemas, resource URLs and parameter metadata;
follow the verified FillLayer route in Docs/PainterWorkflow.md. No external pixel
or noise generation, rejected content, ceremonial .spp, or unchanged stock smart
material. New opaque texture content must come from real native layer/resource
authoring. Reusing accepted Stone/Floor/Metal is explicitly authorized. Do not
duplicate their SPP/texture sets needlessly. Glass graphs are native UE sources;
do not force transparent optics through Painter.

Before mutation save `assembly-contract.md`, exact scene properties, protected
file hashes and an old/new binding plan. After integration and clean reopen,
compare complete properties allowing only explicitly scheduled material overrides.
Verify preserved 17 bindings and all prior sources/assets/config bytes. Save,
close and reopen each new final .spp and reproduce BaseColor, DirectX Normal and
packed ORM exactly; read final native layers/resources/parameters. Verify compiled
saved/reopened UE graphs, channels/import settings, no error material, physical
scale and dependencies (only accepted families, new content and engine math).
Inspect whole-hall and near/oblique material behavior before handoff. At most two
purposeful author QA revisions per new family, with each revision identified.

Use genuine matched before/final 1920x1080 HFOV90 standing-height images: entrance,
inner, side aisle, context across bays, stone/wall oblique, ceiling/soffit upward
view from standing height, entrance frame/glazing, checkpoint and elevator/doors.
Retain camera pose/FOV/tick/exposure metadata; reject queued/origin frames. Inspect
the actual images. Include a bounded actual transmission diagnostic for glazing,
clearly separate from presentation captures; restore any diagnostic state exactly.
One real standing PIE possession and short forward/return movement check; do not
repeat the full route/performance suite unless a regression requires it. Leave
the single clean current map loaded, PIE off, all temporary settings restored.

Deliver `identity.json` and unique nonempty `manifest.json` entries with relative
path/bytes/SHA-256 binding exact map, sources, graphs/textures, complete coverage,
preservation/native evidence, matched captures, scripts and rollback archive.
Separate actual completion from owner acceptance of resulting batch/final look.

Use shared tileable materials. Target <=300 MB new growth, retain correction
headroom at <=400 MB. The prior 2 GB lobby target was a planning estimate for
serial samples and is superseded for this owner-requested complete batch by a
2.4 GB cumulative lobby planning ceiling; the owner's hard 250 GB project cap
remains. Measure no-junction storage; delete no history or user assets.
No installs/downloads/paid service, global/project config or skill changes,
registry writes/rebaseline, delegation, task comments/admin, commits/pushes or
later dispatch. Return concise English handoff with full logs under Saved.

## Fresh independent review

Controller dispatches fresh Multica Visual Reviewer, Astra/high/standard, using
environment-architecture-review within this material completion scope. Write only
`Saved/OpeningLobby/MaterialsComplete01/Review01/`; no DCC calls/candidate edits.
Inspect actual references and complete matched images and record first-look.md
before author conclusions, then audit exact identity and evidence. Judge:

1. Complete live visible coverage: 107 scheduled components, 90 replacements,
   no old proxy/error surfaces, explicit invisible exclusions and every role.
2. Whole-hall reference palette, hierarchy/depth and walking-height coherence.
3. Accepted stone rollout: physical mineral scale, continuity and repetition.
4. Quiet ceiling/wall/soffit response and retained architectural readability.
5. Metal family coherence across all intended hardware and entry surfaces.
6. Real glazing optics, fixed/leaf distinction and entrance readability; explicit
   closure of material-level glazing issues, separate from final atmosphere.
7. Genuine new native Painter authoring, final source regeneration, valid UE
   graphs/channels/dependencies and preserved approved sources.
8. Exact accepted 17 bindings and complete nonmaterial/owner edit preservation.
9. Genuine comparable capture/PIE evidence, clean reopened state and restoration.
10. Exact manifest/history/archive identity, storage and honest complete handoff.

Return separate visual/technical PASS/FAIL/UNVERIFIED, each criterion with image/
data citations, exact candidate/manifest/map/SPP identities, required_corrections,
critical_unverified_requirements and owner_review_ready. Critical missing evidence
blocks readiness. No extra owner gates between material families; controller
executes required bounded corrections and focused fresh recheck. No reviewer
grants owner acceptance or final architectural/atmosphere/performance approval.
