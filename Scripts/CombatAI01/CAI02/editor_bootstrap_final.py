"""Final native reload; separate output paths preserve the first load evidence."""
import sys
sys.path.insert(0,'D:/devgames/MeridianSquad')
from Scripts.CombatAI01.CAI02 import editor_tools
editor_tools.OUT = editor_tools.OUT / 'FinalReload'
