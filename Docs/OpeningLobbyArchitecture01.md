# Opening lobby Architecture01 - GlassReview01 handoff

MSQ-6, 2026-09-14. **GlassReview01 variant B is saved for independent review.
Pane/leaf separation improved; believable light-diffusing glazing and B3 closure
remain unconfirmed.** Owner detail acceptance is pending; MSQ-7 is not authorized.
The diffusion interpretation is the controller's working assumption, not an
owner-approved optical specification.

Current clean editor map:
`/Game/Maps/L_OpeningLobby_Architecture01_GlassReview01`.
It is a template copy of saved LightStudy01 setup B. The original Architecture01
and LightStudy01 maps, assets and images remain unchanged. The archived
LightStudy01 handoff below describes the earlier result, not the current map.

Evidence root (GR): `Saved/OpeningLobby/Stage2/Architecture01/GlassReview01/`.
The complete prior document is also retained in `GR/Before/OpeningLobbyArchitecture01.md`.

## Optical result and limits

Inspected both actual owner reference images and Review02/03-SecurityOblique,
the prior LightStudy01 MetalGlass view, both variants' original MetalGlass-90,
C3-90 and C2-75 tests, and all ten reopened Final native images. Variant A gave
the fixed glass a muted mauve cast. B uses neutral fixed transmission and
stronger leaf absorption while retaining the same lighting. Only two optical
variants were rendered. B's initial proposed values in preflight.json were
adapted after inspecting A and before B's first execution; variant-B.json and
the native graph are the actual B recipe.

In Final/MetalGlass-90, the leaf interiors now carry a darker green-grey body
with a distinct gradient against the softer fixed field. At C3-90 and
Checkpoint-90 the leaf rectangle remains separable behind the station and
detector. C2-75 retains that hierarchy at a small projected size. Fixed-glass
point-light reflections are spread into broad highlights instead of the earlier
disks. B removes most of A's mauve cast. These are useful material-role changes,
but the broad fixed fields still look uniform and somewhat panel-like compared
with the approved reference's luminous glazing. This handoff does not call that
remaining visual ambiguity resolved, nor treat increased brightness as success.

The implementation is Simple Volume scattering/absorption with a rougher
reflective surface. `Transmission/GlassTransmission-90.png` shows the hall,
piers, strips and checkpoint through the lower fixed fields and leaves from the
reverse side. It supports transmission, **not strong frosted image blur**:
architectural edges remain recognizable. No measured optical haze value or
physically calibrated angular diffusion is claimed. The fixed neutral far
field is inherited from LightStudy01; no exterior imagery, backing, light,
probe, emissive mask, random pane color or geometry was added.

Stone grain, floor veins and polished response retain their prior reviewed
scope. Scale and the station/detector/pier relationships are preserved. Thin
edge temporal behavior, performance and final atmosphere remain unassessed.

## Native sources and exact mapping

Four editable parameterized native material graphs are retained under
`/Game/OpeningLobby/Architecture01/GlassReview01/`: `M_GR01_A_Fixed`,
`M_GR01_A_Leaf`, `M_GR01_B_Fixed`, `M_GR01_B_Leaf`. A is preserved as a rejected
optical test; the saved map uses B only. There are no new textures or DCC assets.
Both B graphs feed a Substrate Slab with MSS_SIMPLE_VOLUME from native
TransmittanceToMFP. Colored-transmittance blending, thin-surface mode, backface
culling and per-pixel surface lighting follow the original working glass.
Emissive, opacity, normal, refraction and displacement inputs remain unwired;
there is no opaque pane substitute. Thickness inputs retain source defaults.

| B role | Actors, all material slot 0 | Scattering albedo RGB | Transmittance RGB | Roughness |
| --- | --- | --- | --- | --- |
| Fixed | A01_EntranceUpperGlazing; A01_InnerHighWindow; A01_EntranceSidelight_-1; A01_EntranceSidelight_1; A01_EntranceOverlight | 0.55, 0.55, 0.55 | 0.90, 0.90, 0.90 | 0.32 |
| Leaf | A01_EntranceLeaf_-1; A01_EntranceLeaf_1 | 0.06, 0.06, 0.06 | 0.68, 0.74, 0.71 | 0.09 |

F0 is (0.04,0.04,0.04) for both roles. Values are linear inputs, not measured
total transmission of the assembled panes. `variant-B.json` records exact
actor/component/mesh paths and original/new material bindings.
`native-shader-audit.json` verifies reopened wiring, values, Simple Volume
type, compiled instruction statistics and all seven assignments.

