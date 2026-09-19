# KimodoLocal01: local text-to-motion installation

Prepared 2026-09-20. Multica issue: **MSQ-86**. The owner explicitly requested installation under
`D:/devgames` for subsequent experiments. See
[the owner instruction](../Approvals/KimodoLocal01-OwnerScope01.json).

## Scope and ownership

Use the existing Multica project and one MeridianSquad Code executor at
Astra/max/standard with fast mode disabled. Install the official NVIDIA Kimodo
locally under `D:/devgames/Kimodo`, with an isolated Python environment, bounded
model/cache directories and convenient start/stop instructions. This authorizes
dependency installation, model downloads within budget, local service startup
and one short technical generation smoke. It does not authorize Unreal plugin
installation, project/editor/gameplay changes, paid cloud services or production
animation acceptance. Do not stop or mutate owner-owned application sessions.

The controller handles administration and closure commits. Executor self-checks;
`/root/balance_options_research` owns one bounded independent review of any custom
launch/install changes and applicability of smoke evidence, without repeating
passing tests. Project content and internal reports must be English.

## Installation requirements

- Read ProjectState and this task. Preserve the pre-existing owner modifications
  to `Config/DefaultEngine.ini` and `MeridianSquad.uproject` and all other assets.
- Prefer the official repository `https://github.com/nv-tlabs/kimodo`, pin its
  source commit and record dependency/model revisions. Select the commercially
  usable SOMA-RP-v1.1 model; do not substitute restricted SMPL-X weights.
- The host is Windows with RTX 5090 32 GB, 32 GB RAM, NVIDIA driver 616.92.
  Docker/WSL are not currently installed; PATH Python is only the Store alias.
  A ComfyUI embedded Python exists but must not be modified. Prefer an isolated
  native Python route if supported. Use a CUDA PyTorch build with actual sm_120
  support; verify CUDA computation, not just package names. Do not reboot or
  change global security settings. A major host change is a controller decision.
- Start with at most 45 GB additional disk; count installation and caches toward
  the project's standing 250 GB budget even outside the repository. Measure
  existing project size and installed growth. Keep downloads/cache bounded and
  avoid duplicate model copies. Never delete owner data for space.
- Official installation requires authorized Hugging Face access to the gated
  `meta-llama/Meta-Llama-3-8B-Instruct` text encoder. The controller has asked the
  owner about access. No default HF token file/environment token was found.
  Proceed with all independent setup. Do not bypass gates, use unofficial
  weight mirrors, print/read credentials into logs, or request tokens in chat.
  If credentials/access are absent, prepare a local interactive login route and
  clearly distinguish installed tools from unverified text generation.
- Read upstream installation instructions and actual source before adapting.
  Preserve upstream bytes/history; any necessary Windows compatibility patch
  must be small, documented and captured reproducibly. After two equivalent
  failures, change the diagnostic approach. Keep full logs under Saved.
- Services bind loopback only, one model workload at a time. Never take all
  remaining system RAM; measure before inference and use conservative settings.
  Start background helpers hidden. Provide a convenient local launcher, an
  owned-process stop path and a short English README with URL and output path.
- Keep all installation/model/cache/output bytes under D:/devgames/Kimodo.
  Track reproducible bootstrap/launcher source copies under Scripts/Kimodo/
  if authored, and a concise handoff in Docs/KimodoLocal01.md. Do not commit
  Python environments, models, caches, logs, secrets or generated animations.

## Focused acceptance

### Controller preflight advisory

Upstream now has explicit Windows MotionCorrection build support. Prefer isolated
Python 3.10/3.11 and the existing MSVC toolchain; CMake >=3.15/C++17 required.
Preinstall PyTorch >=2.7 with CUDA >=12.8 for RTX 5090. Current upstream pins
transformers==5.1.0 and needs peft>=0.18 and gradio>=6.8.0. The upstream Dockerfile
uses an older 24.10 image and is not a ready-made Blackwell route. Approximate
weight downloads: SOMA-RP-v1.1 1.13 GB, gated Llama 16.06 GB, two LLM2Vec adapters
0.34 GB; avoid extra variants/training data. The controller measured the full
project at 73,039,458,929 bytes (73.04 GB / 68.02 GiB), including local history and
services. Do not repeat the passing full recursive scan. The 45 GB installation
cap fits within the standing 250 GB project budget.

1. Official pinned source, isolated dependencies, model/license identity and
   measured disk/RAM/VRAM are recorded; unrelated project and host settings are
   preserved.
2. Import/CLI checks and actual CUDA arithmetic pass. Local interactive UI starts
   and responds on loopback, or a concrete upstream blocker is documented with
   all independent setup finished.
3. One short text prompt generates a finite nonempty motion file if gated access
   is available. Otherwise mark generation pending owner authentication explicitly;
   startup/import checks do not establish text-to-motion readiness.
4. Owner can launch/stop and locate output using the supplied files; restarting
   does not download another full cache or silently start multiple model servers.

Evidence root: `Saved/AgentSetup/KimodoLocal01/Worker/`. Return concise installed
paths, exact versions, checks, auth needs and remaining limitations. Do not change
Multica status/profiles, commit, dispatch successors, or operate DCC applications.

## Installation outcome

The 2026-09-20 independent installation phase is complete and passed primary
review, with no open technical findings. See [the handoff](../KimodoLocal01.md).
The conditional acceptance path applies: approved Llama authentication is absent
and current free RAM is insufficient. Full UI, the actual model-server lifecycle
and first text-to-motion smoke remain explicitly unverified. Continue from the
existing installation after those conditions are resolved; do not reinstall or
repeat applicable passing dependency checks. No Unreal integration is authorized.
