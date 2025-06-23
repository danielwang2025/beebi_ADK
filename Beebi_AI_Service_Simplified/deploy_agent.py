import vertexai
from vertexai import agent_engines
from agent import root_agent  # your sleep analysis agent

vertexai.init(
    project="88281213939",
    location="us-central1",
    staging_bucket="gs://beebi-adk-us-central1",
)

remote_app = agent_engines.create(
    agent_engine=root_agent,
    requirements=[
            "pandas",
            "numpy",
            "pymssql",
            "google-cloud-aiplatform[adk,agent_engines]"
        ],
        extra_packages=["./beebi"]
    
)

print("\n✅ Agent deployed successfully!")
print(f"🔗 Agent resource_name: {remote_app.resource_name}")
