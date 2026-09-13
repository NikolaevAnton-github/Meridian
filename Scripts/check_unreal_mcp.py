"""Read-only connection check for the project's Epic MCP; Python standard library only."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, ProxyHandler


ENDPOINT = "http://127.0.0.1:8000/mcp"
OUTPUT = Path(__file__).resolve().parents[1] / "Saved/AgentSetup/McpProbe"


def check():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    # Local editor traffic must not go through a machine's HTTP proxy.
    opener = build_opener(ProxyHandler({}))
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    next_id = 0

    def rpc(method, params=None, report_name=None, notification=False):
        nonlocal next_id
        payload = {"jsonrpc": "2.0", "method": method}
        if not notification:
            next_id += 1
            payload["id"] = next_id
        if params is not None:
            payload["params"] = params
        request = Request(ENDPOINT, data=json.dumps(payload).encode(), headers=headers, method="POST")
        with opener.open(request, timeout=30) as response:
            raw = response.read()
            if method == "initialize":
                session = response.headers.get("Mcp-Session-Id")
                if not session:
                    raise RuntimeError("Initialize returned no MCP session ID")
                headers["Mcp-Session-Id"] = session
            if notification:
                if response.status != 202:
                    raise RuntimeError(f"Notification returned HTTP {response.status}, expected 202")
                return None
        message = json.loads(raw)
        if message.get("id") != payload["id"]:
            raise RuntimeError("JSON-RPC response ID does not match the request")
        if "error" in message:
            raise RuntimeError(f"{method}: {message['error']}")
        result = message["result"]
        if result.get("isError"):
            raise RuntimeError(f"Tool failed: {result.get('content')}")
        if report_name:
            (OUTPUT / report_name).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        return result

    def meta_tool(name, arguments, report_name):
        return rpc("tools/call", {"name": name, "arguments": arguments}, report_name)

    def read_value(toolset, tool, report_name):
        result = meta_tool("call_tool", {"toolset_name": toolset, "tool_name": tool, "arguments": {}}, report_name)
        blocks = [block["text"] for block in result["content"] if block["type"] == "text"]
        return json.loads(blocks[0])["returnValue"]

    try:
        initialized = rpc("initialize", {
            "protocolVersion": "2025-11-25", "capabilities": {},
            "clientInfo": {"name": "MeridianSquadProbe", "version": "1.0"},
        }, "checked-initialize.json")
        headers["Mcp-Protocol-Version"] = initialized["protocolVersion"]
        rpc("notifications/initialized", notification=True)
        tools = rpc("tools/list", {}, "checked-tools.json")
        names = {tool["name"] for tool in tools["tools"]}
        if not {"list_toolsets", "describe_toolset", "call_tool"}.issubset(names):
            raise RuntimeError("Expected Epic discovery tools are missing; check bEnableToolSearch")
        meta_tool("list_toolsets", {}, "checked-toolsets.json")
        editor = "EditorToolset.EditorAppToolset"
        scene = "editor_toolset.toolsets.scene.SceneTools"
        for toolset, required_tool, file_name in (
            (editor, "IsPIERunning", "checked-editor-schema.json"),
            (scene, "get_current_level", "checked-scene-schema.json"),
        ):
            description = meta_tool("describe_toolset", {"toolset_name": toolset}, file_name)
            schema = json.loads(description["content"][0]["text"])
            if not any(tool["name"] == f"{toolset}.{required_tool}" for tool in schema["tools"]):
                raise RuntimeError(f"Required read tool is missing: {toolset}.{required_tool}")
        pie = read_value(editor, "IsPIERunning", "checked-pie.json")
        level = read_value(scene, "get_current_level", "checked-level.json")
        if not isinstance(pie, bool) or not isinstance(level, str):
            raise RuntimeError("Editor state has unexpected value types")
        summary = {
            "checked_at_utc": datetime.now(timezone.utc).isoformat(),
            "endpoint": ENDPOINT, "protocol": initialized["protocolVersion"],
            "passed": True, "meta_tools": sorted(names),
            "pie_running": pie, "current_level": level,
            "scope": "HTTP connection and read-only editor queries; not native Codex tool registration",
        }
        (OUTPUT / "latest.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    finally:
        if "Mcp-Session-Id" in headers:
            try:
                with opener.open(Request(ENDPOINT, headers=headers, method="DELETE"), timeout=5):
                    pass
            except (HTTPError, URLError, TimeoutError):
                pass


if __name__ == "__main__":
    try:
        check()
    except (HTTPError, URLError, TimeoutError, RuntimeError, ValueError, KeyError, IndexError) as error:
        print(f"Epic MCP check failed: {error}", file=sys.stderr)
        sys.exit(1)
