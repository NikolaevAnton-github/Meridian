# Opening lobby concept art and owner approval

Multica task: MSQ-8, a separate child of the lobby milestone MSQ-4.

Owner decision recorded on 2026-09-13: the existing lobby layout does not match
the intended space. Create concept art as a separate task and obtain explicit
owner approval before planning or producing its 3D layout and models.

## Scope and direction

Read [game direction](../Design/GameBrief.md),
[story canon](../Design/StoryCanon.md), and the
[lobby milestone](OpeningLobby.md). The target remains a realistic, dark
near-future skyscraper entrance lobby. The owner has now explicitly selected a
close recreation of the Matrix lobby using two supplied images saved as
[OwnerReferences01](../../Assets/Concepts/OpeningLobby/OwnerReferences01/README.md).
Follow those images closely instead of continuing the exploratory A/B/C designs.
The supplied images already provide the chosen visual basis; do not commission
a new art round merely to redraw them. Reference images are not game textures.

The saved Stage 1 room, its 36 x 22 x 8 m dimensions, column spacing, security
placement and broad central aisle are an unapproved draft. Do not make them
constraints for the new concepts. Preserve the saved map and its evidence.

## Deliverables

1. The first review set is complete and superseded by the owner's supplied
   OwnerReferences01 direction. For any requested refinement, show the
   main space at human eye level, with architecture, proportions, column rhythm,
   circulation, materials and light readable. Keep comparisons easy to judge.
2. The owner confirmed that the supplied images are opposite views of one hall.
   Preserve this relationship in any supplemental view.
   Develop extra views only for an identified missing detail or an owner request.
   Do not force an additional generation round when the references suffice.
3. Preserve the images, prompts, reference roles and concise English notes in
   `Assets/Concepts/OpeningLobby/`. Give every review version a stable name.
   Keep generated logs and discarded scratch outputs under
   `Saved/OpeningLobby/ConceptArt/`; use existing Git LFS rules for images.
4. Record the exact version and views the owner explicitly approves, the approved
   visual choices, requested revisions and remaining open questions separately.
   Until that approval, the task remains pending review and implementation is
   gated. Do not invent an approval entry.

## Acceptance and limits

- Deliver actual concept-art images for review. A prompt, prose description,
  reference collection or polished screenshot of the rejected blockout alone
  does not complete this task.
- Keep the architecture legible without hiding it behind darkness, fog or
  destruction. Unresolved damage, narrative staging and spatial anomaly details
  remain proposals; do not add squad bodies or establish a cause of death.
- No Unreal layout changes, Blender meshes, Painter projects, modular asset
  production plans or final dimensional plans during the art task. Approval of
  art authorizes preparation of a separate layout task, not automatic completion
  of the remaining milestone.
- Use the existing subscription only. Do not use paid image APIs, extra credits,
  asset purchases or new services. Verify the available generation route before
  dispatching a worker; do not assume a CLI worker has the direct chat's image
  tools. Keep task state in Multica and do not create another dispatcher.
- Technical prototype acceptance, silence and a general request to continue
  are not approval of a concept-art version.

## Current approval record

Review01 contains three initial directions and their exact generation prompts:
[`Assets/Concepts/OpeningLobby/Review01`](../../Assets/Concepts/OpeningLobby/Review01/README.md).
The images were generated with the built-in image tool after a bounded Multica
art-direction preparation run. They are now historical alternatives and have
been superseded by the owner's supplied OwnerReferences01 images.

The owner selected OwnerReferences01 as the desired visual direction and then
confirmed its two images are opposite views of the same hall. This confirmation
resolves image orientation; it is not final art-package approval. Continue MSQ-8
with one oblique entrance/security study to clarify the screening equipment and
its connection to a side aisle. The study is now generated and saved in
[LobbyArt-Review02](../../Assets/Concepts/OpeningLobby/Review02/README.md), whose
review package combines it with the unchanged reference pair.

The owner subsequently explicitly approved LobbyArt-Review02 in response to
the question identifying all three views and the transition to layout.
The approved files and SHA-256 hashes are recorded in
[`Review02/approval.json`](../../Assets/Concepts/OpeningLobby/Review02/approval.json).
MSQ-8 is accepted. This approval authorizes the separate
[Layout02 walkthrough revision](OpeningLobbyLayout02.md); it does not approve
the rejected Stage 1 layout or complete the environment milestone. MSQ-6 and
MSQ-7 remain unassigned in backlog pending the revised walkthrough review.
