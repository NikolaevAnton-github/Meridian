"""Register the trial operations for an explicitly launched editor session."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import metahuman_trial01_tools
import metahuman_trial01_unreal
metahuman_trial01_unreal.action('inspect')
