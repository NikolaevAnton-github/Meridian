# MSQ-54: Datum16ShoulderManual01 owner handoff

Prepared 2026-09-17 following the owner's request to participate directly in
Tripo generation. This closes the bounded input-preparation work, not MSQ-54's
original body/rig prototype. The next external step is the owner's first Tripo
generation and returned FBX. No controller upload, Tripo generation, API call,
credit charge, new 3D model or DCC edit was performed.

Package: `Assets/Source/PlayerCharacter01/AI3D/Tripo/Datum16ShoulderManual01/`.
Open [the gallery](../Assets/Source/PlayerCharacter01/AI3D/Tripo/Datum16ShoulderManual01/index.html)
and [manual instructions](../Assets/Source/PlayerCharacter01/AI3D/Tripo/Datum16ShoulderManual01/README.md).

## Delivered input and limits

The wearer's right shoulder cap is derived from the owner-selected
`Assets/Concepts/PlayerCharacter01/Concept02/16.png`. The T-pose art was inspected
as placement context; its changed surface pattern and projections did not become
new design authority. Original art and all prior candidates remain untouched.

One canonical upload image, `Inputs/01-StartHere-Outer45.png`, shows the isolated
complete armor shell against white. An initial excessively deep return wall was
corrected before derivative views; the original attempt is preserved under
`Attempts/StartHere01.png`. The isolated construction is an interpretation of
the selected art, not dimensionally approved production geometry.

Four additional PNGs are stored in `ReferenceOnly/`. They are **not a validated
Multi-view upload set**: the nominal Front/profile views remain partly oblique,
some edge and fastener landmarks vary, and Back adds inferred interior hardware.
Keep them for construction discussion. Do not combine them in the first Tripo job.
No calibrated 3D consistency, final dimensions, hidden attachments or body fit is
claimed. This classification is controller authoring/technical QA; the owner
alone evaluates the art. No independent concept reviewer was dispatched.

## Owner's next action

Generate once from StartHere in Tripo Studio Smart Mesh / P2.0 - Preview with
Quad target 3000 and Private visibility. Keep the geometry untextured and unrigged.
The current inspected Smart Mesh panel places Quad and Polycount under Topology;
it has no separate Texture switch. Do not run the later Texture/Retopo/Segment/
Fill Parts/Animate operations for this first return.

Export the untouched result as FBX, preserving quads if offered, into the package's
`OwnerExports/` directory. Preserve any sidecars/archive and record the task
URL/ID, actual settings, output count and credit use when available. The supplied
JSON is an optional notes template, not evidence of a performed generation.

After return, inspect the actual mesh and establish the common proportional
body/undersuit fit before component assembly and shoulder/aim/reload tests using
`MSQ52-RigContract01`. A fitted master has not been created by this preparation.

## Execution and evidence

The existing Multica Concept Art agent authored the five prompts and its bounded
handoff under MSQ-54, using task-local Astra/high/standard. The controller used
built-in imagegen for six renders (one preserved correction attempt plus five
delivered views), retained exact returned PNG bytes and the exact render requests,
and prepared the gallery, settings and export destination. The task-local agent
profile/native arguments are restored after the run.

Technical evidence and native run output:
`Saved/PlayerCharacter01/Datum16ShoulderManual01/Controller/`.
The package manifest and asset-registry inventory record exact file identities
and distinguish declared image derivation from unverified production geometry.
Registration is not visual acceptance. Project storage before rendering was
16,868,191,285 bytes, below the 250 GB cap; bounded package growth is recorded.

The controller preserves the pre-existing owner change in Config/DefaultEngine.ini
and locally commits only this preparation package and scoped documentation.
