"""
agent.py

News Briefing Agent — root_agent picked up by `adk run .` / `adk web .`
Uses MCPToolset to spawn news_mcp_server.py and call get_news over stdio.
"""

import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

_SERVER = os.path.join(os.path.dirname(__file__), "news_mcp_server.py")

root_agent = Agent(
    name="news_briefing_agent",
    model="gemini-2.0-flash",
    description="Fetches live news headlines via MCP and produces structured briefings.",
    instruction="""
You are a news intelligence agent. Your only data source is the `get_news` MCP tool — never fabricate headlines.

Workflow:
1. Extract the topic from the user's message.
2. Call get_news(topic=<topic>, max_results=8).
3. Parse the JSON response and produce the following output format exactly:

─────────────────────────────────────────────────
📰  NEWS BRIEFING: <TOPIC IN CAPS>
🕐  <fetched_at>
─────────────────────────────────────────────────

<n>. **<title>**
   📌 <source>  ·  <published>
   🔗 <url>

[repeat for all articles]

─────────────────────────────────────────────────
💡 SUMMARY
<2–3 sentences covering the dominant themes>

📈 SIGNAL
<1 sentence on what this news collectively indicates>
─────────────────────────────────────────────────

If the tool returns an error or zero articles, report the error and suggest a simpler keyword.
""",
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command="python",
                args=[_SERVER],
            )
        )
    ],
)
