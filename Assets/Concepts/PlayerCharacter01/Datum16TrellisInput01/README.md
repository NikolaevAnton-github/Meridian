# Datum 16: TRELLIS.2 test input

Prepared from the original Concept02/16.png. Use the single-figure
`16-Datum-TrellisInput01.png`, not the four-panel concept sheet. The new image
is an experimental input illustration, not an approved production turnaround.
Original 16 remains unchanged. Image authoring uses built-in imagegen with
Multica Concept Art Astra/max/standard preparation. Exact prompt and input
reference are preserved in generation-request.json.

The final image has a clean opaque white background; the Space removes it on
upload. An initial transparency request produced an RGB image with a drawn
checkerboard. That attempt is retained under Saved; built-in imagegen corrected
the background using background-correction-request.json. The final image is
not claimed to contain an alpha mask. Both exact prompts are preserved.

[Initial imagegen request](generation-request.json) and
[final background correction request](background-correction-request.json).

## Browser test

1. Open https://huggingface.co/spaces/microsoft/TRELLIS.2.
2. Upload `16-Datum-TrellisInput01.png` to Image Prompt. Check that preprocessing
   retains the helmet, hands, feet and gaps around the limbs.
3. Use Resolution 1024 for the first trial; leave Advanced Settings at defaults.
   Keep the displayed seed if the result needs to be reproduced.
4. Click Generate. Inspect several angles, especially hands, underarms, leg
   separation and the inferred back. These details are not guaranteed by one view.
5. Start with Decimation Target 300000 and Texture Size 2048, then Extract GLB
   and Download GLB. These are source mesh inspection settings, not the final
   game-character polygon budget. Resolution controls 3D generation, while
   Texture Size controls exported texture resolution.

The current Space accepts an alpha-masked image and exports a textured GLB.
Its public ZeroGPU runtime has free access with account-dependent quotas and
queues. No paid credits, account actions or 3D generation were used to prepare
this package.

## Production implications

The output is a candidate 3D starting point. Inspect its unseen surfaces and
separate armor construction, then decide whether to repair or retopologize it.
Animation-ready topology, a skeleton, skin weights, deformation checks and
first-person arm quality are separate work. A successful image-to-3D trial
does not constitute final owner selection or production acceptance.

Local hardware was queried on 2026-09-16: NVIDIA RTX 5090, 32607 MiB VRAM.
TRELLIS.2 documents a 24 GB minimum and Linux testing. Memory capacity fits,
but the local CUDA/Blackwell/software combination has not been validated.
No installation or model downloads were performed.

## Official sources checked on 2026-09-16

- [TRELLIS.2](https://github.com/microsoft/TRELLIS.2): image-to-3D with PBR and GLB; local requirements.
- [Space source](https://huggingface.co/spaces/microsoft/TRELLIS.2/blob/main/app.py): input processing, controls and export.
- [ZeroGPU](https://huggingface.co/docs/hub/spaces-zerogpu): free usage, queues and quotas.
- [TripoSG](https://github.com/VAST-AI-Research/TripoSG): an alternative geometry generator; CUDA GPU, approximately 8 GB minimum. Review preprocessing dependencies before production use.
- [TripoSR](https://github.com/VAST-AI-Research/TripoSR): a lighter older alternative, approximately 6 GB VRAM under default settings.