Reproducible guarded source: `Scripts/OpeningLobby/architecture01_glassreview.py`.
The existing Epic task action dispatches `operation=glassreview01`; no new bridge
was installed. Existing map/package/variant identities are refused on creation.
Native materials retain editable named parameters for subsequent authorized work.

## Verification and handoff state

The reused construction audit passes with 2,045 visual actors and 33 structural
blocking shells. Source, template, reopened and final complete reflected
actor/component/world snapshots are retained. `property-preservation.json`
checks all 2,101 actors, including the three inherited inspection actors, and
all their components. The only allowed differences are the seven explicit
material overrides; all geometry, bounds, collision, gameplay, lights,
postprocess, visibility and renderer values match LightStudy01.

The prior 185 schedule checks, 63 envelope checks and 112.297 s real-input route
are carried with their original scope; they were not repeated for material-only
changes. The prior six noncolliding station fascia panels still postdate that
route. Fresh `standing-spawn.json` verifies real possession in the reopened
GlassReview01 map, OpeningLobbyGameMode, grounded MOVE_WALKING, speed 360 cm/s,
capsule 34/88 cm and gameplay FOV 90. Controls remain WASD, mouse, Space and Escape.

All ten Final views are native 1920 x 1080: C1/C2 at 75 and 90, C3/C3-context
at 90, Stone, Floor, MetalGlass and Checkpoint. The existing capture validator
checks their poses/FOV/resolution, with `Final/capture-inventory.json` recording
hashes. All 16 original-angle A/B/Final cameras exactly match LightStudy01's
corresponding actual poses and renderer settings. Eye Z remains 172.15 cm.
`camera-renderer-preservation.json` records those comparisons.

The seventeenth image is separately labeled diagnostic: reverse-side camera
(-3300,0,172.15) cm, yaw 0, HFOV 90. Its flying/collision-disabled overrides
were restored to collision enabled and MOVE_WALKING at the original spawn
before normal captures. It is not route evidence or an approved exterior view.
PIE is stopped, FOV returned to 90, and the saved candidate is clean.
Numeric play-window settings and throttle before/after readbacks agree in each
capture folder; restoration did not save project or user configuration.

`protected-inputs.json`, `preservation.json`, the standard project-path-to-
SHA256/byte `inventory.json`, and `inventory-validation.json` record integrity.
The disk preflight followed the permitted four-line dispatch-hook addition;
this boundary is explicitly recorded. The remaining original bytes are protected.
`storage-after.json` contains no-junction project accounting and both study and
Stage 2 growth against the 250 GB/2 GB limits. No user assets were deleted.

Controller handoff: assess the actual neutral scattering/absorption treatment
and its remaining uniform-field/blur limitation independently. No B3 pass or
owner-ready detail claim is made. No delegation, installs, paid services,
commits, pushes, registry writes, task comments/status/assignment changes or
later-stage dispatch occurred.

## Archived LightStudy01 handoff

MSQ-6, 2026-09-14. **Neutral light study complete; B3 closure NOT demonstrated.**
A saved separate inspection map and matched evidence are ready for independent
assessment of the partial result. This is not an owner-ready detail submission.
Review02's B1 stone and B2 floor passes remain prior independent findings.
Owner detail acceptance is pending; MSQ-7 remains outside this handoff.

## Maps and controls

| Map | Purpose and state |
| --- | --- |
| `/Game/Maps/L_OpeningLobby_Architecture01` | Unchanged Correction01 baseline, with its original neutral lights, exposure and ten comparison/detail images. |
| `/Game/Maps/L_OpeningLobby_Architecture01_LightStudy01` | Separate saved/reopened study, setup B. Adds three labeled neutral inspection actors; reuses all baseline assets. Current clean editor review map. |

Open either map explicitly. Press Play at Default Player Start. WASD walks,
mouse looks, Space jumps, Escape ends PIE; Shift+F1 releases the cursor.
GameMode remains `/Script/MeridianSquad.OpeningLobbyGameMode`, speed 360 cm/s,
capsule radius/half-height 34/88 cm, standing eye Z 1.7215 m and gameplay HFOV 90.
The study's actual possessed character spawned at (-2850,-105,90.15) cm, standing
on the floor, with zero velocity and the original grounded walking behavior.
Doors remain noninteractive boundaries; the study adds no route or destination.

