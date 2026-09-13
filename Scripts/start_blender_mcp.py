"""Enable the installed Blender MCP addon for this GUI session, without saving startup preferences."""

import importlib
import json
import os

os.environ["DISABLE_TELEMETRY"] = "true"

import addon_utils
import bpy


if bpy.app.background:
    raise RuntimeError("Blender MCP requires a GUI session")

addon_name = "blender_mcp"
if addon_utils.check(addon_name)[1]:
    addon = importlib.import_module(addon_name)
else:
    addon = addon_utils.enable(addon_name, default_set=True, persistent=True)
    if addon is None:
        raise RuntimeError("Could not enable the installed Blender MCP addon")

preferences = bpy.context.preferences.addons.get(addon_name)
if preferences is None:
    raise RuntimeError("Blender MCP preferences are unavailable")
preferences.preferences.telemetry_consent = False
addon.sync_edit_capture_handlers()

existing_server = getattr(bpy.types, "blendermcp_server", None)
if existing_server is not None:
    existing_server.stop()

scene = bpy.context.scene
scene.blendermcp_auto_start_server = False
scene.blendermcp_port = 9876
for flag in (
    "blendermcp_use_polyhaven", "blendermcp_use_hyper3d", "blendermcp_use_hunyuan3d",
    "blendermcp_use_sketchfab", "blendermcp_use_polypizza",
):
    setattr(scene, flag, False)

server = addon.BlenderMCPServer(host="127.0.0.1", port=9876)
bpy.types.blendermcp_server = server
server.start()
scene.blendermcp_server_running = server.running
if not server.running:
    raise RuntimeError("Blender MCP listener failed to start")
if server.get_telemetry_consent() != {"consent": False}:
    raise RuntimeError("Blender MCP telemetry consent did not remain disabled")

print(json.dumps({
    "blender_version": bpy.app.version_string,
    "addon_protocol": addon.ADDON_PROTOCOL_VERSION,
    "listener": "127.0.0.1:9876",
    "telemetry_consent": False,
    "scene_objects": len(scene.objects),
}))
