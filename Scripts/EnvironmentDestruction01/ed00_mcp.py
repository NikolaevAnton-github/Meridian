"""Bounded Epic MCP capture using the established project's local MCP protocol."""
import argparse
import base64
import json
from pathlib import Path
from urllib.request import ProxyHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Saved/EnvironmentDestruction01/ED-00/MSQ-140-Candidate01"
APP = "EditorToolset.EditorAppToolset"
VIEWS = {
    "entry": {"location": {"x": -500, "y": 0, "z": 172.15}, "rotation": {"pitch": -10, "yaw": 180, "roll": 0}, "scale": {"x": 1, "y": 1, "z": 1}},
    "hall": {"location": {"x": 1900, "y": 0, "z": 172.15}, "rotation": {"pitch": 0, "yaw": 180, "roll": 0}, "scale": {"x": 1, "y": 1, "z": 1}},
}


class Client:
    def __init__(self):
        self.opener = build_opener(ProxyHandler({}))
        self.headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        self.next_id = 0
        self.rpc("initialize", {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "MSQ140Evidence", "version": "1.0"}})
        self.rpc("notifications/initialized", notification=True)

    def rpc(self, method, params=None, notification=False):
        payload = {"jsonrpc": "2.0", "method": method}
        if not notification:
            self.next_id += 1
            payload["id"] = self.next_id
        if params is not None:
            payload["params"] = params
        request = Request("http://127.0.0.1:8000/mcp", data=json.dumps(payload).encode(), headers=self.headers, method="POST")
        with self.opener.open(request, timeout=55) as response:
            raw = response.read()
            if method == "initialize":
                self.headers["Mcp-Session-Id"] = response.headers["Mcp-Session-Id"]
            if notification:
                return None
        message = json.loads(raw)
        if "error" in message:
            raise RuntimeError(message["error"])
        result = message["result"]
        if result.get("isError"):
            raise RuntimeError(result)
        return result

    def call(self, toolset, name, arguments=None):
        result = self.rpc("tools/call", {"name": "call_tool", "arguments": {"toolset_name": toolset, "tool_name": name, "arguments": arguments or {}}})
        payload = json.loads(result["content"][0]["text"])
        return payload.get("returnValue", payload)

    def capture(self, state, view, capture_id="epic"):
        assert state in ("source", "lab") and view in VIEWS
        assert capture_id in ("epic", "gameview")
        path = OUT / f"{state}-{view}-{capture_id}.png"
        assert not path.exists(), path
        expected = "/Game/Maps/L_OpeningLobby_" + ("PainterStone01" if state == "source" else "DestructionLab01")
        assert self.call("editor_toolset.toolsets.scene.SceneTools", "get_current_level") == expected
        assert self.call(APP, "IsPIERunning") is False
        record = self.call(APP, "CaptureViewport", {"captureTransform": VIEWS[view], "bShowUI": False, "annotations": {"gridSpacing": 0, "gridExtent": 0, "gridHeight": 0, "maxLabelDistance": 0, "classFilter": {"refPath": "/Script/Engine.Actor"}, "maxLabels": 0}})
        bitmap = record.pop("image")
        path.write_bytes(base64.b64decode(bitmap["data"]))
        record.update(map=expected, requested=VIEWS[view], scope="Native editor still; not gameplay movement evidence")
        path.with_suffix(".json").write_text(json.dumps(record, indent=2), encoding="utf-8")
        return {"image": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "camera": record["cameraLocation"], "fov": record["cameraFOV"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("state", choices=["source", "lab"])
    parser.add_argument("view", choices=VIEWS)
    parser.add_argument("--capture-id", choices=["epic", "gameview"], default="epic")
    args = parser.parse_args()
    print(json.dumps(Client().capture(args.state, args.view, args.capture_id)))
