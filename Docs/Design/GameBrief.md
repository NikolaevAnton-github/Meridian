# Game direction

Combat priority update, 2026-09-23: prioritize good enemy AI, shooting quality and
environmental destruction. Advanced body damage and dismemberment are deferred
until after that priority work; they do not block the initial combat slice.
Ordinary damage, hit reactions, death and ragdoll remain. See the
[owner decision](../Approvals/CombatPriorities01-OwnerScope01.json).

Combat AI direction update, 2026-09-23: the owner explicitly describes an **arcade
shooter** and asks for surprising, excellent enemy AI without excessive pressure.
Enemies should run, keep searching after contact, hear footsteps and respond to the
source of incoming fire. See the [exact request](../Approvals/CombatAI01-Planning01.json),
[design proposal](CombatAI01.md) and [implementation plan](../Tasks/CombatAI01Plan.md).
The plan does not start gameplay production or approve all proposed mechanisms.
Existing visual/narrative direction remains; realistic presentation does not impose
simulation-style combat. The latest [cadence decision](../Approvals/CombatSlowdownCadence01-OwnerScope01.json)
sets world, bullets and rifle cadence to 0.25 while hero movement stays at 0.65,
superseding the earlier normal-player/faster-player-firing descriptions below.

Combat execution update, 2026-09-18: the owner authorizes MSQ-68 and fixes the
[time/projectile policy](../Approvals/CombatFoundation01-OwnerScope01.json): player
movement remains normal while the rest of the world slows or stops. All bullets,
including the player's, follow world time and may injure their shooter. The hit
foundation must support this now; the actual time ability and player health are
implemented in their later tasks. Ability input/cost/duration remain proposals.

Gameplay planning update, 2026-09-18: the owner requested preparation of a
sequential task family for combat, representative body/environment damage,
time slowdown, force push, telekinesis and a bounded opening episode. See
[CombatSlice01](../Tasks/CombatSlice01Plan.md) and the
[exact decision](../Approvals/CombatSlice01-TaskCreation01.json). Tasks are prepared
as unassigned backlog; this does not dispatch implementation, approve new art or
settle unspecified ability rules/story staging. Purchased arms remain the baseline;
original protagonist work and deferred lobby architecture stay paused.

Current lobby scheduling, 2026-09-16: the owner closed all remaining lobby tasks
and deferred further work until a new owner list after gameplay integration.
See [the closure decision](../Approvals/LobbyDeferred01-OwnerClosure01.json).
Earlier lobby dispatch/status wording below is historical; fixed product
direction is unchanged. This closure does not commission a gameplay task.

Owner brief recorded on 2026-09-13. This document distinguishes product goals
from the scope of the first environment milestone. MeridianSquad is the current
project/repository name; a final public game title has not been established.

## Fixed product direction

- An arcade first-person shooter in a dark near-future setting, in **2043**
  (setting direction on 2026-09-16; arcade combat clarification on 2026-09-23).
- Shooting is the highest gameplay priority. The owner wants strong perceived
  impact, enemy body destruction, and extensive environmental destruction.
- Player abilities: world time slowdown/stop, force push, and telekinesis. Their costs,
  limits, progression, controls, and interactions have not been specified.
- Primary game references: F.E.A.R., Control, and TimeShift. References guide
  experience and combat; they do not import those games' settings or systems.
- Narrative foundation: [Story canon](StoryCanon.md). Spatial distortion grows
  toward the wounded antagonist; the protagonist's time-related ability does
  not give the spatial antagonist control of time.

The impact goal will later require coordinated weapon response, animation,
enemy reactions, sound, particles, decals, physics and damage behavior. These
are future implementation areas, not systems already present in the project.
No multiplayer scope or target shipping platform beyond the current Windows
prototype has been committed.

Latest protagonist continuation, 2026-09-16: the owner prefers Concept01 variants
01 and 08 and requests ten further directions with more armor while remaining
mobile, plus a closed helmet containing a computer for the interface. See
[Concept02 direction](../Approvals/PlayerArtConcept02-Direction01.json) and
[task](../Tasks/PlayerArtConcept02.md). This is a direction preference, not final
modeling approval. The 2043 setting and owner-only concept evaluation remain.

Initial protagonist concept direction, 2026-09-16: produce at least 15 original
MERIDIAN protagonist alternatives with fully concealed faces, respecting the
story canon and 2043 setting. The concept artist uses Astra/max/standard; the
owner alone evaluates this concept batch, with no independent expert review.
See [the direction record](../Approvals/PlayerArtConcept01-Direction01.json) and
[concept task](../Tasks/PlayerArtConcept01.md). This authorizes MSQ-51 concept
execution only. A named owner selection is still required before modeling;
later integrated gameplay review remains unchanged.

## First owner-visible milestone

An explorable skyscraper entrance lobby closely matching the lobby in The Matrix
(1999). The owner selected the supplied
[OwnerReferences01 images](../../Assets/Concepts/OpeningLobby/OwnerReferences01/README.md)
as the visual basis, superseding the initial A/B/C studies. The owner should be
able to start Play in Unreal, move on foot, look
around at first-person height, and judge scale and atmosphere.

The owner explicitly approved `LobbyArt-Review02` on 2026-09-13: the supplied
reference pair and the [Review02 entrance security supplement](../../Assets/Concepts/OpeningLobby/Review02/README.md).
The [lobby art task](../Tasks/OpeningLobbyConceptArt.md) has met its owner approval
gate, authorizing the separate [layout revision](../Tasks/OpeningLobbyLayout02.md).
The earlier orientation confirmation established that the source pair shows
opposite ends of one hall; the subsequent explicit approval accepts the identified
art package. Off-camera connections and the small inner door's function remain
unresolved. The owner subsequently rejected MSQ-9/Layout02's
architectural scale and requires a monumental space at least twice as large.
The [dimensioned scale package](../OpeningLobbyScaleReview.md) passed independent
review and received explicit owner approval on 2026-09-14, including exact
dimensions and human-use exceptions. It authorizes the separate
[Layout03 neutral blockout](../Tasks/OpeningLobbyLayout03.md);
LobbyArt-Review02 remains the visual basis. After technical and independent
visual review of Layout03/Correction01, the owner explicitly accepted the
in-game scale on 2026-09-14 and authorized continuing. Detail assessment is
deferred; see the [scoped decision](../Approvals/LobbyLayout03-Scale01.json).

The owner rejected the current Stage 1 layout. Its technical acceptance does
not approve its layout or art direction; preserve that prototype and its evidence.
MSQ-6 [architecture/material production](../Tasks/OpeningLobbyArchitecture01.md)
is now authorized with the accepted scale preserved. MSQ-7 atmosphere work
remains in backlog pending architecture/material review and owner detail acceptance.

The first playable environment milestone remains the lobby walkthrough.
Combat, abilities, enemy body damage, live environmental destruction,
squad-death staging, cinematic arrival, surveillance exposition and a complete
opening mission are later work.
Static damage can establish the environment without committing to how the
catastrophe or the protagonist's survival occurs.

Begin with concept art and dimensioned drawings with explicit owner approval, then build the space
in sequential reviewable stages, with one writer per editor.
Use the existing project, Multica and asset registry. Do not duplicate the
Unreal project or introduce another orchestration system.

See [lobby milestone and acceptance](../Tasks/OpeningLobby.md).
