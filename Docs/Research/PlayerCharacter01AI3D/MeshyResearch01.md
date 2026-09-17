# Meshy research for PlayerCharacter01

Research date: 2026-09-17. Scope: the owner's existing Meshy web subscription and its potential contribution to an original armored, full-body first-person protagonist. This is research and workflow design, not character selection, production modeling acceptance, or permission to buy credits.

## Evidence and current status

The findings below come from Meshy's official help center, product changelog, product announcements, API documentation and terms. Features documented for the API are separated from web features. No generation, upload, download, rigging job, API request, key inspection, purchase or account modification was performed by this research task.

The root controller separately inspected the owner's open Meshy workspace during this task and reported seeing Smart Topology, Meshy T2, a triangle target of 15,000, Texture enabled, A/T/custom pose controls, Private selected and a displayed generation price of 15 credits. This confirms those controls are visible in this account; it does not establish output quality or all feature combinations. No account balance is recorded here. Remaining capabilities below are documentation findings unless explicitly marked as observed.

The installed Meshy generation skill is API-oriented and contains older model/cost assumptions. Its API recipes were read for orientation only. This report does not activate paid API work.

## What Meshy can contribute

| Capability | Current documented behavior | Use for our protagonist |
| --- | --- | --- |
| Text to 3D | Generates geometry from a description, with texturing as a subsequent step. Meshy recommends image input when exact appearance matters. | Exploration only; an approved character image gives stronger design control. [Text to 3D guide](https://help.meshy.ai/en/articles/9996858-how-to-use-meshy-text-to-3d) |
| Image to 3D | Accepts PNG/JPG/JPEG/WebP up to 20 MB; includes background removal, pose options and image enhancement. The model stage returns a white mesh. | Generate a candidate from the isolated character or a prepared component sheet; inspect the untextured shape before paying for appearance. [Image to 3D guide](https://help.meshy.ai/en/articles/9996860-how-to-use-meshy-image-to-3d) |
| Meshy 7 high detail | The current web documentation names Meshy 7; the changelog also describes Ultra geometry and Meshy 7 Texture. | Candidate for detailed shape and multiview reconstruction, subject to the actual account picker. [Web changelog](https://docs.meshy.ai/en/webapp/changelog) |
| Smart Topology / T2 | The web changelog documents low-poly generation with native part segmentation and controllable polygon count. T2 and triangle control were observed in the owner's workspace. | A separate candidate route for lighter, separated geometry. Inspect actual boundary quality; visible part separation is not proof of correct armor thickness or rig-ready joints. [Web changelog](https://docs.meshy.ai/en/webapp/changelog) |
| Multiview geometry | Meshy 7 web workflow supports one main image plus up to three auxiliary views. Smart Topology and Multi-View cannot currently be enabled together. | Choose between multiview shape control and native low-poly topology; do not design a recipe that requires both simultaneously. [Multi-View help](https://intercom.help/meshy/en/articles/12634481-how-to-use-multi-view) |
| AI image preparation | Text/image generation, style references and A/T poses; image creation accepts up to five references. | Optional reference repair. Preserve approved originals and inspect every generated complementary view before 3D. [Image creation guide](https://help.meshy.ai/en/articles/12005614-how-to-create-images-in-meshy) |
| Remesh / quad output | Produces a separate remeshed version; can lose detail. GLB triangulates quads; FBX or OBJ preserves quad faces for DCC editing. | An optional starting mesh for Blender, not automatic acceptance of deformation topology. Keep the original high-detail source. [Quad export guide](https://help.meshy.ai/en/articles/9992029-how-to-download-a-quad-mesh-model) |
| UV Unwrap | A web viewer tool is documented. | Optional draft UVs; the final UV layout should follow the finished mesh and first-person texel needs. [Workspace tour](https://help.meshy.ai/en/articles/12618267-meshy-interface-tour-workspace-tabs-and-navigation) |
| Texturing / Retexture | Meshy models and uploaded models can receive new textures from prompts; PBR and resolution options are documented. | Preview material direction, then retain or rebake useful maps in the final material workflow. [Text-to-texture help](https://help.meshy.ai/en/articles/9996850-how-to-use-the-text-to-texture-feature) |
| Rigging / animations | Humanoid, quadruped and beta Smart Rig modes are documented. Humanoid bone names follow Mixamo conventions. | Quick locomotion/deformation probe; final weapon handling requires a separately checked skeleton, skinning and hand control. [Auto-rigging guide](https://help.meshy.ai/en/articles/16231707-how-to-create-3d-animation-with-auto-rigging) |
| 3D Agent / ancillary tools | Chat generation, texturing and batch operations; image/video and 3D-to-image functions are also documented. | Convenience features, not necessary stages for the protagonist. Do not spend credits on image/video previews to judge mesh correctness. [Agent guide](https://help.meshy.ai/en/articles/15297780-getting-started-with-meshy-agent), [Feature catalog](https://help.meshy.ai/en/articles/9991738-what-features-does-meshy-have) |

## Multiview input and our eight-view package

The documented web upload slots are Main/Front, Left, Back and Right. Use separate, matching views at comparable scale and lighting, with one isolated subject and separated limbs. The official guide supports four total inputs; eight delivered concept views do not mean eight images can be uploaded in this workflow. Preserve the two 45-degree and two axial views as inspection references rather than forcing them into side slots. [Multiview tutorial](https://www.meshy.ai/tutorials/multi-view-image-to-3d)

Meshy's best-practices guide explicitly says inconsistent supplemental images can perform worse than one clean reference. Our generated turnaround is input art with unverified 3D consistency: align silhouettes and compare helmet, cuirass, belt, shoulder, elbow, knee and boot details before selecting four inputs. AI-generated complementary views remain design inferences. More views do not resolve contradictions automatically. [Multiview best practices](https://help.meshy.ai/en/articles/16102789-meshy-multi-view-best-practices-angles-and-images)

API distinction: the Multi-Image endpoint accepts 1-4 JPG/JPEG/PNG inputs. Meshy 7 uses the first as the primary/front reference; its API says remaining order is immaterial. The current endpoint lists Meshy 6, 6 Lite, 7 and latest, whereas web help restricts Multi-View to Meshy 7. Follow the surface-specific contract; the API model list does not establish web availability. [Multi-Image API](https://docs.meshy.ai/en/api/multi-image-to-3d)

## Parts: three different operations

1. **Native multipart generation:** Smart Topology creates lower-density meshes with parts in one generation. The T2 research announcement discusses naturally disconnected components and approximate budget bands, not exact counts. This is worth testing for armor, but it does not promise an underlying body or mechanically correct separation between layers. [T2 announcement](https://www.meshy.ai/blog/meshy-t2-native-3d-mesh-generation)
2. **Auto Split / semantic cuts:** Auto Split documentation describes watertight pieces, capped cuts, build-plate preparation, optional thickening and connectors. The changelog also adds semantic head/limb/torso cuts. Such output may be printable while unsuitable for an animated character; a capped arm cut is not a finished shoulder deformation interface. [Auto Split help](https://help.meshy.ai/en/articles/15898622-how-does-auto-split-work-in-meshy), [Web changelog](https://docs.meshy.ai/en/webapp/changelog)
3. **Authoring components separately:** Our proposed production method is to establish one proportion reference/body first, then create or rebuild a bounded set of hard pieces around it in Blender. Independent generation of every limb and plate risks incompatible scale, thickness, seams and style. This is a project recommendation, not a Meshy guarantee.

The general Image-to-3D help loosely describes Auto Split as separating clothing/accessories, while its dedicated page describes printing operations and even contains conflicting draft/texturing-order language. Therefore an actual split export must be inspected before classifying it as useful game modularity. Do not activate print connectors or wall thickening for game production by default.

For this hero, keep the deforming undersuit/body continuous where useful, with helmet, cuirass, shoulder armor, forearm protection, belt equipment and other rigid attachments handled as deliberate components. Retain separate editable objects in the Blender source. Combining objects with Join alone neither welds boundaries nor binds them to a common skeleton. This is our proposed DCC architecture, pending the selected design and movement tests.

## Textures, UVs and export traps

Meshy's August multiview announcement explicitly describes 2K/4K/8K **base color only**, with metallic, roughness and normal maps absent from that particular multiview texture release. It supports a later texture stage on generated or imported untextured geometry. Do not equate multiview texture with a complete PBR delivery. [Multiview upgrade](https://www.meshy.ai/blog/multiview-upgrade)

The current Retexture API separately documents PBR generation, original-UV preservation and multiview inputs; it also warns that model availability may be account-gated. Generic PBR capability does not settle which maps the multiview mode currently exports. Record the actual delivered maps, resolution and channel packing per candidate. [Retexture API](https://docs.meshy.ai/en/api/retexture)

For uploads, the web help specifies a 100 MB ceiling, removal of non-mesh objects, animations and shape keys, and merging multiple meshes. Keeping original UV/texture requires one material and one UV map after merge, with no overlapping islands. Consequently, a finished multi-object, multi-material, rigged Blender assembly should not be round-tripped through Meshy without a dedicated disposable export. Web exports include FBX, OBJ, GLB, USDZ, STL and BLEND, plus printing formats. [Format and upload requirements](https://help.meshy.ai/en/articles/9991884-what-3d-file-formats-does-meshy-support-full-export-list)

Use FBX or OBJ when retaining quad faces, and GLB for a compact textured reference when triangles are acceptable. Keep texture dependencies beside FBX/OBJ exports. A BLEND export is a useful imported source, not evidence that topology, rig or materials satisfy our project requirements.

API UV Unwrap is more constrained: GLB only, at most 40,000 faces, quad/ngon triangulation, new UVs and a placeholder material rather than retained textures. API Remesh supports quad-dominant or decimated triangles with a 100-300,000 polygon target range; actual output may differ. These are API limits, not assumed web slider limits. [UV Unwrap API](https://docs.meshy.ai/en/api/uv-unwrap), [Remesh API](https://docs.meshy.ai/en/api/remesh)

Finalize topology and UVs before final texturing. If the mesh changes, rebake/reproject useful original detail. Meshy's own production workflow recommends cleanup, retopology, deliberate UVs and high-to-low baking in Substance Painter. In our stack, Blender fills the mesh/sculpt role; Painter builds consistent materials for metal, fabric, rubber and visor. [DCC/Painter workflow](https://help.meshy.ai/en/articles/16103076-meshy-with-zbrush-and-substance-painter-workflow)

## Rigging, hands and first-person use

For the web workflow use the Humanoid path for this biped, then inspect the exported FBX skeleton and weights. The official guide advertises over 600 motion presets, but explicitly says beta Smart-rigged models cannot currently use its animation library and quadrupeds only have walking. Do not confuse a feature called Smart Rig with the standard humanoid animation path. [Auto-rigging guide](https://help.meshy.ai/en/articles/16231707-how-to-create-3d-animation-with-auto-rigging)

The API has a narrower documented contract: clearly separated humanoid limbs, textured inputs, GLB URL upload, +Z forward, and a 300,000-face ceiling for input tasks. It returns rigged FBX/GLB and basic walking/running. API tasks do not appear in web My Assets. These limits must not be silently copied onto web controls or vice versa. [Rigging API](https://docs.meshy.ai/en/api/rigging)

No inspected official specification guarantees a particular finger-bone count, clean trigger-finger isolation, twist bones, hand IK, weapon sockets, reliable reload contacts or our Unreal skeleton compatibility. Meshy itself warns of fused/missing/extra fingers and recommends DCC repairs. First-person hands are therefore an explicit custom mesh/rig/animation quality task even when the full-body draft looks good. [Character/hand limitations](https://help.meshy.ai/en/articles/16102152-fix-character-pose-face-and-hand-issues-in-meshy)

Our proposed acceptance probes: shoulder lift, elbow bend, forearm twist, open/closed hand, trigger-finger isolation, rifle grip, reload reach, crouch and walk. Look for armor bending like cloth, collapsed joints, self-intersection, drifting contacts and camera-visible texture defects. These are project tests; Meshy animation preview alone cannot pass them.

## Credits, subscription and API boundary

The user owns a web subscription; its exact tier and remaining allowance are not assumptions for this report. The observed T2 configuration showed 15 credits with texture. The web task-cost reference currently lists Meshy 7 geometry 25, Meshy 6 geometry 20, T2 geometry 5, texture 10 for 2K/4K or 15 for 8K, Auto Split 10, Smart-Rig 0 and text-to-motion 3. It explicitly defers to the price shown before running a web task. Pro and above downloads do not consume credits. [Web credit schedule](https://help.meshy.ai/en/articles/10000507-how-many-credits-does-each-generation-task-cost)

Examples for planning only: two T2 untextured drafts would be 10 listed credits; one T2 textured draft would be 15; one Meshy 7 draft plus 2K/4K texture would be 35 on the listed web schedule. Verify the live price and free-retry entitlement first. A visually disappointing but technically completed model is generally not refunded; task failure and cancellation while queued are treated differently from cancellation after processing starts. [Credit refunds](https://help.meshy.ai/en/articles/15643245-when-were-my-meshy-credits-used-or-refunded)

API pricing is separate documentation: Meshy 7 geometry is listed as 20 plus 5 for Ultra, rigging 5, animation 3 per action, Remesh 5 and UV Unwrap 5. The API page calls usage prepaid and directs users to buy credits. However, the official MCP help says requests consume the connected account balance like web/API use, and plan help lists API access on paid tiers. The sources do **not** support assuming either unlimited included API work or a universally separate credit wallet. [API pricing](https://docs.meshy.ai/en/api/pricing), [MCP account/credits help](https://help.meshy.ai/en/articles/16102957-meshy-mcp-server-and-ai-coding-agent-setup), [Plan comparison](https://help.meshy.ai/en/articles/12062933-which-meshy-plan-is-right-for-you-free-vs-pro-vs-premium-vs-ultra)

Operational decision: use the owner's existing web entitlement for the proposed pilot after its scope is authorized; do not enable API automation, recharge or additional purchases from the subscription announcement alone. Keep one generation active at a time and measure repair effort, not just generation speed.

## Ownership and privacy evidence

Current ownership help says paid users retain private ownership if they use authorized inputs and do not publish to Meshy Community; the commercial-use help permits commercial projects and describes Free outputs as CC BY 4.0. Preserve Private for original protagonist work and record the selected license with generation provenance. [Ownership help](https://help.meshy.ai/en/articles/10137554-what-is-the-ownership-of-the-generated-models), [Commercial-use help](https://help.meshy.ai/en/articles/9992001-can-i-use-meshy-assets-commercially-license-copyright-explained)

A documentation date conflict matters here: the retrieved terms page is labeled **September 19, 2026**, two days after this research date, and says changes take effect on its stated date. That page describes a CC0 consequence for Community publication and distinguishes generated output from service assets such as supplied rigs/animations. It cannot establish which terms were already effective on September 17. Capture the effective terms at actual production use and before release; do not infer unrestricted standalone resale of Meshy's motion library from generated-model ownership. [Retrieved terms](https://www.meshy.ai/terms-of-use)

The public pricing FAQ says web data is hosted on AWS in the United States and not shared or used for training without consent. This is a vendor statement, not an independent privacy audit. [Pricing/data FAQ](https://www.meshy.ai/pricing)

## Proposed bounded validation sequence

1. Freeze the named character direction and identify any unresolved view contradictions. The current Datum input packages remain references until the owner selects the production design.
2. Record web model version, mode, pose, license, input identities and displayed cost. Prepare a whole-character proportion trial and a separate helmet or forearm-armor trial; do not start with dozens of unrelated parts.
3. Compare Meshy 7 multiview high-detail shape with T2 single-image multipart output only where that comparison answers a production question. Inspect untextured geometry first.
4. Import the chosen candidate in Blender; check dimensions, connected components, underside surfaces, topology, normals, material slots and the actual hand shapes. Preserve the untouched download separately from working files.
5. Use a common body/proportion reference to fit rigid armor and rebuild weak surfaces. Retopologize deforming regions and make first-person hands deliberate original assets.
6. Finalize UVs, bake retained detail and finish material families in Painter. Keep a small 2K/4K trial before considering 8K.
7. Bind to the chosen production skeleton; use Meshy humanoid rigging only if an exported trial saves time. Run hand/weapon and full-body deformation checks in Blender, then Unreal.
8. Accept the result based on approved-design fidelity, close first-person views, animation, actual performance and editable provenance. Choose a provider by total usable-result cost, including manual repair.

This sequence is a project recommendation. No provider quality winner, final topology budget, production skeleton or approval of modeling is established by documentation research.
