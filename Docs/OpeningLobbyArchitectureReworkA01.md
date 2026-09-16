# LobbyArchitecture-ReworkA01 — worker handoff

The neutral representative Variant A assembly is saved at
`/Game/Maps/L_OpeningLobby_ArchitectureReworkA01`. It contains the complete
entrance, both terminal bays, engaged end piers, first free pair and continuous
upper-wall setback in the accepted Layout03 hall context. Independent visual
review and owner acceptance of 3D quality remain pending.

Authority is the owner-selected A package with manifest
`fb0f306ff60011d01a1008345017d9029964301b2365d81d8ca5d5eba686a4df` and
`Docs/Approvals/LobbyArchitectureRework01-VariantA.json`. All 28 frozen entries
match. The existing freeze verifier reports one historical input change:
`Docs/VisualAcceptance.md` gained the later A authorization. Approved drawing,
design and reference bytes match; the worker did not modify that document.
See `design-provenance.json` and `freeze-verification.txt` in the evidence folder.

Loaded skill: `.agents/skills/environment-architecture-production/SKILL.md`.
Actual native turn metadata confirms `gpt-6-astra`, effort `max`; service is
configured `default`. The runtime config's fallback effort is `ultra`, overridden
by the native turn's `max`. No runtime settings were changed. Actual local tools
were UE 5.8.1 and Blender 5.2.1 LTS, addon protocol 5, telemetry disabled.

The editable kit has 23 reusable closed modules and 65 placed instances. Main
jamb/reveal planes are X -28.4/-29.0, shoulder -29.6, engaged pier -28.8 and panes
-30 m. The terminal gaps are 6.6 m. Upper wall faces are at abs(Y) 6.2, giving the
0.6 m setback and 12.4 m upper central width. The pocket field/perimeter undersides
are Z 9.2/8.4 with 0.35 m edges. The accepted primary hall, six free pairs,
checkpoint, human elements and gameplay class remain preserved.

The jamb pair uses an explicit opposite-hand source assignment to compensate
FBX's Y reflection into Unreal. An initial visual/profile check found and corrected
this before handoff. Actors retain positive unit scales. New masses use exact
closed-mesh static collision; the stepped recess and collar are not filled by
bounding-box collision. The datum keeps its approved thin section and exposed
front side returns; its rear metre meets the reveals. Hidden support, door
operation/hardware and off-camera destinations remain unresolved.

Technical evidence in `Saved/OpeningLobby/ArchitectureReworkA01/Worker/`:

- `construction.json`: 404 passing saved/reopened geometry, import, context and
  gameplay checks. `imported-profile-probes.json`: 26 passing actual section
  traces, including both jamb hands and both closed ceiling pockets.
- `schedule-verification.json`: 170 passing reused Layout03 schedule checks;
  explicit A aliases/exceptions, maximum error 0.035 m on retained historical
  human elements, within the 0.05 m primary tolerance.
- `saved-source-audit.json`: all 23 saved native modules and 23 reimported FBXs
  pass bounds, closed topology, normals, applied scale/rotation, UV and slot checks.
  `asset-audit.json` records actual Interchange source paths, retained imported
  normals/tangents, local materials and collision properties.
- `runtime-summary.json`: full real-key hall route plus focused checks after the
  jamb correction. Actual checkpoint passage both ways, both terminal crossovers
  and adjacent aisles, portal/reveal/pier contacts, possession/look, grounding,
  jump and landing are covered. Speed/capsule/HFOV remain 360 cm/s, 34/88 cm, 90.
  The longitudinal start moved from X -28.5/Y -3 to clear X -27.5/Y -3; expected
  travel is 56 m. Reports preserve the partial focused run's approach-setup
  failure and the successful input-only continuation. No passing full-hall run
  was repeated after the bounded jamb correction.
- `capture-inventory.json`: eight native 1920 x 1080 PNGs with actual poses,
  HFOV, eye height about 1.7215 m, retained exposure, map identity and hashes.
  C1-90 is the unaffected inner-end context view retained before the jamb swap;
  the seven entrance views were recaptured after it.
- `preservation.json`, `storage-after.json`, `runtime-model-audit.json` and
  `capture-settings-restored.json`: preservation, budget, actual model and
  settings evidence. Final editor state is in `final-state.json`.

Actual image assessment: the continuous portal and recessed shoulder now read
as separate solid masses, the terminal beam/soffit joint closes, and the human
checkpoint remains subordinate in the full hall. The exact 106-degree drawing
comparison includes the portal head; the required 90-degree oblique/C3 poses crop
it. Neutral materials preserve depth but do not establish final source-art mood.
See `visual-inspection.md` for the worker's observations and limitations.

Source is `Assets/Source/OpeningLobby/ArchitectureReworkA01/LobbyArchitectureReworkA01.blend`;
exports are `Worker/FBX/`; assets are under
`/Game/OpeningLobby/ArchitectureReworkA01/`. The source contains a reusable-kit
scene and an assembled representative scene. All reproduction helpers are
`Scripts/OpeningLobby/reworka01_*.py`; existing helpers remain unchanged.

For a fresh authorized creation, run `reworka01_kit.build()` in the verified local
Blender bridge, register `reworka01_tools` once in Unreal using the established
bootstrap, then call official Epic MCP
`Game.Scripts.OpeningLobby.reworka01_tools.OpeningLobbyReworkA01Tools.action` with
`create`, `import`, `assemble`. Creation refuses existing source/assets/maps.
For the delivered candidate, `audit` and `save_reopen` inspect saved geometry;
`capture_prepare/camera/shoot/restore` reproduce the named views with official
StartPIE/StopPIE; `verify` takes `full` or `entrance` and requires foreground
collection of `status` through completion. The narrow `entrance_resume` mode
documents this run's unfinished-check continuation. Run `reworka01_check.py`
with the existing UE-bundled Python for the reused schedule/capture checks.

`Worker/manifest.json` and `manifest.sha256` identify all delivered artifacts;
`ReworkA01-WorkerCandidate01.zip` contains the native source, exports, candidate
assets/map, helpers, current views and reports. Historical diagnostic captures
and process logs are retained locally outside that submission. No commits,
pushes, registry updates, default-map changes or later dispatch were performed.
MSQ-6 remains incomplete and MSQ-7 remains backlog.

Preservation verified 283 protected existing files unchanged. Before delivery
packaging the project measured 11.558 GB without traversing junctions, growth
37.17 MB; dedicated source/content/evidence was 43.92 MB. The submission archive
adds a small duplicate delivery copy; all outputs remain well below the 1 GB
task target and the 250 GB project limit. Exact archive bytes and SHA-256 are
recorded in the external `delivery-package.json` sidecar.