Baseline map SHA-256:
`1d6ba401f1551f3b4189dbb4d275a9c740eda7d7a76163be55566e85b584b51e`.
Study map SHA-256:
`fd7f4f110a77eb450497c10d712c1b07525dcf27c0824579aac15cde3fca4f74`.

## Study outcome and exact differences

`LS` below means `Saved/OpeningLobby/Stage2/Architecture01/LightStudy01`.
`OUT` means its parent, `Saved/OpeningLobby/Stage2/Architecture01`.
The unchanged baseline images remain directly under `OUT`; the ten study images
are under `LS/Final`. Do not substitute them into the baseline inventory or claim
identical lighting. The approved owner entrance reference and Review02 oblique
supplement were inspected directly, alongside Review02 and Correction02/03.

Tested only two neutral setups at MetalGlass-90, C3-90 and C2-75. A used linear
RGB (12,12,12) at both horizon and zenith. It made frames/handles easier to see,
but produced a very uniform pale transmitted field. B uses horizon (1.5,1.5,1.5)
and zenith (6,6,6), with horizon falloff 3. Its quieter grey gradient retains
better near-view edge contrast and was saved as useful material inspection
support. No third setup, material/coating/probe experiment or exterior was made.

The final MetalGlass view shows distinct dark stiles, centre member, handles and
some edge layering. C3 shows a more legible leaf rectangle behind the checkpoint.
However, the pane interiors still largely merge with their surrounding glazing;
C2-75 remains weak at distance. The existing circular light reflections remain
prominent. A physically transmitting shader and brighter silhouette alone do
not establish convincing clear-pane depth. **The author leaves B3 unresolved.**
This result does not establish that any particular untested remedy is necessary.

The separate study has exactly these added actors, all under
`LightStudy01/NeutralInspectionOnly`, with actor collision disabled and every
primitive component set to NoCollision:

| Actor | Saved configuration |
| --- | --- |
| `LS01_NeutralFarField_InspectionOnly` | Stock `/Engine/EngineSky/BP_Sky_Sphere`, reusing `SM_SkySphere` and `M_Sky_Panning_Clouds2` through its native dynamic material. Origin (0,0,0) cm, bounding radius 100000 cm. B horizon/zenith above; overall color (1,1,1). Sun-driven colors disabled, no directional light, sun brightness/cloud opacity/cloud speed/star brightness all 0. Cloud color (12,12,12) has zero opacity. Cast shadows disabled. |
| `LS01_NeutralSkyLight_InspectionOnly` | SkyLight at (0,0,900) cm, Movable, captured-scene source, intensity 1, white color, sky-distance threshold 50000 cm, cubemap resolution 128, real-time capture false, lower-hemisphere black false. Recaptured after setup changes. |
| `LS01_FrontLayerReflections_InspectionOnly` | Unbound PostProcessVolume at origin, priority 10, blend weight 1. Only enabled override is `bOverride_LumenFrontLayerTranslucencyReflections`; its value `LumenFrontLayerTranslucencyReflections=True`. |

This is a neutral far field, not authored exterior scenery or an opaque panel at
the glass. No ground, street, landscape, buildings, signs, sun/cloud/star imagery,
time-of-day assertion, fog or new DCC asset is present. Native engine BP instance
parameters rebuild its dynamic sky material after reopening; no material package
or texture bytes were changed. Full added properties are in `LS/support-live.json`
and `LS/Reopened/all-properties.json`; A/B settings are independently recorded.

Original interior lights and the entire original postprocess/exposure struct are
identical. Manual exposure retains bias -5, physical-camera exposure false,
bloom 0 and motion blur 0. Live UE 5.8.1 uses deferred Substrate, Lumen GI and
reflections, hardware ray tracing, GI/reflection quality 3. FrontLayer Allow=1,
Enable=0, EnableForProject=0 throughout. The study enables only the allowed
per-view field. All 15 recorded renderer variables match source, per-image and
final state. No global console, scalability, project or user configuration
change was persisted; no global console override was needed.

## Retained architecture, native kit and material sources

Accepted Layout03 scale remains 60 x 24 x 18 m, six 2.4 m square pier pairs,
8.4 m shaft height/pitch, 6 m bay gaps, 11.2 m central clearance and 4 m aisles.
The approved human-size door/checkpoint exceptions and layer separation remain.
The 18-mesh kit, 2,045 visual actors, seven glass layers, equipment and 33 invisible
structural blocking shells are unchanged. Assets stay under
`/Game/OpeningLobby/Architecture01/{Meshes,Materials,Textures}`.

