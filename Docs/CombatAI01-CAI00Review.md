# MSQ-102 / CAI-00 primary independent technical review

Date: 2026-09-23. Candidate: **Candidate01/build02**.
Verdict: **PASS for the authorized source/build and pure capture-contract scope**.
No blocking source findings remain. Gameplay, motion, audio/readability, in-engine
reset/export and performance acceptance remain **PENDING OWNER**.

This is the sole primary independent technical review under
[the scoped owner start](Approvals/CombatAI01-CAI00-OwnerStart01.json) and
[CAI-00](Tasks/CombatAI01/CAI-00.md). Review used Astra/high at standard speed.
The reviewer inspected the changed source, direct lifecycle/authority call sites,
executor checks and [handoff](CombatAI01-CAI00.md). No editor operation, Play,
gameplay probe, firing, rebuild or test rerun was performed. Controller scope,
preservation acceptance, status and commit remain separate responsibilities.

## Candidate and applicable evidence

The reviewed manifest is
`Saved/CombatAI01/CAI-00/Worker/Candidate01/candidate-manifest.json`, SHA256
`dbfc41a5e5cf976b76263239430db5c3d3d2614a3089ea95db5761945ecec2ec`.
Its base commit is `288f44d3a313a9d6801c858ac74076d2cd6c7fd9`.
All **30 manifest entries** match the bytes used for this review: 12 delivered
source/document/tool files, the DLL, module descriptor and 16 evidence files.
The review identity result is saved at
`Saved/CombatAI01/CAI-00/Review/candidate-identity-check.json`.

The project DLL SHA256 is
`a70a3ffa6f0ba426c7958083ded4ea5a7ae434cc413ed38c2cb9b2c2449dbcb1`.
`build02.log` records a successful UE 5.8.3 Win64 Development Editor compile/link
in 8.41 seconds, including `EnemyCombatObservation.cpp` and the final native changes.
The passing earlier build is historical evidence, not the final build identity.

Reused executor evidence under `Worker/Candidate01/`:

- `self-check.json`: all 24 focused source/preservation/pure-check rows pass.
- `pure-test-build.log` and `pure-test.log`: the production value header compiles
  with MSVC C++20 `/W4 /WX`; seed, ring, value ownership and reset checks pass.
- `baseline-identity.json`: incoming MSQ-70 source and binary match its recorded
  candidate; no historical implementation or review evidence was replaced.
- `audio-inventory.json`: 160 enumerated `/Game` audio assets, comprising 134
  SoundWaves and 26 SoundCues. Named handoff cues are present.
- `editor-after.json` and `editor-load-check.json`: the executor records the
  retained lobby, no PIE, no dirty packages, and final DLL load in PID 41272.
  The earlier script-mode bootstrap exited; the handoff correctly identifies
  ordinary `editor-launch02.json` as the retained session. These are executor
  lifecycle observations, not an independent runtime behavior test.

## Technical criteria

| Criterion | Assessment and source basis |
| --- | --- |
| Bounded observability | PASS. `CombatAIObservation.h:61` owns a fixed 64-entry ring with 96-byte reason storage, chronological eviction and no dynamic record growth. Source state/shot logs become ring events. `EnemyCombatComponent.cpp:413` exports only on an explicit `trace` command; ordinary capture does not write files. Explicit exports may accumulate, as disclosed. |
| Knowledge and fairness separation | PASS. `EnemyCombatObservation.cpp:80` captures own feet/home and memory-gated sight samples without dereferencing the target or reading the player. The sight adapter retains the existing successful-visibility gate. Snapshot and trace entries contain values only. `PrivilegedFairnessTrace` is a separate, unwired type; it is not consumed by the legacy policy. |
| Honest legacy state and path reporting | PASS. JSON distinguishes current intent, physical authority, memory-derived alert and sight evidence. Labels expressly describe legacy finite memory. Navigation instrumentation reports bounded query/follow/failure/cancellation outcomes without changing navigation decisions or the walking command. |
| Stable seeds and capture reproducibility | PASS within the declared contract. `CombatAIObservation.h:16` derives the 31-bit stream seed from encounter seed and explicit placement slot. `PhysicsControlDummyWorld.cpp:39` assigns the slot before deferred spawning finishes; reset generation and actor identity are not seed inputs. Pure checks cover 1024 distinct test slots and identical full input records through 1000 ring pushes. Default slots 0/1/2 yield 930522253/1447358377/298751569. |
| Generation, reset and ammunition | PASS by source and pure ring checks. `CombatProjectileWorld.cpp:608` advances encounter generation before fixture reset. `EnemyCombatComponent.cpp:63` clears old intent, reinitializes the same configured agent seed and opens an empty ring with a fresh reset event. Ring admission rejects stale generations. The F6 binding and player rifle feedback path retain their existing ammunition behavior; no player ammunition assignment was added. Direct fixture reset remains within its existing encounter, as documented. |
| Authority, projectile and clock preservation | PASS by focused source comparison and call-site inspection. The fixture still supplies the sole GASP/Mover command bridge; physical/death authority suppresses combat before movement/fire. No alternate tick/controller, actor placement or damage writer was introduced. Existing launch gates, finite-flight projectile path and world/bullet/rifle 0.25 versus hero-movement 0.65 policy remain unchanged. |
| Baseline and audio evidence | PASS. The handoff separates source facts from the owner's uncaptured failure cause, records exact interfaces and current finite-search/walking limits, and does not imply hearing, running, group tactics or measured cost. Audio inventory establishes asset presence and the existing firing call only; playback/audibility and tactical voice coverage are correctly left unproven. |

The ring is a sampled diagnostic tail and value-capture contract. It does not
reconstruct every legacy decision: unsampled updates, animation/collision gates,
navigation frontier and historical per-event tuning are absent. The final handoff
states those limits and labels tuning as status-time data. Pure value equality
and seed stability therefore do not establish policy replay, deterministic Chaos,
or repeated in-engine encounters.

## Finding closure and remaining gates

No production defect requiring correction was found. During review, the initial
executor check `capture_no_player_or_target_dereference` reported failure because
its regex matched `Target.` in a source comment. Manual inspection confirmed no
target dereference in the capture adapter. The executor strips line comments
before that check; the final row passes and `self-check-initial.json` preserves
the earlier result. This was a check false positive, not evidence of a gameplay
knowledge leak.

Runtime F6 ring/generation/ammunition behavior, status/export in an actual game,
physical motion, owner-observed loss-of-contact causes, audio/readability and
performance remain pending under the owner-only gameplay reservation. No passing
source row substitutes for those observations. The handoff's short owner route
is appropriate. CAI-01 and later behavior packages remain undispatched by this
review.
