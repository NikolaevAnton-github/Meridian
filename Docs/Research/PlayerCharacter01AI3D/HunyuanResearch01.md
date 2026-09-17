# Hunyuan 3D research for PlayerCharacter01

Research date: 2026-09-17. Scope: public official documentation, the international Studio UI, and Tencent's official research repositories. The controller supplied additional live read-only observations from the existing browser session. No login, upload, model generation, API activation, installation, purchase, or asset changes were performed by this research task. This is a planning input, not character production or visual acceptance.

## Finding and proposed role

Tencent's hosted Studio is a plausible free-quota candidate for a controlled character generation comparison, with especially relevant part splitting, topology, UV, texture, and rigging tools. Treat its output as a starting mesh and an editable source candidate. No Datum generation was executed by this research, and no actual exported topology, textures, skeleton, or deformation has been inspected in this research.

The useful production sequence is a coherent whole-character reference and proportions first, then controlled component separation and repair. Generating every body section independently is not inherently superior: independent generations can disagree about scale, cross-sections, hidden surfaces, attachment points, and armor thickness. This is a project engineering inference, not a vendor guarantee. A single original body/undersuit with separately fitted rigid armor is a stronger working hypothesis than a collection of independently invented anatomical segments.

## Keep four different products separate

| Surface | What was verified | What this does not establish |
| --- | --- | --- |
| [International Studio](https://hy3d.tencent.ai/studio) | Live page loaded in Chrome on the research date. The controller inspected actual role workflow controls as detailed below. | Visible controls are not tested exports or proof of generation quality. |
| [International Tencent Cloud API](https://www.tencentcloud.com/document/product/1284/75531) | The current API catalog lists Pro/Rapid generation, parts, topology, auto-rigging, texture editing, UV, and format conversion. | API account, balance, regions, billing, and terms are separate from the browser Studio. |
| [Mainland Tencent Cloud](https://cloud.tencent.com/document/product/1804/120696) | The product overview documents 3.0/3.1, 8-view 3.1 input, parts, topology, UV, texturing, format conversion, avatar templates, and text-to-motion. | These features and account requirements must not be copied wholesale into international Studio instructions. |
| Official local repositories | Hunyuan3D-2, 2.1, 2mv, and Part code/model releases exist. | They are not downloads of the current hosted 3.1 Studio, and their licenses do not establish hosted-output rights. |

Tencent's November 2025 [global launch announcement](https://www.tencent.com/en-us/articles/2202235.html) confirms text, image, sketch input, up to four input views at launch, triangle/quad topology, and OBJ/GLB output for Blender/Unreal workflows. It is historical evidence, not a current feature ceiling.

## Current capability evidence and limits

| Capability | Evidence | Relevance to our protagonist |
| --- | --- | --- |
| Text-to-3D | Live [role geometry UI](https://hy3d.tencent.ai/studio/creation/role/geo): 3D Generation V3.1 with text and image input; displayed face choices 1.5M, 1M, 500k, 50k. | Useful for rough generic studies; the existing named concept should control final appearance. |
| Image-to-3D / multiview | Live [role geometry UI](https://hy3d.tencent.ai/studio/creation/role/geo): Add Multi-View, minimum 2 and maximum 8; Front required, then Back, Left, Right, Top, Bottom, Left 45 degrees, Right 45 degrees. A single-image A-pose standardization option is visible. | Our eight-view file names structurally fit these slots, but screen-relative versus anatomical side mapping and cross-view consistency require checking. Do not assume that more inconsistent views improve reconstruction. |
| Geometry-only | The [Pro Cloud API](https://www.tencentcloud.com/document/product/1284/75540) documents Geometry mode, outputting GLB without texture. | Good for inspecting silhouette, gaps, armor thickness, and hidden anatomy without texture concealing errors. |
| Generated PBR | The [Pro Cloud API](https://www.tencentcloud.com/document/product/1284/75540) has an explicit PBR switch; its default is false. | A colored preview does not demonstrate physically based maps. Confirm actual exported channels. |
| Parts / component splitting | Live [components UI](https://hy3d.tencent.ai/studio/creation/role/comp) describes automatic splitting with component merging and boundary adjustment. | Evaluate separation after generating a coherent whole. Splitting can create inferred hidden surfaces rather than simply detach existing polygons. |
| Retopology / polygon reduction | Live [topology UI](https://hy3d.tencent.ai/studio/creation/role/poly): Retopology V1.5, low/medium/high, triangles/quads. | Useful as a candidate mesh; joint edge flow and first-person hands still require inspection and correction. |
| UV unwrapping | Live [UV UI](https://hy3d.tencent.ai/studio/creation/role/uv) describes automatic UV seam generation. | Inspect seam placement, distortion, overlaps, padding, and texel density after final geometry changes. |
| Texture painting / editing | Live [texture UI](https://hy3d.tencent.ai/studio/creation/role/texture) shows single/multiview image-to-texture and text-to-texture. Magic Brush was disabled in the observed state. | Provisional texture work; preserve the option to finish coherent game materials in Painter. |
| Rig / animation | Live [rig UI](https://hy3d.tencent.ai/studio/creation/role/rs) describes skeleton and skinning prediction. [Animation Effects](https://hy3d.tencent.ai/studio/creation/role/ae) states standard A/T-pose humanoid driving only and lists locomotion/combat/dance templates. | Useful for a rough motion test, not evidence of a suitable FPS skeleton, finger rig, or armor behavior. |
| Export | OBJ/GLB confirmed in global launch. Live Animation Effects download menu displays FBX/USDZ/MP4/GIF. | Formats depend on workflow and selected result; this does not establish FBX or USDZ for every operation. Actual embedded textures, parts, units, and rig preservation need an export inspection. |

The live hosted upload control lists PNG/JPG/JPEG/WebP, maximum 10 MB, minimum 128 x 128 and maximum 4096 x 4096 resolution. Use these observed browser limits for Studio inputs, rather than the separate API bounds below.

The current [Pro API specification](https://www.tencentcloud.com/document/product/1284/75540) independently documents model 3.0/3.1, the eight named 3.1 views, and single-object images on a simple background, with the object occupying over half the frame. It documents 128–5000-pixel side bounds, common image formats, and a nominal 3000–1500000-face range. Model 3.1 does not accept the LowPoly or Sketch generation parameters; use a separate topology operation if needed. These are API facts; its face-count range must not replace the observed browser choices above.

For text prompts, Tencent's [prompt guide](https://www.tencentcloud.com/document/product/1284/75290) recommends one subject plus relevant shape, material, color, and style. It does not call for negative prompts or decorative quality terms such as “4k.” This supports concise component descriptions rather than long contradictory prompt lists.

## What the postprocessing tools actually do

The official [Hunyuan3D-Part repository](https://github.com/Tencent-Hunyuan/Hunyuan3D-Part) describes P3-SAM detecting semantic parts and their bounds, followed by X-Part generating complete parts. The public X-Part release is a light version; recommended X-Part inputs include scanned or AI-generated meshes. This is materially different from an exact Blender “separate selected faces” operation: newly generated hidden surfaces must be checked. Part splitting does not prove mechanically correct joints, interchangeable armor fit, or a watertight production assembly.

The international [Smart Topology API](https://www-sg.tencentcloud.com/ko/document/api/1284/77048) uses a model named Polygen/Polygon 1.5 in Tencent's translated pages. It accepts GLB/OBJ up to 200 MB, recommends an untreated high-poly input, and offers high/medium/low reduction plus triangles or mixed triangles/quads. Its documentation excludes already-topologized and some complex models from reduction. Therefore run it on an expendable copy, preserve the high-poly source, and judge the result at elbows, shoulders, fingers, and plate edges before adoption.

The international [texture edit API](https://www-sg.tencentcloud.com/zh/document/api/1284/77448) accepts FBX/OBJ/GLB and either a reference image or a text prompt. Its PBR option is documented for prompt input only. A reference-driven repaint and PBR synthesis are therefore not interchangeable capabilities. The texture set returned by the hosted UI remains unverified.

The international [auto-rigging API](https://proxy-hk.tencentcloud.com/document/product/1284/79641) performs skeleton creation and skinning on characters or animals. It specifically requires standard T-pose and FBX/OBJ at no more than 60 MB, and lists 48 preset motion IDs. It does not document an Unreal Manny-compatible skeleton, a complete articulated hand rig, or a rifle-specific animation set. Existing project T-pose preparation is useful, but the actual generated mesh must also be in T-pose.

Tencent's [Studio research paper](https://arxiv.org/html/2509.12815v1) describes a whole-shape-to-parts workflow, semantic UV seams, PBR/material editing, and humanoid/general-character animation branches. The humanoid research branch uses a 22-body-joint template and pose standardization. The paper also discusses 4K material-map generation. These are research-system descriptions and do not prove that every module, control, or quality level is enabled in the current free international account. In particular, the cited body template is not evidence of production finger articulation.

## Free quota, account and rights

The live public [Studio page](https://hy3d.tencent.ai/studio) displayed **“Limited-time Benefits: 86 times/day”** on 2026-09-17. This was observed without starting work or entering an account. Tencent's [2025 global announcement](https://www.tencent.com/en-us/articles/2202235.html) had advertised 20 free generations per day. Both facts can coexist because the live offer is explicitly temporary. Neither supports promising unlimited, permanent free service. Per-operation allocation, reset time, account eligibility, queue priority, export rights, and the promotion end date were not verified.

Cloud API free credits are different. Tencent's [Cloud FAQ](https://www.tencentcloud.com/document/product/1284/75301) describes a one-time resource package valid for one year and billing after exhaustion; it also documents default input moderation. Do not activate or call this API merely because Studio is free. No API usage is needed for the proposed first evaluation.

The public [international login page](https://3d.hunyuanglobal.com/login-email) was indexed with an email entry and agreement to terms, acceptable use, and privacy. Actual account availability in the owner's location was not tested. Tencent Cloud's [API quick start](https://intl.cloud.tencent.com/ind/document/product/1284/75287) requires a Cloud account and real-name verification; that is not evidence that browser Studio requires the same process.

Hosted commercial-use rights remain **unverified in this report**. Tencent's [SaaS privacy module](https://intl.cloud.tencent.com/pt/document/product/1284/75294) explicitly covers 3D SaaS, but privacy text alone does not grant a game distribution license. The [Cloud API terms](https://intl.cloud.tencent.com/ko/document/product/301/78149) are explicitly API terms and include separate territory/trade provisions; they must not be substituted for the hosted site's actual linked agreement. Before adopting hosted output into production, record the account-visible terms version, output ownership/commercial-use clause, input/content license, privacy/training treatment, any attribution/publication obligations, and export conditions. This is a narrow unresolved provenance check, not a claim that commercial use is prohibited.

## Local releases are an optional, separate route

- [Hunyuan3D-2](https://github.com/Tencent-Hunyuan/Hunyuan3D-2) provides separate shape and texture stages. Its official news identifies 2mv as a multiview shape release and includes a Blender addon. These are older local capabilities, not a browser Studio connector.
- [Hunyuan3D-2.1](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1) introduces PBR texturing and documents 10 GB VRAM for shape, 21 GB for texture, and 29 GB for combined execution. Hardware suitability must be measured before any installation; this research did not inspect installed hardware or start a model workload.
- The current [2.1 community license](https://raw.githubusercontent.com/Tencent-Hunyuan/Hunyuan3D-2.1/main/LICENSE) excludes the EU, UK and South Korea from its territory and expressly applies a territory restriction to outputs. It also has a threshold provision for licensees above one million monthly active users, says Tencent claims no output rights, and restricts using outputs to improve unrelated AI models. These restrictions belong to that local release; they do not establish the rights for international hosted Studio. Do not describe the local model as unrestricted worldwide commercial software.

## Bounded evaluation proposal

After identifying the owner-selected character direction and recording applicable hosted terms/visible allowance:

1. Use the same approved reference set and pose as the other services. Preserve the original art, record exact file hashes and input-view mapping, and do not upload the entire project.
2. Generate one whole-character candidate with restrained initial settings. Record model/version, views, operation, displayed cost, queue/runtime, and downloaded source package. This report does not authorize the run.
3. Compare clay geometry before textures: front/back/profile silhouette, helmet, shoulder mobility, hand separation, crotch, boots, hard plate boundaries, inferred back surfaces, and left/right consistency.
4. If the whole is coherent, test one bounded component split on a copy. Inspect newly inferred inner surfaces and whether each piece remains aligned to the same body.
5. In Blender, retain a single original deforming body/undersuit and fit selected armor objects around it. Repair topology and intersections. Do not weld rigid plates into soft anatomy merely to create one object.
6. Evaluate one topology result, then establish final UVs, bake retained high-poly detail, and finish consistent PBR materials. Decide on a production skeleton and weights independently of a convenient vendor preview rig.
7. Verify a complete export in Blender and Unreal: scale/orientation, material channels, part transforms, normals, skeleton/fingers, shoulder and crouch deformation, rifle grip and reload clearance, first-person arms, and LOD behavior.

Accept a vendor candidate only if it saves the total work of reaching those checks. Successful generation and a pleasing viewer preview are not the same as a production-ready protagonist.
