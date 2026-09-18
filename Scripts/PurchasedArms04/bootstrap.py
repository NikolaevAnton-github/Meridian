"""Register MSQ-64 checks on the existing official Epic MCP server."""
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
for folder in ['OpeningLobby', 'PurchasedArms02', 'PurchasedArms04']:
    sys.path.insert(0, str(SCRIPTS / folder))
import tools04
