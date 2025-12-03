
<p align="center">
  <img src="https://github.com/mpethamotaung/Daxter/blob/main/frontend/public/logo.png" alt="Daxter Logo">
</p>

# Daxter Project: Accountant Aggregation and Insights Dashboard

A proof-of-concept for OpenTax, simulating real-time financial and tax data aggregation with AI insights and observability in a lightweight, local setup.

## Setup Instruction 

### Backend (FastAPI + SQLAlchemy)

1. **Clone the Repository & Configure**

#Clone the repository
git clone https://github.com/mpethamotaung/Daxter

On terminal, navigate to location where you cloned the project
```
cd daxter
cd backend
```
2. **Create Virtual Environment**

Create virtual environment with Conda/Miniconda (Recommended)
```
conda create --name daxter

conda activate daxter
```
3. **Install dependencies**

From Daxter/backend run:
```
pip install -r requirements.txt
```

4. **Run the backend server (uses file-based SQLite daxter.db)**

```
uvicorn main:app --reload --port 8000
```

5. **Verify API Endpoints**

http://localhost:8000/docs


### Frontend (Next.js + React Query + Tailwind)
while backend terminal is running, open another terminal

1. **Navigate to frontend directory**

```
cd frontend
```

2. **Install dependencies**

```
npm install
```

3. **Start development server(proxies /api to backend)**

```
npm run dev
```

4. **View the dashboard**

http://localhost:3000

**Access Points**

| Service | Address | Purpose |
| --- | --- | --- |
| Frontend | http://localhost:3000 | The main dashboard application. |
| Backend API | http://localhost:8000 | FastAPI endpoints (e.g., /api/summary). |


## Features

- Summary metrics(total payments, unpaid invoices).
- Pagninated/filterable table for payments and invoices
- Monthly payments bar chart (interactive).
- AI assistant for data queries (mock responses).
- Observability logs panel (auto-refreshes).
- All data stored in in-memory SQLite, seeded on startup

## Deliverables

- A README.md 
- A SOLUTION.md 
- A git repository 
- Loom video walkthrough




















