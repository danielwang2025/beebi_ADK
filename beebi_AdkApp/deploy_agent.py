import vertexai
from vertexai import agent_engines
from agent import root_agent  # your sleep analysis agent

vertexai.init(
    project="your-project-ID",
    location="us-central1",
    staging_bucket="gs://your-project",
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
