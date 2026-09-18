# LobbyEncounter01: a short repeatable lobby firefight

Multica issue: **MSQ-72**.
Stage 6 of [CombatSlice01](CombatSlice01Plan.md).
Predecessor: [PlayerSurvival01](PlayerSurvival01.md).

## Scope

Build one small encounter, initially capped at three enemies, using the verified
prototype and existing lobby cover. Mark this count as tuning, not a fixed game
requirement. Define start trigger, spawn positions, encounter completion and reset.
Use lightweight cover-position choice and movement between reachable positions;
no squad-command framework or final narrative placement.

Tune firing opportunities and incoming-fire readability so the player can fight,
reload and reposition. Add only removable gameplay/navigation actors. Record the
positions used, preserve architectural scale/materials/light and keep the ordinary
walkthrough possible when the encounter is disabled. This is a combat test scenario,
not a canonized account of the protagonist's arrival.

## Acceptance

- Start, engage, win, die and restart the bounded encounter with correct actor
  counts and no repeated spawn/completion events.
- Enemies use reachable cover positions, avoid firing through columns and do not
  block the player through invalid collision or persistent spawn congestion.
- The fight gives readable hit and incoming-fire feedback; completion is visible.
  Record owner-playable controls and unresolved balance observations.
- Capture comparable gameplay views and a bounded performance sample with settings
  and actor counts. Diagnose introduced costs; do not repeat unrelated benchmarks.

No new level layout, ability, destruction or mission script. Follow the parent
plan; deliver `Docs/LobbyEncounter01.md`, placements and focused play evidence.
