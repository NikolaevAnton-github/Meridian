# MSQ-166 / DS-06 handoff

Implemented in the [direct batch](DestructionScaling01Batch01.md), under the owner's [scoped exception](Approvals/DestructionScaling01-DirectBatch01.json).

Moved fragments gather owned identity/revisions, pose and immutable hull references after physics. Coarse UE Tasks batches calculate exact lowest hull points while the game thread publishes changed spatial bounds and invalidates support dependencies. The explicit completion boundary precedes exact engine queries and same-frame apply. Invalidated results are rejected/recomputed; reset and world teardown retain no borrowed storage.

`msq.Destruction.Parallel=0` selects serial, `1` uses parallel above 128 moved hulls, and `2` forces a small controlled comparison against the serial calculation. Batches contain up to 64 fragments. Diagnostic counters expose jobs, rejected results and exact serial comparisons. No async-physics/timestep settings were changed.

Final build and focused serial/parallel/reset evidence are in the batch handoff. No separate parallelism performance claim is made for a small workload below the normal threshold.
