from google.adk.agents import Agent 

from beebi.analysis.sleep.sleep import root_agent as sleep_agent
from beebi.analysis.diaper.diaper import root_agent as diaper_agent
from beebi.analysis.feed.feed import root_agent as feed_agent
from beebi.analysis.report.agent import root_agent as report_agent

root_agent = Agent(
    name="baby_care_manager",
    model="gemini-2.5-pro",
    description="A manager agent for baby care analytics.",
    instruction="""
You are a manager agent responsible for coordinating baby care analytics.

Your primary role is to interpret the user's question and **delegate it to the most appropriate specialized agent** from the list below:

---

**🛌 Use `sleep_agent`** for questions about sleep, such as:
- Total sleep duration (duration output in **hours**)
- Number and duration of naps (duration output in **hours**)
- Nighttime wake-ups (duration output in **hours**)
- Sleep rhythm or irregularities (duration output in **hours**)
- Sleep trends over time (duration output in **hours**)

**🧷 Use `diaper_agent`** for questions about diaper activity, including:
- Frequency of diaper changes (output in **times**)
- Type of output (urine, stool, mixed)
- Timing and distribution of diaper changes
- Gaps or intervals between changes
- Abnormalities or concerns (e.g., too few changes)

**🍼 Use `feed_agent`** for questions about feeding behavior:
- Milk volume (output in **milliliters**)
- Feeding frequency, timing, and patterns
- Day vs night feeding behavior
- Daily intake summaries

**📊 Use `report_agent`** when the question involves:
- Multiple domains (e.g., sleep + feeding + diaper)
- Overall wellness summaries
- Cross-topic trends and comparisons
- General performance or health check

---

💬 If the question is vague (e.g., “How is the baby doing lately?”), politely ask the user to clarify which aspect they’re interested in — **sleep, feed, diaper, or all combined** — before proceeding.

🔁 Regardless of which agent is used, always return a **clear and parent-friendly explanation**, with values properly labeled:
- Sleep in **hours**
- Diaper in **times**
- Feeding in **milliliters (ml)**

🎯 Your tone should be **calm, kind, and supportive** — like a helpful assistant to new parents navigating early childcare.

""",
    sub_agents=[

        sleep_agent,
        diaper_agent,
        feed_agent,
        report_agent
    ],
)

from vertexai.preview import reasoning_engines

app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

import asyncio

async def main():
    # 1. Create session
    session = app.create_session(user_id="u_123")
    print("Created Session:")
    print(session)

    # 2. List sessions
    sessions = app.list_sessions(user_id="u_123")
    print("\nList of Sessions:")
    print(sessions)

    # 3. Get specific session
    retrieved = app.get_session(user_id="u_123", session_id=session.id)
    print("\nRetrieved Session:")
    print(retrieved)

    # 4. Send message using stream_query
    final_reply = ""
    print("\n\U0001F4AC Querying agent...")

    for event in app.stream_query(
        user_id="u_123",
        session_id=session.id,
        message="how is the sleep in the past 3 days"
    ):
        content = event.get("content", {})
        parts = content.get("parts", [])

        for part in parts:
            if "function_call" in part:
                continue  # Skip function call logs
            elif "function_response" in part:
                continue  # Skip function response logs
            elif "text" in part:
                final_reply += part["text"]
                print("\U0001F4DD Text:", part["text"])

    print("\n✅ Final reply:")
    print(final_reply or "⚠️ No final text response received.")

if __name__ == "__main__":
    asyncio.run(main())

