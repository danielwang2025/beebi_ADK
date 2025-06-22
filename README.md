# About the Project
We envisioned an intelligent companion for new parents—one that transforms scattered baby care logs into meaningful, real-time insights. With Beebi, we aim to relieve the cognitive load of early parenting by replacing static charts with conversational, AI-powered summaries. This vision redefines baby tracking as not just data collection, but a proactive, supportive experience that empowers parents to understand and respond to their baby's needs with clarity and confidence.

## Architecture Diagram
![微信图片_20250622210550](https://github.com/user-attachments/assets/1a546599-9c0c-48fa-816a-875117a50b80)


## Technology Stack

### Database Layer
[![Azure SQL](https://img.shields.io/badge/Microsoft%20Azure%20SQL-0089D6?style=for-the-badge&logo=microsoft-azure&logoColor=white)](https://azure.microsoft.com/en-us/products/azure-sql/)
- Azure SQL Server
- Azure SQL Database
- Stores structured baby care event data

### AI Agent Layer
[![Google Gemini](https://img.shields.io/badge/Gemini-4285F4?style=for-the-badge&logo=googleai&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)](https://google.github.io/adk-docs/)
[![Cloud Google Run](https://img.shields.io/badge/Google%20Cloud%20Run-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
- Gemini LLM with Google AI SDK for generating personalized insights
- Google ADK for building and orchestrating multi-agent AI architecture
- SubAgents:
  - Sleep Monitoring
  - Feeding Analysis
  - Diaper Change Tracking
  - Health Reporting
- Root Agent hosted on Cloud Run (deployment in process)
- Genetic insight summaries

### Mobile App Layer
[![Android](https://img.shields.io/badge/Android-3DDC84?style=for-the-badge&logo=android&logoColor=white)](https://developer.android.com/)
[![Kotlin](https://img.shields.io/badge/Kotlin-7F52FF?style=for-the-badge&logo=kotlin&logoColor=white)](https://kotlinlang.org/)
[![Java](https://img.shields.io/badge/Java-007396?style=for-the-badge&logo=openjdk&logoColor=white)](https://www.java.com/)
- Native Android Application (Java/Kotlin)
- User input processing
- Response visualization

### Backend Layer
[![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)](https://nodejs.org/)
[![Express](https://img.shields.io/badge/Express-000000?style=for-the-badge&logo=express&logoColor=white)](https://expressjs.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
- Node.js + Express for the backend server
- FastAPI to connect frontend with backend and AI services
- Parameter transformation
- Tool function routing

### Deployment
[![Cloud Run](https://img.shields.io/badge/Google%20Cloud%20Run-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
- Google Cloud Run for deploying the AI agent system

## Data Flow
1. **User Input**: Android app captures user requests
2. **Middleware**: Cloud Run endpoint processes requests
3. **AI Processing**:
   - Root Agent orchestrates subagents
   - Gemini LLM generates insights
4. **Data Persistence**:
   - Azure SQL stores interaction data
   - Azure SQL transmit basic data to AI agnet layer
6. **Response Delivery**: Processed results returned to mobile app

## Key Features
- Google ADK Multi-agent AI architecture with 4 specialized subagents
- Context-aware parameter transformation
- User data integration via Azure SQL
- Google Cloud Run deployment

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
python -m venv venv
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
