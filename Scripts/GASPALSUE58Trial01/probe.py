"""Focused GASPALS trial checks through the existing official Epic MCP client."""

import base64
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Scripts/OpeningLobby"))
from functionalbuild01_client import call

OUTPUT = ROOT / "Saved/Experiments/GASPALSUE58Trial01"
OUTPUT.mkdir(parents=True, exist_ok=True)
EDITOR = "EditorToolset.EditorAppToolset"
SCENE = "editor_toolset.toolsets.scene.SceneTools"


def invoke(toolset, name, arguments=None):
    result = call("call_tool", {
        "toolset_name": toolset, "tool_name": name, "arguments": arguments or {}
    })
    return json.loads(result["content"][0]["text"])["returnValue"]


def save(name, result):
    (OUTPUT / f"{name}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))


action = sys.argv[1]
if action == "state":
    save("state", {
        "level": invoke(SCENE, "get_current_level"),
        "pie_running": invoke(EDITOR, "IsPIERunning"),
    })
elif action == "play":
    level = invoke(SCENE, "get_current_level")
    assert level.startswith("/GASPALS/Levels/DefaultLevel"), level
    assert not invoke(EDITOR, "IsPIERunning"), "A Play session is already running"
    invoke(EDITOR, "StartPIE", {"options": {
        "bSimulate": False, "playMode": "PlayMode_InViewPort", "warmupSeconds": 3
    }})
    save("play", {"level": level, "pie_running": invoke(EDITOR, "IsPIERunning")})
elif action == "stop":
    # SceneTools reports an empty level while the possessed PIE viewport has focus.
    # Confirm the endpoint's editor process identity before using this action.
    assert invoke(EDITOR, "IsPIERunning"), "No Play session is running"
    invoke(EDITOR, "StopPIE")
    save("stop", {"pie_running": invoke(EDITOR, "IsPIERunning")})
elif action == "capture":
    label = sys.argv[2]
    assert label.replace("_", "").replace("-", "").isalnum()
    result = call("call_tool", {
        "toolset_name": EDITOR,
        "tool_name": "CaptureViewport" if len(sys.argv) > 3 else "CaptureEditorImage",
        "arguments": {"captureTransform": None, "annotations": None, "bShowUI": False}
        if len(sys.argv) > 3 else {}
    })
    images = []
    for block in result["content"]:
        if block["type"] == "image":
            images.append(block["data"])
        elif block["type"] == "text":
            try:
                value = json.loads(block["text"])["returnValue"]
                if isinstance(value, dict) and "image" in value:
                    value = value["image"]
                if isinstance(value, dict) and value.get("data"):
                    images.append(value["data"])
            except (KeyError, ValueError, TypeError):
                pass
    assert images, "No image was returned"
    for index, data in enumerate(images):
        destination = OUTPUT / f"{label}-{index}.png"
        destination.write_bytes(base64.b64decode(data))
        print(destination)
else:
    raise ValueError(action)
