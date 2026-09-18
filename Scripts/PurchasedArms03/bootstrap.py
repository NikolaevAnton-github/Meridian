"""Register the bounded MSQ-63 operations on the existing Epic MCP server."""
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
for folder in ['OpeningLobby', 'PurchasedArms02', 'PurchasedArms03']:
    sys.path.insert(0, str(SCRIPTS / folder))
import tools03
