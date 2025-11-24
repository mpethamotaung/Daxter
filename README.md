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
  ```
  #Clone the repository
  git clone https://github.com/mpethamotaung/Daxter
  cd daxter

  #Create the environment configuration file
  touch .env 
  ```
2. **Configure .env File**
Add the following variables to your newly created .env file. You can use the default database credentials for local testing.

```
# --- DATABASE CREDENTIALS (Used by docker-compose) ---
POSTGRES_USER=daxter_user
POSTGRES_PASSWORD=daxter_password
POSTGRES_DB=daxter_db

# --- AI API KEY (Required for AI features) ---
# Replace with your actual LLM API key (e.g., Gemini API key)
GEMINI_API_KEY=""
```

3. **Build and Run**
   Run the following command from the root **daxter** directory. The first run will build the images and install all dependencies inside the containers.
     
```
docker compose up --build
```
**Access Points**
| Service | Address | Purpose |
| --- | --- | --- |
| Frontend | http://localhost:3000 | The main dashboard application. |
| Backend API | http://localhost:8000 | FastAPI endpoints (e.g., /api/summary). |
| Health Check | http://localhost:8000/api/health-check | Verifies server and database connection. |
