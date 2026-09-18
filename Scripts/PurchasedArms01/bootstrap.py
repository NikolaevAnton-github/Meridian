"""Register bounded MSQ-61 tools only for an explicitly launched editor."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'OpeningLobby'))
import purchased_arms_tools
