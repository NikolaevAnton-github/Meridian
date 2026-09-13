# MeridianSquad agent instructions

- Communicate with the user in Russian. Write all project content in English,
  including documentation, code comments, names, commit messages and Multica
  task reports. Russian is reserved for the owner's direct chat with Codex.
- Budget: the user's existing $200/month Codex subscription only. Do not add paid
  API usage, paid cloud generation, extra credits or paid services. Local models
  are allowed, subject to available RAM/VRAM and project disk space.
- Project disk budget is at most 250 GB, including generated data, local version
  history and project-specific services. Avoid duplicated Unreal worktrees and
  unrestricted caches. Never delete user assets to reclaim space.
- Optimize for a verified result including rework. Use Astra for difficult work;
  select other models only when appropriate and available. Prefer standard speed;
  set reasoning effort to the task rather than routinely using the maximum.
- Delegate bounded independent tasks only. Keep context focused: locate files,
  read relevant sections, return concise findings and save full logs under Saved/.
- One writer per running Unreal/Blender/Substance instance. Coordinate the whole
  editing operation, not just individual MCP calls. Run one memory-heavy build,
  bake, render or local model workload at a time until measurements justify more.
- Prefer the official Epic MCP for Unreal editor operations. Its Codex entry is
  unreal_epic, address http://127.0.0.1:8000/mcp. Discover needed toolsets on demand.
  Confirm the project and editor state before mutations. Rider tools remain
  useful for code work and debugging; their connection is independent of Epic MCP.
- Check actual capabilities and installed versions before using a DCC bridge.
  Do not assume a working connection just because configuration exists.
- Define acceptance criteria, make a bounded change, and verify the result.
  Repeat failed actions only when new evidence warrants it. After two equivalent
  failed attempts, change the diagnostic approach. Avoid redundant passing tests.
- Source code, configuration, accepted decisions and asset source files belong
  in Git; binary assets use Git LFS. Generated data and large logs stay outside Git.
  Never put credentials in tracked files or tool output.
- The local Multica pilot passed one read-only task using Codex subscription
  authentication. Keep runtime concurrency at one and use the existing project
  directory. Do not build a competing task dispatcher or create a separate task
  database. Multica uses PostgreSQL; asset metadata is not implemented yet.
  See Docs/AgentDevelopment.md and Docs/MulticaPilot.md for the next acceptance gate.
