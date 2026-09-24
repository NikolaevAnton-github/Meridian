# Direct GASPALS AI audit tools

See [the audit report](../../../Docs/GASPALSAIAudit01.md).
These tools are diagnostic and are not registered at normal project startup.

## Offline analysis

From the repository root:

```powershell
& 'D:/UE_5.8/Engine/Binaries/ThirdParty/Python3/Win64/python.exe' 'Scripts/CombatAI01/GASPALSAudit01/analyze.py'
```

The default input is `Saved/GASPALSAIAudit01`. Use `--evidence` for a copied capture
directory and `--output` to create a new summary file. Existing outputs are refused.
Angles outside visible, aimed combat are diagnostic values, not launch attempts.
The log cutoff is specific to this recorded audit session.

## Editor capture

The toolset wraps existing native telemetry through the official Epic registry.
In the confirmed MeridianSquad editor's Python context, import:

```python
import sys
sys.path.insert(0, 'D:/devgames/MeridianSquad')
from Scripts.CombatAI01.GASPALSAudit01 import tools
```

Then discover `Game.Scripts.CombatAI01.GASPALSAudit01.tools.GASPALSAIAuditTools`
through the existing Epic MCP registry. No new service is required. The attempted
Python remote bootstrap found no remote node in this session; its source is saved
as evidence, not installed as a project startup path.

| Operation | Argument | Effect |
| --- | --- | --- |
| `snapshot` | Unique label | Reads full state into a new JSON file. |
| `sample` | JSON `[label, seconds]` | Samples existing native telemetry at approximately 10 Hz of world time; writes on completion. |
| `sight` / `visible_positions` | Empty | Reads geometry with diagnostic traces; candidate positions are specific to the retained lobby. |
| `place_player` | JSON `[x,y,z]` | Teleports the transient PIE player. |
| `manual_move` | JSON `[x,y,walk,duration]` | Disables the first fixture's combat and sends movement; stops movement after the world-time duration. **Combat remains disabled until explicitly resumed.** |
| `resume_combat` | Empty | Enables fixture combat in the PIE world. |
| `throttle` | `true` or `false` | Changes the transient editor background-throttle setting; returns its previous value. Restore that value after capture. |

Use one writer and one PIE world. Wait for a sample or manual command callback to
complete before stopping PIE; callbacks are not a general scenario runner.
Snapshots require unique filenames. Restore any changed editor setting, resume
combat when continuing the same PIE experiment, stop diagnostic PIE at completion,
and check for dirty packages. The audit sampled the retained rifle's local
`(0,62,9)` fallback muzzle; update that capture if a later rifle adds a Muzzle socket.
