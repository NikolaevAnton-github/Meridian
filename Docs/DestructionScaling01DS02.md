# MSQ-162 / DS-02 handoff

Implemented in the [direct batch](DestructionScaling01Batch01.md), under the owner's [scoped exception](Approvals/DestructionScaling01-DirectBatch01.json).

`DestructionFragmentState.h` defines owned IDs, revisions and pure pose/hull calculations. Cladding captures stable tile/concrete identity before pending projectile hits are applied. Swap-removal refreshes the exact tile mapping; a disappeared target consumes its original step-start round without redirecting to the swapped-in neighbour. Fragment handles survive world recreation without reuse.

The world lifecycle owns snapshots and resolves Chaos particles only in the safe read/solver phases. Worker snapshots contain values and shared immutable hull arrays. They never borrow component arrays, UObject references or Chaos pointers. Selected adapters return `Applied`, `Queued`, `Stale`, `UnsupportedState`, `Unavailable` or `InvalidInput` explicitly.

The restored production baseline was built before runtime checks; source and DLL identities are in `Saved/LobbyColumnsPerf02/ds02_production_baseline_20260929.json`. Integrated final build and functional evidence are recorded in the batch handoff. Owner acceptance is separate.
