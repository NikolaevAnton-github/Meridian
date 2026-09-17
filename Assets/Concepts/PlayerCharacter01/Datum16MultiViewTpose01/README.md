# Datum 16: eight T-pose input-art views

Eight separate PNG illustrations of operative 16 / Datum, with pure opaque
white as the background target, prepared for the owner's multi-view input
experiment. Every view targets the same neutral T-pose: upright torso, both
arms extended horizontally sideways at shoulder height, straight elbows,
relaxed open hands, straight legs, and forward-facing feet. Only the camera
changes between views; foreshortening can hide or overlap limbs in profile,
overhead, and underfoot projections. This is input-art
preparation only. Final owner selection and modeling approval remain pending.

[Open the gallery](index.html). [Exact image manifest](manifest.json).
[Multica prompts](prompts.json). [Exact imagegen requests](render-requests.json).

## Upload mapping

Upload each linked PNG into the correspondingly named view slot.
The gallery itself is not an input image.

| View slot | Original PNG | Camera convention |
| --- | --- | --- |
| Front | [16-Datum-Front.png](16-Datum-Front.png) | Front camera; the wearer faces the viewer. |
| Left 45 degrees | [16-Datum-Left45.png](16-Datum-Left45.png) | Three-quarter front view with the nose turned toward screen-left. |
| Right 45 degrees | [16-Datum-Right45.png](16-Datum-Right45.png) | Three-quarter front view with the nose turned toward screen-right. |
| Left profile | [16-Datum-Left.png](16-Datum-Left.png) | Profile camera; the nose points screen-left. |
| Right profile | [16-Datum-Right.png](16-Datum-Right.png) | Profile camera; the nose points screen-right. |
| Back | [16-Datum-Back.png](16-Datum-Back.png) | Rear camera; the wearer faces away from the viewer. |
| Top | [16-Datum-Top.png](16-Datum-Top.png) | Overhead projection looking down from above the head; strong foreshortening is expected. |
| Bottom | [16-Datum-Bottom.png](16-Datum-Bottom.png) | Underfoot projection looking up from beneath the feet; strong foreshortening is expected. |

Left and Right describe the direction of the nose on the screen, not anatomical
sides. In the Left profile, the nose points screen-left. In the Right profile,
the nose points screen-right. The same facing-direction convention applies to
the two 45-degree views.

Top and Bottom specify overhead and underfoot projections, respectively,
with the camera looking down from above the head or up from beneath the feet.
Strong foreshortening is expected in these projections.

## Scope and provenance

All eight PNGs are 1254 x 1254 RGB, saved as returned by built-in imagegen.
Multica Concept Art prepared prompts at Astra/max/standard. The controller
established new Front/Back T-pose anchors, then used those for the remaining
six views with additional profile/axial camera constraints. Actual requests
are preserved in render-requests.json; no pixel resizing or editing followed.

The original Concept02/16.png, prior Datum16TrellisInput01 artwork, and
Datum16MultiView01 views are preserved identity references. Prior protected
package files passed SHA-256 comparison
against the controller's pre-task snapshot. This packaging script reads the
delivered PNGs without editing or resaving their pixels. The manifest records
their exact bytes, dimensions, modes and outer-border white statistics.

The images are independently generated illustrations and may have small detail
and projection variations between views. Hidden surfaces are inferred, and
exact three-dimensional consistency has not been verified. They are not a validated
production turnaround, mesh, topology, rig or deformation design. Border
statistics are technical observations, not independent art review or owner
acceptance. No independent art review or external 3D generation was performed
as part of this package.
