# FunctionalBuild01 neutral source

`LobbyFunctionalBuild01.blend` contains the editable native reusable kit and its
assembled room/column/checkpoint/elevator placement. Seventeen modules serve
twenty instances. Coordinates and UV units are metres; native scales are positive
and applied. `approved-solids.json` is a direct evaluation of the two frozen
FunctionalRevision02 geometry function sources, with historical retained geometry
stubbed out because Unreal reuses the actual ReworkA01 actors.

`Scripts/OpeningLobby/functionalbuild01_data.py` groups approved solids into joined
shells, frames and functional modules. Roof portions already occupied by original
piers are trimmed to eliminate visible coincident faces. The retained 3 cm inner
end band completes the inner shells. The opaque wall keeps the original X30 plane
and opens behind the closed elevator leaves to X30.06. Two 2 mm meeting-edge bevels
make the elevator's two closed leaves readable; their combined opening envelope
is unchanged. Every other new module has exact unbevelled scheduled bounds.

Reproduce with the existing runtime Python and installed Blender 5.2.1:

1. Run `functionalbuild01_preflight.py` and `functionalbuild01_data.py` on a clean
   candidate output directory; neither modifies approved inputs.
2. Run Blender with `--background --factory-startup --disable-autoexec
   --python-exit-code 1 --python Scripts/OpeningLobby/functionalbuild01_kit.py`.
   Existing native source is protected by the build guard. The explicit
   `--refine-elevator` flag requires the archived initial source before overwrite.
3. Register `functionalbuild01_tools` in editor Python, then use official Epic MCP
   `OpeningLobbyFunctionalBuild01Tools.action`: inspect, baseline, create, import,
   assemble, audit. Creation refuses to overwrite an existing map or namespace.
   Existing neutral ReworkA01 materials and context assets are read-only.
4. Run `functionalbuild01_source_audit.py` through Blender for saved native and
   FBX geometry verification; use the task's capture and real-input adapters.

Exports compensate the measured FBX Y reflection on temporary mesh data with
repaired normals. Native source stays in drawing coordinates. The imported
profile probes verify actual service and inner door orientation, not just bounds.
The source kit uses metre tiling UVs and one neutral material slot per module.
No texture bake or Painter work is part of this candidate.

The final identity, native screenshots and test logs are under
`Saved/OpeningLobby/FunctionalBuild01/Worker/manifest.json` and its digest sidecar.
Independent visual review and owner acceptance of these 3D bytes remain pending.
