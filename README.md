
<p align="center">
  <img src="https://github.com/mpethamotaung/Daxter/frontend/public/logo.png" alt="Daxter Logo">
</p>

# Daxter Project: Accountant Aggregation and Insights Dashboard

Daxter (OpenTax Agent Data Ingestion and AI Dashboard) is a project simulating a full-stack application for accountants. 
It aggregates financial/tax compliance data from multiple agent sources, persists it in a PostgreSQL database, and provides
an interactive dashboard and an AI Assistant (powered by LangGraph/LLM) for natural language queries and insights.

## Tech Stack

| Component | Technology | Description |
| --- | --- | --- |
| Backend API | Python, FastAPI | High-performance, asynchronous API for data ingestion and serving. |
| Database | PostgreSQL | Relational data persistence, accesed via **SQLAlchemy**. |
| AI Layer | LangGraph, LLM API | Orchestrates multi-step AI workflows for RAG and natural language to SQL translation. |
| Frontend UI | Next.js, React.js, TypeScript | Unified dashboard interface built with **Material UI (MUI)**. |
| State Mgt. | Redux Toolkit | Manages application state and data flow on the frontend. |
| Orchestration | Docker Compose | Defines and runs the full multi-service environment (recommended setup). |

## Setup Instruction (Recommended: Docker Compose)
The fastest and most reliable way to get all three services ( **db**, **backend**, and **frontend**) running simultaneously
is using Docker Compose.

## Prerequisites

- **Git**

- **Docker Setup** (must be running)

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

## Local Setup (Alternative)
If you prefer to run the frontend and backend services directly on your host machine, follow these steps.

### Prerequisites
- **Git** 
- **Conda/Miniconda** (for Python environment) 
- **Node.js** (LTS version, frontend) 
- **PostgreSQL** (running locally, or use the Docker DB service, adjusting the URL) 

### Backend Setup (Python/FastAPI)
   
**Create and Activate Conda Environment:**
   
```
conda create -n daxter python=3.11
conda activate daxter
```
   
**Install Dependencies:**

```
cd backend
pip install -r requirements.txt
cd ..
```
**Set Environment Variables:**

Set the **DATABASE_URL** and **API-KEY** environment variables. If you are using Docker DB service (running on port 5433 - if you already have local PostgreSQL running on the default port 5432), use the following:

```
# Set the DB URL using the local IP/port
export DATABASE_URL="postgresql://daxter_user:daxter_password@localhost:5433/daxter_db"

# Set the AI Key
export API_KEY="YOUR_ACTUAL_API_KEY_HERE"
```

**Run Migrations (Alembic):**
   Run containerised DB once to create tables, or connect to local DB and ensure the account_data table exists.

**Start the Backend Server:**

```
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup (Next.js/React)

1. Navigate and Install Dependecies:

```
cd frontend
npm install
```

2. **Set Backend API URL:** The frontend expects the backend to be available at port 8000. This is configured manually internally in the Next.js setup, but you can override it with an environment variable if needed.
   
3. **Start the Frontend Server**:

```
npm run dev
```

The frontend will now be running at **http://localhost:3000**






















