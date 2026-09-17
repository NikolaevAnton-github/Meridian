# MSQ-54: Datum16UndersuitInput01

Owner direction, 2026-09-17: "Хорошо, сгенерируй изображение для tripo"
("Okay, generate an image for Tripo"). This accepts the immediately preceding
proposal to prepare one whole-character image in the original Datum16 coverall
without external armor plates, with proportions retained and face concealed.
Only input art is commissioned here. Owner-operated Tripo generation and later
source repair/fitting remain separate; do not generate a 3D model or use APIs.

Read Docs/ProjectState.md, the Datum16 selection, and the AI3D pipeline.
The primary design reference is Assets/Concepts/PlayerCharacter01/Concept02/16.png.
The latest owner-corrected pose reference is
Assets/Concepts/PlayerCharacter01/Datum16MultiViewTpose01/16-Datum-Front.png.
Preserve those sources and all earlier shoulder/concept/owner-export packages.

## Bounded Multica prompt authorship

Use Concept Art, task-local Astra/high/standard, one author run. Inspect both
actual reference images. Author a concise English prompt for ONE square image:
one complete character, full front near-orthographic T-pose, arms straight and
horizontal at shoulder height, palms down, relaxed separated fingers, feet
forward at hip width. Include entire head, fingertips and soles with white
margins, pure opaque white background, no ground/cast shadow, text or insets.

Retain the lean athletic human proportions and the olive/charcoal utilitarian
cloth identity of Datum16. Show a continuous practical woven coverall, modest
folds and flexible joint regions, soft gloves and tactical boots. Remove chest,
back, shoulder, upper-arm, forearm, elbow, abdominal, thigh, knee and shin armor;
remove external harness, pouches, belt gear, weapon and helmet computer.
For this under-armor foundation, show a close-fitting soft cloth hood/balaclava
covering all skin and eyes, with no openings or rigid helmet shell. This is an
inferred under-helmet layer, not a replacement final helmet design. Do not add
plastic muscle panels, sci-fi tubes, decorative gadgets or rigid kneepads.
The silhouette must show the coverall's own volume, not naked anatomy or rubber.
Hidden garment construction and final dimensions remain working interpretations.

Write only:
- Assets/Source/PlayerCharacter01/AI3D/Tripo/Datum16UndersuitInput01/prompt.json
  with id, filename (Inputs/01-StartHere-FrontTpose.png), prompt, reference roles.
- Saved/PlayerCharacter01/Datum16UndersuitInput01/Artist/handoff.md
  with actual source hashes and concise inferred-construction/pose notes.

No independent concept review, image rendering, DCC/browser/provider calls,
installs, delegation, comments, issue changes, commits or other edits. The
controller renders using built-in imagegen, inspects and preserves exact output
bytes, packages one upload image, records limitations and commits the delivery.
This does not complete MSQ-54's original fitted body/deformation prototype.

## Controller delivery

Delivered one 1254 x 1254 PNG at
Assets/Source/PlayerCharacter01/AI3D/Tripo/Datum16UndersuitInput01/Inputs/01-StartHere-FrontTpose.png.
Built-in imagegen produced the initial image and one targeted framing correction.
Both exact outputs and both requests are preserved; use only the Inputs image.
Controller inspection confirmed complete white margins, front T-pose, cloth
foundation without external armor/gear, and fully concealed face/eyes. Finger
separation in depth and hidden surfaces remain unverified by this front image.
The supplied T-pose is not the rig's A-pose bind. No Tripo submission, model,
body fitting, rigging or owner visual acceptance is claimed. Multica prompt
authorship is complete; task-local settings are restored. MSQ-54 remains incomplete.