Editable sources remain in `Assets/Source/OpeningLobby/Architecture01`, including
`LobbyArchitecture01.blend`, the Painter project and canonical textures.
Generated FBX/Painter exports stay under `OUT`. All nine materials retain their
Correction01 bytes. No Blender/Painter bridge or authoring session was needed.

Stone/Wall and Floor/Strip reuse the corrected 2048 x 2048 map families at 4 m
world projection (512 source pixels/m), flat polished normals and open branching
mineral/vein structure. Stone roughness is 0.30; Floor 0.155. BaseColor is sRGB;
ORM and DirectX normals are linear, with green flipping off. The unchanged
Painter set has three 1024 maps. Glass remains native Substrate Simple Volume,
colored transmittance (0.90,0.97,0.94), F0 0.04, roughness 0.045, zero diffuse and
emissive, thin surface and backface culling. The prior reverse-side transmission
proof is preserved; it was not rerun or treated as a replacement front view.

`Final/Stone-90` and `Floor-90` retain readable grain/open veins and calm polished
highlights. Whole views retain the dark green-grey palette, pier rhythm, strips
and checkpoint/aisle relationship. Previous limits remain: sparse repeating
floor motifs, uniform stone groundmass, thin-edge temporal behavior unverified,
and performance unprofiled. Still images cannot establish temporal stability.

## Verification and preservation

The study was created from the clean saved baseline using the proven
`LevelEditorSubsystem.new_level_from_template`; existing studies are refused.
No World duplicate_asset operation or duplicated asset kit was used.
`LS/property-preservation.json` compares every reflected property exposed by the
installed Epic ToolsetLibrary for 2,098 original actors and 2,119 components,
plus complete world settings. Only the copied map name is normalized in object
references; property values, component names and GUIDs are retained. Source,
initial template, reopened candidate and final snapshots are saved separately.
No original actor/component differences were found. The existing construction
audit also passes with identical original bounds, materials and collision.

Those positive preservation results and asset/config/source hashes support
carrying the prior **185 schedule checks**, **63 envelope checks** and
**112.297 s real-input route**, with their original limits. They were not rerun
for noncolliding light support. The previously recorded station fascia panels
postdate the original movement run; that scope caveat is retained.
`LS/standing-spawn.json` is fresh PIE possession/standing-spawn verification.

All 18 images are native 1920 x 1080 with exact baseline poses, actual eye height
and FOV: two unchanged-map LiveBefore controls, three A, three B, and ten Final.
The Final set is C1/C2 at 75 and 90, C3/C3-context at 90, Stone, Floor, MetalGlass
and Checkpoint. All actual images were visually inspected. The existing
`check_architecture01_evidence.captures()` validated all ten Final views using
only an in-memory output-directory configuration. `LS/Final/capture-inventory.json`
and `LS/image-inventory.json` record hashes and actual cameras/renderer settings.
The original ten baseline captures and their inventory remain byte-identical.

PIE is stopped, gameplay FOV was returned to 90, temporary 1920 x 1080 capture and
foreground-throttle settings were restored, and the editor is clean on the
identified study map. `LS/final-state.json` records this handoff state.

The initial preservation manifest covers 919 project/evidence files. Only this
handoff and the bounded branch in `Scripts/OpeningLobby/architecture01_unreal.py`
are authorized changes to that set. The new guarded recipe is
`Scripts/OpeningLobby/architecture01_lightstudy.py`, dispatched through the
existing official Epic action with `operation=lightstudy01`. Historical defaults
and identity guards are restored after each temporary validator/capture context.
`LS/Before` preserves the pre-edit handoff and dispatch source.

`LS/preservation.json` and the standard path-to-SHA256/bytes `LS/inventory.json`
record final integrity. Existing no-junction accounting measured approximately
11.14 GB for the complete project, 0.78 GB of Stage 2 growth and 0.15 GB of study
growth. Exact figures are in `LS/storage-after.json`; the 250 GB project and
2 GB lobby growth limits pass. No user asset was deleted.

The first setup report referenced a stale BP component after reconstruction;
the component was reacquired and the stock child scale included before any A
capture. A subsequent missing accessor was replaced with the live editor
property. These were setup/report corrections, not additional lighting variants.
Prior corrections/reviews and all approved/historical sources are unchanged.

`LS/final-assessment.md` separates useful diagnostic visibility from unresolved
visual acceptance. Independent B3 assessment and any next scope decision belong
to the controller. No owner acceptance, task administration/comments, delegation,
installs, paid services, registry writes, commits, pushes or later dispatch occurred.
