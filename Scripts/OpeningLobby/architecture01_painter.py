"""Use the installed Painter bridge with only the explicitly assigned task roots.

The process-local environment replaces SmokeTest roots; no configuration is saved.
All operations still pass the existing bridge's planning, validation and path guards.
"""
import asyncio
import json
import sys
import tomllib
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/OpeningLobby/Stage2/Architecture01'
SRC=ROOT/'Assets/Source/OpeningLobby/Architecture01'

async def main():
    config=tomllib.loads((ROOT/'.codex/config.toml').read_text())['mcp_servers']['substance_painter']
    env=dict(config['env'])
    env.update(SP_MCP_PROJECT_ROOTS=str(SRC),SP_MCP_MESH_ROOTS=str(OUT/'FBX'),SP_MCP_EXPORT_ROOTS=str(OUT/'PainterTextures'))
    params=StdioServerParameters(command=config['command'],args=config['args'],env=env)
    async with stdio_client(params) as (read,write):
        async with ClientSession(read,write) as session:
            await session.initialize()
            async def call(name,args={}):
                assert name in config['enabled_tools']
                response=await session.call_tool(name,args)
                data=response.model_dump(mode='json',exclude_none=True)
                (OUT/('painter-'+name+'.json')).write_text(json.dumps(data,indent=2))
                print(json.dumps(data))
                assert not response.isError,name
                return data
            stage=sys.argv[1]
            if stage=='plan':
                await call('painter_status')
                await call('plan_project_creation',dict(mesh_file_path=str(OUT/'FBX/SM_A01_CheckpointPanel.fbx'),output_path=str(SRC/'CheckpointFinish.spp'),settings=dict(normal_map_format='DirectX',default_texture_resolution=1024)))
            elif stage=='create':
                assert not (SRC/'CheckpointFinish.spp').exists()
                await call('create_project',dict(mesh_file_path=str(OUT/'FBX/SM_A01_CheckpointPanel.fbx'),output_path=str(SRC/'CheckpointFinish.spp'),settings=dict(normal_map_format='DirectX',default_texture_resolution=1024),confirm=True))
            elif stage=='info':
                await call('get_project_info')
                await call('list_layers',dict(texture_set='M_A01_Checkpoint'))
            elif stage=='recipe':
                recipe=[dict(type='fill',name='Intact graphite enamel',base_color=[.19,.23,.21],channels=dict(Roughness=.34,Metallic=.25),active_channels=['BaseColor','Roughness','Metallic'])]
                (SRC/'CheckpointRecipe.json').write_text(json.dumps(dict(texture_set='M_A01_Checkpoint',recipe=recipe),indent=2))
                await call('plan_layer_recipe',dict(texture_set='M_A01_Checkpoint',recipe=recipe))
                await call('create_layer_recipe',dict(texture_set='M_A01_Checkpoint',recipe=recipe))
                await call('save_project',dict(confirm=True))
                await call('audit_project')
            elif stage=='export':
                await call('export_textures',dict(output_directory=str(OUT/'PainterTextures'),preset='Unreal Engine (Packed)',file_format='png',bit_depth='8',size_log2=10,texture_sets=['M_A01_Checkpoint']))
            else:raise ValueError(stage)

if __name__=='__main__': asyncio.run(main())
