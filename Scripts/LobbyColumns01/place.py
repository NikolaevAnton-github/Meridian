"""Replace the sixteen architectural columns and their floor finishes only."""
import json
from pathlib import Path
import unreal as u

ROOT=Path('D:/devgames/MeridianSquad')
OUT=ROOT/'Saved/LobbyColumns01'
DEST='/Game/OpeningLobby/LobbyColumns01/'
editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assert not editor.get_game_world()
assert not u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
assert not u.EditorLoadingAndSavingUtils.get_dirty_content_packages()
assert (ROOT/'Content/Maps/L_OpeningLobby_PainterStone01.umap').read_bytes()==(OUT/'LobbyBefore.umap').read_bytes()
source=json.loads((OUT/'source.json').read_text())
by_label={a.get_actor_label():a for a in actors.get_all_level_actors()}
data=u.load_asset(DEST+'DA_LobbyColumn01')
upper=u.load_asset(DEST+'SM_ColumnUpper01')
placed=[]
with u.ScopedEditorTransaction('LobbyColumns01: copy accepted column structure'):
    for row in source['columns']:
        old=by_label[row['label']]
        x,y,_=row['location']
        new=u.NGDTools.spawn_prop(editor.get_editor_world(),data,u.Vector(x,y,0),u.Rotator(),row['label'])
        assert new and new.actor_has_tag('LobbyColumns01')
        new.set_folder_path('OpeningLobby/LobbyColumns01')
        if row['height']==1800:
            mesh=old.static_mesh_component
            mesh.set_static_mesh(upper)
            for i in range(upper.get_num_sections(0)):
                mesh.set_material(i,upper.get_material(i))
            old.set_actor_location(u.Vector(x,y,0),False,True)
            old.set_actor_scale3d(u.Vector(1,1,1))
            old.set_actor_label(row['label']+'_Upper')
        else:
            assert row['height']==840
            assert actors.destroy_actor(old)
        placed.append(dict(label=row['label'],path=new.get_path_name(),height=row['height']))
    assert actors.destroy_actor(by_label['RC01_ReinforcedColumn'])
    for label,name in [('Floor','SM_FloorWithColumnSeats01'),('FloorStrip_-1','SM_FloorStrip_N01'),('FloorStrip_1','SM_FloorStrip_P01')]:
        a=by_label[label]
        mesh=u.load_asset(DEST+name)
        a.static_mesh_component.set_static_mesh(mesh)
        for i in range(4):
            material=mesh.get_material(i)
            if material: a.static_mesh_component.set_material(i,material)
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(OUT/'placed.json').write_text(json.dumps(placed,indent=2))
print(json.dumps(dict(replaced_columns=len(placed),static_upper_sections=4,floor_actors=3)))
