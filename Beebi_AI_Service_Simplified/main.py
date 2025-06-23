from fastapi import FastAPI
from pydantic import BaseModel
import vertexai
from vertexai import agent_engines

# Vertex AI setup
vertexai.init(
    project="88281213939",
    location="us-central1",
    staging_bucket="gs://beebi-adk-us-central1"
)

remote_app = agent_engines.get(
    resource_name="projects/88281213939/locations/us-central1/reasoningEngines/7045714491253719040"
)

# FastAPI app
app = FastAPI()

class ChatInput(BaseModel):
    user_id: str
    message: str

@app.post("/chat")
def chat(input: ChatInput):
    session = remote_app.create_session(user_id=input.user_id)

    # Get the session back (optional)
    session = remote_app.get_session(user_id="u_456", session_id=session["id"])
    # Step 2: Stream the query and collect response text
    full_reply = ""
    for event in remote_app.stream_query(
        user_id=input.user_id,
        session_id=session["id"],
        message=input.message
    ):
        parts = event.get("content", {}).get("parts", [])
        for part in parts:
            if "text" in part:
                full_reply += part["text"]

    # Step 3: Return reply
    return {"reply": full_reply.strip()}