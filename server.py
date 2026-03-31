"""
server.py

FastAPI HTTP server that wraps the ADK agent for Cloud Run deployment.
Cloud Run needs an HTTP server — this exposes a /query endpoint.
"""

import os
import asyncio
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
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id="user",
        session_id="session",
    )

    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

    msg = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=f"News about: {topic}")]
    )

    async for event in runner.run_async(
        user_id="user",
        session_id="session",
        new_message=msg,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                return event.content.parts[0].text

    return "No response generated."


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
      <head>
        <title>News Briefing Agent</title>
        <style>
          body { font-family: sans-serif; max-width: 600px; margin: 60px auto; padding: 0 20px; }
          input { width: 100%; padding: 10px; font-size: 16px; margin: 10px 0; box-sizing: border-box; }
          button { padding: 10px 24px; font-size: 16px; cursor: pointer; }
          pre { background: #f4f4f4; padding: 16px; white-space: pre-wrap; border-radius: 6px; }
        </style>
      </head>
      <body>
        <h2>📰 News Briefing Agent</h2>
        <input id="topic" placeholder="Enter a topic (e.g. artificial intelligence)" />
        <button onclick="fetchNews()">Get Briefing</button>
        <pre id="result">Your briefing will appear here...</pre>
        <script>
          async function fetchNews() {
            const topic = document.getElementById('topic').value;
            document.getElementById('result').textContent = 'Fetching...';
            const res = await fetch('/query', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ topic })
            });
            const data = await res.json();
            document.getElementById('result').textContent = data.result;
          }
        </script>
      </body>
    </html>
    """


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
