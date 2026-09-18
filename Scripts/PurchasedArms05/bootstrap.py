"""Register focused MSQ-65 adapters on the project's official Epic MCP server."""
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
for folder in ['OpeningLobby', 'PurchasedArms02', 'PurchasedArms05']:
    sys.path.insert(0, str(SCRIPTS / folder))
import tools05
