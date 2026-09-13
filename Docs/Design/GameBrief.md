# Game direction

Owner brief recorded on 2026-09-13. This document distinguishes product goals
from the scope of the first environment milestone. MeridianSquad is the current
project/repository name; a final public game title has not been established.

## Fixed product direction

- A realistic first-person shooter in a dark near-future setting.
- Shooting is the highest gameplay priority. The owner wants strong perceived
  impact, enemy body destruction, and extensive environmental destruction.
- Player abilities: time slowdown, force push, and telekinesis. Their costs,
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

## First owner-visible milestone

An explorable skyscraper entrance lobby inspired by the lobby in The Matrix
(1999). The owner should be able to start Play in Unreal, move on foot, look
around at first-person height, and judge scale and atmosphere.

The immediate deliverable is the lobby walkthrough. Combat, abilities, enemy
body damage, live environmental destruction, squad-death staging, cinematic
arrival, surveillance exposition and a complete opening mission are later work.
Static damage can establish the environment without committing to how the
catastrophe or the protagonist's survival occurs.

Build the space in sequential reviewable stages, with one writer per editor.
Use the existing project, Multica and asset registry. Do not duplicate the
Unreal project or introduce another orchestration system.

See [lobby milestone and acceptance](../Tasks/OpeningLobby.md).
