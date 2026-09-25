# NGD-03: Toolkit load, slowdown and playable handoff

Multica issue: **MSQ-151**. Parent: [MSQ-74](../EnvironmentDestruction01.md).
Prepared 2026-09-25; unassigned backlog, no execution authorized.
Authority and shared rules: [toolkit integration plan](../EnvironmentDestruction01Plan.md)
and [owner task rewrite](../../Approvals/NextGenDestruction01-TaskRewrite01.json).
Prerequisite: [NGD-02](NGD-02.md). AI integration/traversal are separate consumers.

## Work and acceptance

- Populate the same bounded fixture with a small reproducible set of the accepted
  technical specimen. Define counts/settings and derive budgets from measured
  baseline; no whole-lobby production, new materials or unlimited stress population.
- Measure empty baseline, intact objects, isolated/overlapping breaks, settled
  debris and repeated reset at fixed camera/shot sequences. Record frame time,
  Game/Render/GPU and available physics cost, P95/max spikes, sample duration,
  active bodies and memory trends with engine/hardware/render settings.
- Address demonstrated hotspots through bounded activation, sleep, collision/effect
  cost and cleanup. Preserve NGD-01/02 shot, material, support and collision behavior.
  Show visual comparisons for quality tradeoffs; FPS/average alone cannot close hitches.
- Check normal time, entry to slowdown, active debris/cleanup under slowdown,
  restoration and reset: world/projectiles/rifle cadence 0.25, hero movement 0.65.
  No full time-stop implementation. Keep movement/fire/reload baseline intact.
- Verify final fixture reset/return to play and bounded repeated usage. Reuse prior
  evidence unless changed behavior or a concrete gap warrants a focused recheck.
- Deliver one identified owner-ready map/configuration with controls, candidate,
  settings/counts, performance table, known limits, review finding closure and
  explicit pending owner play/visual judgement. List MSQ-131 and MSQ-78 consumer
  contracts without claiming their behavior is already integrated.

Use one primary independent technical reviewer under the plan; technical delivery
does not imply owner design/play approval. MSQ-74 can close its technical integration
scope after all three child handoffs; it does not depend back on AI or traversal.
Evidence: `Saved/NextGenDestructionIntegration01/NGD-03/<candidate>/`.
