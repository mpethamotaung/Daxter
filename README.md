# Daxter Project: Accountant Aggregation and Insights Dashboard
Daxter (OpenTax Agent Data Ingestion and AI Dashboard) is a project simulating a full-stack application for accountants. 
It aggregates financial/tax compliance data from multiple agent sources, persists it in a PostgreSQL database, and provides
an interactive dashboard and an AI Assistant (powered by LangGraph/LLM) for natural langugage queries and insights.

##Tech Stack
| Component | Technology | Description |
| --- | --- | --- |
| Backend API | Python, FastAPI | High-performance, asynchronous API for data ingestion and serving. |
| Database | PostgreSQL | Relational data persistence, accesed via **SQLAlchemy**. |
| AI Layer | LangGraph, LLM API | Orchestrates multi-step AI workflows for RAG and natural language to SQL translation. |
| Frontend UI | Next.js, React.js, TypeScript | Unified dashboard interface built with **Material UI (MUI)**. |
| State Mgt. | Redux Toolkit | Manages application state and data flow on the frontend. |
| Orchestration | Docker Compose | Defines and runs the full multi-service environment (recommended setup). |

##Setup Instruction (Recommended: Docker Compose)
The fastest and most reliable way to get all three services ( **db**, **backend**, and **frontend**) running simultaneously
is using Docker Compose.

###Prerequisites
**Git**
**Docker Setup** (must be running)

1. **Clone the Repository & Configure**
  '''
  #Clone the repository
  git clone https://github.com/mpethamotaung/Daxter
  cd daxter

  #Create the environment configuration file
  touch .env 
  '''
3.   sdfd 
