# Prototype play defaults

Owner request, 2026-09-29: two direct local changes outside the planned task queue.

- Enemy AI starts disabled. **Ctrl+F10** enables/disables AI on the existing enemy;
  this does not reset the encounter, change the fixture count or respawn actors.
  F6 and fixture recreation preserve the selected session setting.
- Infinite ammunition starts enabled. **Ctrl+F8** toggles it. Enabled mode does not
  consume magazine/reserve ammunition and rejects reload requests. Enabling it
  refills the magazine, cancels an active reload and clears the empty-fire latch.
  Disabled mode retains finite ammunition, empty-fire feedback and normal reloads.
- The HUD displays both switches. Existing V fire-mode selection is unchanged.

The retained `bInfiniteReserve`/`ToggleInfiniteReserve` API names now describe this
full infinite-ammunition behavior, preserving existing reflected references.
The enemy AI switch is separate from the one-enemy/three-fixture selection.
Finite-ammunition timing probes explicitly scope their mode and restore the play
setting on completion.

Focused technical evidence: `Saved/PrototypeDefaults01/`. Final gameplay testing
and acceptance remain with the owner. No Multica task was created or dispatched.

Development Editor build passed (`build.log`) and the editor was reopened with
the rebuilt DLL. `runtime.json` records 21 passing checks through real simulated
key input: both chords, stable enemy identity, 58 shots without ammunition loss
or reload, finite empty/reload behavior, cancellation when enabling infinite mode,
stale-notify rejection and reset/recreation persistence. Background editor CPU
throttling was temporarily disabled for this bounded check and restored afterward;
the initial throttled run is retained separately. PIE is stopped and no editor
packages were changed or saved by the checks.
