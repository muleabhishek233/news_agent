# News Briefing Agent
**Google Gen AI Intensive — APAC Edition, Cohort 1, Track 2**

An AI agent built with **Google ADK** that connects to an external data source via **MCP (Model Context Protocol)**, retrieves live news headlines, and generates a structured briefing.

---

## Architecture

```
User Input
    │
    ▼
┌─────────────────────────────────┐
│         ADK Runner              │
│  ┌──────────────────────────┐   │
│  │   news_briefing_agent    │   │  ← agent.py (root_agent)
│  │   model: gemini-2.0-flash│   │
│  └────────────┬─────────────┘   │
│               │ MCP (stdio)     │
│  ┌────────────▼─────────────┐   │
│  │    news_mcp_server.py    │   │  ← MCP Server (subprocess)
│  │    tool: get_news()      │   │
│  └────────────┬─────────────┘   │
└───────────────┼─────────────────┘
                │ HTTP
                ▼
       Google News RSS Feed
       (news.google.com/rss)
```

**Data flow:**
1. Agent receives a topic from the user
2. Agent calls `get_news` via MCPToolset (spawns `news_mcp_server.py` as a subprocess over stdio)
3. MCP server hits Google News RSS, parses XML, returns structured JSON
4. Agent uses the JSON payload to compose the final briefing

---

## Project Structure

```
news_agent/
├── agent.py              # root_agent — ADK agent with MCPToolset
├── news_mcp_server.py    # MCP server exposing get_news tool
├── main.py               # Programmatic runner (alternative to adk CLI)
├── requirements.txt
└── .env                  # GOOGLE_API_KEY goes here
```

---

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your Gemini API key to .env
echo "GOOGLE_API_KEY=your_key_here" > .env
```

Get a free API key at: https://aistudio.google.com/app/apikey

---

## Running

**Option A — ADK Web UI** (recommended for demos)
```bash
adk web .
# Opens at http://localhost:8000
```

**Option B — ADK CLI**
```bash
adk run .
```

**Option C — Direct Python**
```bash
python main.py
```

---

## MCP Tool Reference

| Tool | Input | Output |
|------|-------|--------|
| `get_news` | `topic: str`, `max_results: int (default 8)` | JSON with `topic`, `fetched_at`, `count`, `articles[]` |

Each article contains: `title`, `source`, `published`, `url`

---

## Sample Output

```
─────────────────────────────────────────────────
📰  NEWS BRIEFING: ARTIFICIAL INTELLIGENCE
🕐  2025-06-10 08:42 UTC
─────────────────────────────────────────────────

1. **OpenAI announces GPT-5 with reasoning improvements**
   📌 The Verge  ·  Tue, 10 Jun 2025 07:15:00 GMT
   🔗 https://...

2. **Google DeepMind publishes new protein folding research**
   📌 Nature  ·  Tue, 10 Jun 2025 06:00:00 GMT
   🔗 https://...

...

─────────────────────────────────────────────────
💡 SUMMARY
Coverage is dominated by model capability announcements and enterprise
adoption stories, with growing focus on AI regulation in the EU.

📈 SIGNAL
The industry is shifting from foundational model competition toward
application-layer differentiation and governance frameworks.
─────────────────────────────────────────────────
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Agent Framework | Google ADK |
| LLM | Gemini 2.0 Flash |
| Tool Protocol | MCP (stdio transport) |
| Data Source | Google News RSS |
| Language | Python 3.10+ |
