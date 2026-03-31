"""
server.py

FastAPI HTTP server that wraps the ADK agent for Cloud Run deployment.
Exposes GET / (UI) and POST /query (agent endpoint).
"""

import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from agent import root_agent

app = FastAPI(title="News Briefing Agent")
APP_NAME = "news_briefing_app"


async def run_agent(topic: str) -> str:
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME, user_id="user", session_id="session"
    )
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
    msg = genai_types.Content(
        role="user", parts=[genai_types.Part(text=f"News about: {topic}")]
    )
    async for event in runner.run_async(
        user_id="user", session_id="session", new_message=msg
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                return event.content.parts[0].text
    return "No response generated."


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>News Briefing Agent</title>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg:        #0c0c0c;
      --surface:   #141414;
      --border:    #282828;
      --accent:    #e2b96f;
      --accent-dk: #9e7a3a;
      --text:      #ede9e0;
      --muted:     #5a5a5a;
      --dim:       #888;
    }

    html, body {
      background: var(--bg);
      color: var(--text);
      font-family: 'DM Sans', sans-serif;
      font-weight: 300;
      min-height: 100vh;
    }

    .page {
      max-width: 720px;
      margin: 0 auto;
      padding: 56px 24px 80px;
    }

    .eyebrow {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 20px;
    }

    .eyebrow-dot {
      width: 6px; height: 6px;
      border-radius: 50%;
      background: var(--accent);
    }

    .eyebrow span {
      font-size: 11px;
      font-weight: 500;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      color: var(--accent);
    }

    h1 {
      font-family: 'Playfair Display', serif;
      font-size: clamp(40px, 7vw, 64px);
      font-weight: 900;
      line-height: 1.0;
      color: var(--text);
      margin-bottom: 16px;
    }

    h1 em { font-style: italic; color: var(--accent); }

    .subtitle {
      font-size: 15px;
      line-height: 1.7;
      color: var(--dim);
      max-width: 460px;
      margin-bottom: 44px;
    }

    .rule {
      border: none;
      border-top: 1px solid var(--border);
      margin-bottom: 40px;
    }

    .field-label {
      font-size: 11px;
      font-weight: 500;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 10px;
    }

    .search-row {
      display: flex;
      gap: 10px;
      margin-bottom: 40px;
    }

    input[type="text"] {
      flex: 1;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 5px;
      padding: 13px 16px;
      font-family: 'DM Sans', sans-serif;
      font-size: 14.5px;
      font-weight: 300;
      color: var(--text);
      outline: none;
      transition: border-color 0.2s;
    }

    input::placeholder { color: var(--muted); }
    input:focus { border-color: var(--accent); }

    button {
      background: var(--accent);
      color: #0c0c0c;
      border: none;
      border-radius: 5px;
      padding: 13px 26px;
      font-family: 'DM Sans', sans-serif;
      font-size: 13.5px;
      font-weight: 500;
      letter-spacing: 0.04em;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: background 0.15s;
      white-space: nowrap;
    }

    button:hover    { background: #edca85; }
    button:disabled { background: var(--accent-dk); cursor: not-allowed; opacity: 0.7; }

    .spin {
      display: none;
      width: 14px; height: 14px;
      border: 2px solid rgba(0,0,0,0.25);
      border-top-color: #0c0c0c;
      border-radius: 50%;
      animation: rot 0.65s linear infinite;
    }
    @keyframes rot { to { transform: rotate(360deg); } }

    .result-label {
      font-size: 11px;
      font-weight: 500;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .status-dot {
      width: 6px; height: 6px;
      border-radius: 50%;
      background: var(--border);
      transition: background 0.3s;
    }

    .status-dot.live { background: #4caf7d; }

    #result {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 28px 30px;
      font-family: 'DM Sans', sans-serif;
      font-size: 14px;
      line-height: 1.9;
      color: var(--text);
      white-space: pre-wrap;
      word-break: break-word;
      min-height: 140px;
      transition: border-color 0.25s;
    }

    #result.idle    { color: var(--muted); font-style: italic; }
    #result.loading { border-color: var(--accent-dk); color: var(--dim); }
    #result.done    { border-color: var(--border); }

    footer {
      margin-top: 56px;
      padding-top: 24px;
      border-top: 1px solid var(--border);
      font-size: 11.5px;
      color: var(--muted);
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 8px;
    }
  </style>
</head>
<body>
<div class="page">

  <div class="eyebrow">
    <div class="eyebrow-dot"></div>
    <span>Google ADK &nbsp;·&nbsp; MCP &nbsp;·&nbsp; Gemini 2.5 Flash</span>
  </div>

  <h1>News<br><em>Briefing</em> Agent</h1>

  <p class="subtitle">
    Enter any topic. The agent fetches live headlines via Google News RSS
    through an MCP tool, then generates a structured briefing.
  </p>

  <hr class="rule"/>

  <p class="field-label">Topic</p>
  <div class="search-row">
    <input type="text" id="topic" placeholder="e.g. artificial intelligence, ISRO, climate change…"/>
    <button id="btn" onclick="fetchNews()">
      <div class="spin" id="spinner"></div>
      <span id="btn-text">Fetch Briefing</span>
    </button>
  </div>

  <div class="result-label">
    <div class="status-dot" id="dot"></div>
    Briefing Output
  </div>
  <pre id="result" class="idle">Awaiting topic…</pre>

  <footer>
    <span>Google Gen AI Intensive · APAC Edition · Cohort 1 · Track 2</span>
    <span>Powered by Google ADK + MCP</span>
  </footer>

</div>
<script>
  const input   = document.getElementById('topic');
  const result  = document.getElementById('result');
  const btn     = document.getElementById('btn');
  const spinner = document.getElementById('spinner');
  const btnText = document.getElementById('btn-text');
  const dot     = document.getElementById('dot');

  input.addEventListener('keydown', e => { if (e.key === 'Enter') fetchNews(); });

  async function fetchNews() {
    const topic = input.value.trim();
    if (!topic) { input.focus(); return; }

    btn.disabled = true;
    spinner.style.display = 'block';
    btnText.textContent = 'Fetching…';
    result.textContent = 'Contacting news sources and generating briefing…';
    result.className = 'loading';
    dot.className = 'status-dot';

    try {
      const res  = await fetch('/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      });
      const data = await res.json();
      result.textContent = data.result || data.error || 'No response received.';
      result.className = 'done';
      dot.className = 'status-dot live';
    } catch (err) {
      result.textContent = 'Network error — make sure the server is running.';
      result.className = '';
    } finally {
      btn.disabled = false;
      spinner.style.display = 'none';
      btnText.textContent = 'Fetch Briefing';
    }
  }
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML


@app.post("/query")
async def query(request: Request):
    body = await request.json()
    topic = body.get("topic", "").strip()
    if not topic:
        return JSONResponse({"error": "topic is required"}, status_code=400)
    result = await run_agent(topic)
    return {"topic": topic, "result": result}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
