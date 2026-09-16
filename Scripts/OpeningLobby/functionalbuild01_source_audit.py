"""Read-only native/FBX audit through the existing ReworkA01 validator."""
import sys
from pathlib import Path
ROOT=Path('D:/devgames/MeridianSquad')
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'Scripts/OpeningLobby'))
source=(ROOT/'Scripts/OpeningLobby/reworka01_source_audit.py').read_text()
source=source.replace('from reworka01_data import','from functionalbuild01_data import')
source=source.replace('LobbyArchitectureReworkA01.blend','LobbyFunctionalBuild01.blend')
source=source.replace('SM_RA01_','SM_FB01_').replace('ReworkA01_ReadOnlySourceAudit','FunctionalBuild01_ReadOnlySourceAudit')
source=source.replace('==23','==17').replace('modules=23','modules=17')
namespace={};exec(compile(source,str(ROOT/'Scripts/OpeningLobby/reworka01_source_audit.py'),'exec'),namespace)
namespace['run']()
