# Kimodo GetUp01: first floor-to-standing experiment

2026-09-20. The owner explicitly requested a get-up animation in the already
running Chrome Kimodo UI at `http://127.0.0.1:7860/`. The controller generated and
saved one candidate through that UI. This is an animation experiment supporting
MSQ-87 planning; gameplay implementation, retargeting and owner acceptance remain
separate. No Unreal session was changed.

## Candidate

External experiment directory: `D:/devgames/Kimodo/outputs/GetUp01/Attempt01/`.

- `motion.npz`: original SOMA motion, 180 frames and 77 joints.
- `GetUp_FromBack_6s.bvh`: skeletal export at 30 FPS, with Standard T-pose enabled
  for the rest skeleton; the motion itself still begins on the floor.
- `meta.json`: exact prompt and generation parameters saved by Kimodo.
- `verification.json`: finite-array and BVH frame-header check.

Model: Kimodo-SOMA-RP-v1.1. Duration: 6 seconds. One sample, seed 42,
100 diffusion steps, classifier-free guidance enabled with text/constraint
weights 2.0/2.0. No pose constraints and no optional SOMA layer were selected.

Prompt:

> A person is lying flat on their back on the floor. They roll onto their side, push up with their hands, come onto one knee, plant both feet, and stand up steadily. They finish standing upright with their arms relaxed at their sides.

## Observed result and limits

Browser preview showed a supine opening pose, kneeling during the rise and upright
standing at the end. Numeric motion arrays are finite; both source and BVH contain
180 frames. The example was saved successfully through Save Example, and BVH
through Save Motion. The browser tab and owner-started server were left available.

This establishes one real UI/text-to-motion run, superseding the earlier
installation-only generation blocker for this session. Server restart/lifecycle
was not retested. This candidate has not been retargeted to Manny, tested with
ragdoll blending, or accepted for production animation quality. Generated files
remain in the external experiment directory; the selected result can enter the
project asset pipeline when the owner chooses it.
