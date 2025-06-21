# About the Project
We envisioned an intelligent companion for new parents—one that transforms scattered baby care logs into meaningful, real-time insights. With Beebi, we aim to relieve the cognitive load of early parenting by replacing static charts with conversational, AI-powered summaries. This vision redefines baby tracking as not just data collection, but a proactive, supportive experience that empowers parents to understand and respond to their baby's needs with clarity and confidence.

## Architecture Diagram
![image](https://github.com/user-attachments/assets/e8dcf3f8-3cbe-4ae6-b00f-ab3c55af6fb7)

## Technology Stack

#### Database Layer
[![Azure SQL](https://img.shields.io/badge/Microsoft%20Azure%20SQL-0089D6?style=for-the-badge&logo=microsoft-azure&logoColor=white)](https://azure.microsoft.com/en-us/products/azure-sql/)
- Azure SQL Server
- Azure SQL Database

#### AI Agent Layer
[![Google Gemini](https://img.shields.io/badge/Gemini-4285F4?style=for-the-badge&logo=googleai&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Google Vertex AI](https://img.shields.io/badge/Vertex%20AI-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)](https://cloud.google.com/vertex-ai)
[![Cloud Run](https://img.shields.io/badge/Google%20Cloud%20Run-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
- Gemini LLM with Google AI SDK
- SubAgents:
  - Sleep Monitoring
  - Feeding Analysis
  - Diaper Change Tracking
  - Health Reporting
- Root Agent hosted on Cloud Run
- Genetic insight summaries

#### Mobile App Layer
[![Android](https://img.shields.io/badge/Android-3DDC84?style=for-the-badge&logo=android&logoColor=white)](https://developer.android.com/)
- Native Android Application
- User input processing
- Response visualization

#### Middleware
[![Cloud Run](https://img.shields.io/badge/Google%20Cloud%20Run-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
- AI Agent Endpoint
- Parameter transformation
- Tool function routing

## Data Flow
1. **User Input**: Android app captures user requests
2. **Data Transmission**: Azure SQL stores and transmits user basic data to AI Agent
3. **Middleware**: Cloud Run endpoint processes requests with user context
4. **AI Processing**:
   - Root Agent orchestrates specialized subagents
   - Gemini LLM generates personalized insights
5. **Response Delivery**: Processed results returned to mobile app

## Key Features
- Multi-agent AI architecture with 4 specialized subagents
- Context-aware parameter transformation
- User data integration via Azure SQL
- Cloud-native deployment
- Genetic algorithm-powered insights

## Deployment
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)](https://cloud.google.com)
[![Azure](https://img.shields.io/badge/Microsoft%20Azure-0078D4?style=for-the-badge&logo=microsoft-azure&logoColor=white)](https://azure.microsoft.com)


# Getting Started Backend
## Installation
1. Clone the repo
```bash
git clone https://github.com/danielwang2025/beebi_ADK 
```
2. Setup Environment
```bash
# Create virtual environment in the root directory
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
```
## Install dependencies
```bash
pip install -r requirements.txt
```
## Run the project
```bash
adk web
```

## Contact

Daniel(Zhichong) Wang - [Github](https://github.com/danielwang2025)  
Tim Shi - [Github](https://github.com/TIMXSHI)  

Project Link: 


# Acknowledgments
This project is submitted to [![Devpost][devpost]][devpost-url] as part of a hackathon project for the Agent Development Kit Hackathon with Google Cloud.

[devpost]: https://img.shields.io/badge/Devpost-003E54?style=for-the-badge&logo=Devpost&logoColor=white
[devpost-url]: https://googlecloudmultiagents.devpost.com/?ref_feature=challenge&ref_medium=discover&_gl=1*yi86ui*_gcl_au*MTE3ODA4Njc5Ni4xNzUwNDcwNzUz*_ga*MzY4MDAwNTk4LjE3NTA0NzA3NTM.*_ga_0YHJK3Y10M*czE3NTA0NzA3NTIkbzEkZzEkdDE3NTA0NzI0MDgkajQ5JGwwJGgw
