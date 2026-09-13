"""Run one configured Painter MCP tool for diagnostics without calling a language model."""

import argparse
import asyncio
import json
from pathlib import Path
import sys
import tomllib

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


ROOT = Path(__file__).resolve().parents[1]


async def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool", help="Configured tool name, or 'schema' to list enabled tool schemas")
    parser.add_argument("--arguments", type=Path, help="UTF-8 JSON file containing tool arguments")
    parser.add_argument("--quiet", action="store_true", help="Print the report path instead of a large tool response")
    options = parser.parse_args()
    with (ROOT / ".codex/config.toml").open("rb") as handle:
        config = tomllib.load(handle)["mcp_servers"]["substance_painter"]
    if options.tool != "schema" and options.tool not in config["enabled_tools"]:
        parser.error("Tool is not in the project configuration's enabled_tools list")
    params = StdioServerParameters(command=config["command"], args=config["args"], env=config["env"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            if options.tool == "schema":
                catalog = await session.list_tools()
                result = {"tools": [tool.model_dump(mode="json", exclude_none=True)
                                    for tool in catalog.tools if tool.name in config["enabled_tools"]]}
            else:
                arguments = json.loads(options.arguments.read_text(encoding="utf-8-sig")) if options.arguments else {}
                response = await session.call_tool(options.tool, arguments=arguments)
                result = response.model_dump(mode="json", exclude_none=True)
    report = ROOT / "Saved/AgentSetup/PainterProbe" / f"{options.tool}.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if options.tool == "schema":
        print(json.dumps({"tools": [tool["name"] for tool in result["tools"]], "report": str(report)}))
    else:
        print(json.dumps({"report": str(report), "isError": result.get("isError", False)} if options.quiet else result, ensure_ascii=False))
        if result.get("isError"):
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run())
