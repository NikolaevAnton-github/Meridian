# LobbyFunctional-Build01 / WorkerCandidate01

The approved FunctionalRevision02 package is built in neutral 3D and ready for
fresh independent review. The saved candidate is
`/Game/Maps/L_OpeningLobby_FunctionalBuild01`, created from ReworkA01. Unreal 5.8.1
is left on this map with PIE stopped, no dirty packages and temporary capture
and throttle settings restored. Owner acceptance of these 3D bytes remains pending.

The four rooms extend to the outer walls, with transverse entrance service doors,
hall-facing inner doors and stepped roof closure. Four 2.4 x2.4 x18 m columns,
the two 1.5 m checkpoint lanes, and the 3.6 x4.2 m elevator opening/opaque upper
wall follow the approved active dimensions. Remaining ReworkA01 architecture,
neutral materials, lighting, floor strips and hall scale are preserved.

The editable source is
`Assets/Source/OpeningLobby/FunctionalBuild01/LobbyFunctionalBuild01.blend`;
17 modules serve 20 placed assemblies. Source README and
`Scripts/OpeningLobby/functionalbuild01_*.py` document guarded reproduction,
import, actual profile measurements, native captures and real PIE input checks.
The exact identity is `Saved/OpeningLobby/FunctionalBuild01/Worker/manifest.json`
with its `manifest.sha256` sidecar. All paths below are relative to that Worker
directory unless stated otherwise.

| Evidence | Verified result |
| --- | --- |
| `construction.json`, `asset-audit.json` | 201 checks passed after save/reopen; all unchanged baseline actors preserve transforms, meshes, collision, materials and light/exposure properties |
| `scheduled-measurements.json` | 65 schedule measurements passed; primary tolerance 0.05 m, recorded comparisons within 0.0005 m |
| `imported-profile-probes.json` | 66 actual complex traces passed for doors, roof tiers/beam contact, columns, lanes and elevator/opaque field |
| `saved-source-audit.json` | All 17 saved native modules and 17 reimported FBX modules passed transforms, normals, closed topology, bounds, UV and slot checks |
| `runtime-verification.json` | 115 input-driven events, 2,041 samples, 223.22 s; both lanes both ways, remaining aisles through X +/-16.8 bays, four doors, six column passages, all new blocking families, full-hall route, look, possession, grounding, jump and landing |
| `ElevatorRecheck/runtime-verification.json` | 11 events, 226 samples; actual movement/contact passed after the subtle two-leaf meeting-edge refinement |
| `evidence-validation.json` | 13 native 1920 x1080 images with checked poses/HFOV90; protected historical file hashes preserved |
| `capture-settings-restored.json`, `final-state.json` | Original settings restored; candidate loaded clean, PIE stopped, original GameMode retained |

The four matched sheet05 images are `entrance-90.png`, `inner-90.png`,
`context-90.png` and `aisle-90.png`. Additional views cover the negative service
door, both inner door thresholds, elevator detail, checkpoint context, room
junction, ceiling contact and baseline C1/C2 gameplay cameras. Per-image camera
JSON records actual poses, FOV, exposure and final map identity. The measured
section is supplementary technical evidence; it does not replace playable views.

Author visual judgement: room/pier integration, recessed doors, continuous roof
joins, column ceiling contacts and the opaque inner focal field read coherently.
The new shafts substantially narrow both baseline axial views as approved.
The entrance portal remains dominant behind the common checkpoint. All current
images were inspected; detailed findings and diagnostic distinctions are in
`visual-inspection.md`. Independent visual review remains a separate gate.

The initial unified elevator surface was refined into two closed leaf solids
with a 2 mm meeting-edge bevel; its opening envelope and contact plane remain
within schedule. Initial source/leaf/image diagnostics are preserved separately.
No historical assets were overwritten. The saved baseline map still hashes to
`71cfc087c80510313054255d784d1b43c45395d6400c9e0b75e9f64d7be944d0`.
The candidate map hash is
`9990d2ca10a62a32fcb7d7e38fb324e84d6f52e406601b74ce9689c6b6d08894`.

The loaded skill was `.agents/skills/environment-architecture-production/SKILL.md`.
Execution used installed Blender 5.2.1, Unreal 5.8.1 and official Epic MCP with
the existing subscription. Project storage measured about 11.85 GB without
following junctions; growth was about 35 MB, below the 1 GB task target.
No delegation, paid service, installation, registry update, configuration edit,
task administration, commit or push was performed.

No interiors, door/elevator operation, logo, final materials or atmosphere are
included. Ground-level route closure is verified; anti-jump security is not
claimed. This handoff grants neither owner 3D acceptance nor later-stage scope.
