"""
main.py

Programmatic entry point — runs the agent without the ADK CLI.
Uses Runner + InMemorySessionService, mirrors what `adk run` does internally.
"""

import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from agent import root_agent

APP_NAME   = "news_briefing_app"
USER_ID    = "u1"
SESSION_ID = "s1"


async def query(topic: str) -> str:
    session_svc = InMemorySessionService()
    await session_svc.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_svc)

    msg = genai_types.Content(role="user", parts=[genai_types.Part(text=f"News about: {topic}")])

    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=msg):
        if event.is_final_response():
            return event.content.parts[0].text if event.content and event.content.parts else ""

    return ""


async def main():
    print("News Briefing Agent  |  Ctrl+C to exit\n")
    while True:
        try:
            topic = input("Topic: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not topic or topic.lower() in ("exit", "quit"):
            break
        print("\nFetching...\n")
        print(await query(topic))
        print()


if __name__ == "__main__":
    asyncio.run(main())
