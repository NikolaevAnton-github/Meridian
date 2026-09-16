# UpperVoid01 / HeightCorrection02 author handoff

**Status: independent recheck handoff with HC-R1 still visually unresolved.**
Two authorized trials are complete. The selected Trial02 reduces the bright upper
pool, but the near-column image still has a compact common terminal silhouette.
The author does **not** claim successful HC-R1 closure or owner-viewing readiness.
Fresh MSQ-32 recheck must judge this residual and the darker central shafts.
No third trial, owner acceptance or glass acceptance is implied.

## Candidate and scope

- Candidate: `LobbyAtmosphere-UpperVoid01/HeightCorrection02`.
- Map: `/Game/Maps/L_OpeningLobby_PainterStone01`.
- Map SHA-256: `d0cfd7c89e0702ce98f04b48f9d2c8f62abce96eb9f3fde25676b5968c7f39ac`.
- [Manifest](../Saved/OpeningLobby/UpperVoid01/HeightCorrection02/Worker/manifest.json)
  and [final receipt](../Saved/OpeningLobby/UpperVoid01/HeightCorrection02/Worker/manifest-receipt.json).
- [Verified predecessor archive](../Saved/OpeningLobby/UpperVoid01/HeightCorrection02/Controller/BeforeCorrection/archive.json)
  contains the exact previous map and two atmosphere assets.
- [Editable source and recipe](../Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection02/recipe.json).

Only the two dedicated atmosphere graphs and six central light components changed.
All twelve side lights, geometry, surface material/source bytes, 107 bindings,
glass/support, collision, gameplay and configurations remain unchanged.
The map started clean on UE 5.8.1; all operations used official Epic MCP, with one
minimal Rider registration for the isolated task toolset. No delegation, task
administration, controller edits, paid APIs, registry writes, commits or push.

## Two purposeful trials

| Setup | Dedicated response | Six central fills | Finding |
| --- | --- | --- | --- |
| Trial01 | World-height 13.7–17.8 m; postprocess `exp(-8*h*h)*(1-h)^2*(1+2*h)`; broader cubic light transmission | Specular scale 0.2 to 0.05; intensity 100000 retained | Exact close pose still reads as a cut top; high diffuse pool remains conspicuous. |
| Trial02, selected | Same graphs and high limits | Intensity 100000 to 20000; Trial01 specular retained | Bright pool substantially reduced; terminal silhouette remains visible and centre is darker. |

Here `h` is clamped world Z normalized between 1370 and 1780 cm. Both curves
equal one below onset and zero above extinction. Node topology, graph placement
after tonemapping, manual exposure bias -5, light positions/radii/indirect scales
and all side-light properties are unchanged. No screen-height, pitch, time or
camera-dependent mask was introduced. No surface gloss parameter changed.

Each trial retains its recipe, actual images and camera records. Trial01 also
retains full compressed scene properties and native graph readback. The same
graph bytes serve Trial02; its final map carries the second trial's light values.
No standalone native Trial01 map copy was made. Exact HeightCorrection01 history
is preserved separately and verified; no old evidence was edited or rebaselined.

## Actual visual evidence and residual

Evidence root: `Saved/OpeningLobby/UpperVoid01/HeightCorrection02/Worker/`.
Inspect **Trial02/close-column-90.png**, **Movement/close_column_up.png** and
**Movement/motion-003 through motion-006.png** before reading author conclusions.
The explicit still uses the failed pose (-1551.150808,230.164361,172.15) cm,
yaw0/pitch74.912516/HFOV90 at native **1920x1082**. The real-input hold has its own
honest actual pose and must not be represented as exactly the same placement.

Fourteen still images retain both trials; eleven selected candidate views span
close/axis/corner/central-up/both-aisle/reflection conditions. Trial02 close,
entrance-axis and west-aisle images are referenced directly; eight other views
were captured after reopening. Secondary native images are **960x540**, compared
by pose with immutable predecessor **1920x1080** references, not pixel-matched
resolution pairs. No screenshot pixels were edited.

Author inspected all stills, all seven motion frames and the native hold capture.
The main roof/contact remains hidden in these views; both aisle ceilings and
finite enclosures remain visible. Floor and stone reflections remain legible,
without an identified bright main-roof reflection. Central shaft shading is
substantially darker, while inherited side pools remain. The exact close view
still gives a narrow apparent terminal edge. This residual remains the principal
visual blocker; the numerical smoothness of the graph does not override it.

The fresh **23.281-second actual-input approach/turn** has **208 continuous
telemetry samples**, seven timestamped 960x540 native frames, and a **6.829-second
sampled upward hold**. Every sample is grounded, possessed and FOV90; movement
and look bindings increment. No teleport was used in the walkthrough. Earlier
full-route gameplay evidence is carried forward because gameplay is unchanged.
Sampling does not exclude every unsampled transient; no continuous-video claim.

## Technical verification

- Full **129 actors / 150 components** comparison: exactly **12 scheduled light
  deltas**, zero unexplained changes. **107 lobby bindings** and the separate
  support component are preserved. Candidate/Reopened/Handoff properties agree.
- Six graph field changes: four thresholds and two custom formulas. Native
  readback matches both editable HLSL files. Reopened graph connections agree
  after normalizing only transient hexadecimal object addresses, preserving
  all object paths/types. Full properties are losslessly gzip-compressed;
  existing immutable schema files are referenced instead of duplicated.
- **4302 protected file entries** checked; only current map/two atmosphere assets
  changed. **3435 entry checks across nine historical manifests** resolve through
  explicit exact archive paths. The interrupted original UpperVoid01 run had no
  manifest; its five archived entries and all original evidence remain verified.
- Capture controls restored; callbacks complete, held inputs released, PIE off,
  no dirty packages. Reflection schemas do not serialize every delegate/event;
  unchanged source/config plus actual traversal provide corroboration.
- One matching stationary floating-PIE sample: 5 s warmup plus 20 s measurement,
  actual 1920x1082. Predecessor **119.900 FPS / 8.34030 ms**; selected candidate
  **119.979 FPS / 8.33482 ms**. Same pose, renderer and recorded CVars. The existing
  near120Hz plateau is unexplained; no GPU-stage, uncapped-headroom, standalone,
  1440p or worst-route claim. Native warnings are summarized in `error-audit.json`.

## Storage and handoff limits

Before report/manifest sealing, measured additional correction data was
**16,887,894 bytes**, exceeding the **15 MB aim** by 1,887,894 bytes. Combined
HeightCorrection01/02 data, including controller/review/source/helpers/reports,
was **99,621,923 bytes**, below **100 MB** with little headroom. Project usage was
**14,246,328,236 bytes**, below the **250 GB hard cap**. Cumulative lobby usage was
**2,478,928,510 bytes**, exceeding the **2.4 GB planning target** by **78,928,510
bytes**. These are explicitly failed planning/aim checks, not a false PASS.
The final receipt records later sealing growth and exact identity; future
controller/review growth must still be counted. No history or user asset deleted.

The two-trial bound is exhausted. Handoff is for fresh independent recheck and
controller disposition of the unresolved visual result and storage variance.
It is not a request to accept HC-R1 on technical evidence. Glass remains
**DEFERRED_BY_OWNER**; no further task is dispatched.
