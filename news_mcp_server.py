"""
news_mcp_server.py

MCP server that exposes a single tool: get_news(topic, max_results)
Data source: Google News RSS — no API key required.
Launched as a subprocess by ADK via StdioServerParameters.
"""

import json
import asyncio
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types


app = Server("news-mcp-server")

WMO_CLEAN_TITLE = lambda t: t.rsplit(" - ", 1)[0] if " - " in t else t


def _fetch_rss(topic: str, max_results: int) -> dict:
    q = urllib.parse.quote(topic)
    url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    with urllib.request.urlopen(req, timeout=10) as r:
        root = ET.fromstring(r.read().decode("utf-8"))

    articles = []
    for item in root.find("channel").findall("item")[:max_results]:
        src_el = item.find("source")
        articles.append({
            "title":     WMO_CLEAN_TITLE(item.findtext("title", "").strip()),
            "source":    src_el.text.strip() if src_el is not None else "Unknown",
            "published": item.findtext("pubDate", "").strip(),
            "url":       item.findtext("link", "").strip(),
        })

    return {
        "topic":      topic,
        "fetched_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "count":      len(articles),
        "articles":   articles,
    }


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_news",
            description="Fetch latest news headlines for a topic via Google News RSS.",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic":       {"type": "string",  "description": "Search keyword or phrase"},
                    "max_results": {"type": "integer", "description": "Number of articles (default 8, max 15)", "default": 8},
                },
                "required": ["topic"],
            },
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name != "get_news":
        raise ValueError(f"Unknown tool: {name}")

    topic       = arguments["topic"]
    max_results = min(int(arguments.get("max_results", 8)), 15)

    try:
        payload = _fetch_rss(topic, max_results)
    except Exception as e:
        payload = {"error": str(e), "topic": topic, "articles": []}

    return [types.TextContent(type="text", text=json.dumps(payload, indent=2))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
