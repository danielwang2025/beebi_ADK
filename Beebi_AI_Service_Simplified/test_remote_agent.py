import vertexai
from vertexai import agent_engines
import json

# Init Vertex AI with your project and bucket
vertexai.init(
    project="88281213939",
    location="us-central1",
    staging_bucket="gs://beebi-adk-us-central1"
)

# Connect to your deployed agent using its resource name
remote_app = agent_engines.get(resource_name="projects/88281213939/locations/us-central1/reasoningEngines/7045714491253719040")

# Create session
remote_session = remote_app.create_session(user_id="u_456")

# Get the session back (optional)
session = remote_app.get_session(user_id="u_456", session_id=remote_session["id"])

# Collect reply text only
final_response = ""
for event in remote_app.stream_query(
    user_id="u_456",
    session_id=remote_session["id"],
    message="analyze sleep for last 7 days"
):
    parts = event.get("content", {}).get("parts", [])
    for part in parts:
        if "text" in part:
            final_response += part["text"]

# Print final response in JSON format
print(json.dumps({"reply": final_response.strip()}))