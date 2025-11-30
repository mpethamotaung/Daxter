# backend/app/main.py

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from typing import AsyncGenerator, Dict, Any, List
import logging

# Imports for SQLAlchemy models and Pydantic schemas
from sqlalchemy import select, func, text
from .models import AccountantData, DataSummary # Import DataSummary
# Import all required schemas
from .schemas import AccountantDataCreate, AccountantDataResponse, DashboardSummary, SummaryRequest, SummaryResponse
# Import the new asynchronous agent logic module
from . import async_agents 

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Database Configuration (ASYNC) ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set.")

# Adjust URL for async support (postgresql+asyncpg://)
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create the asynchronous engine
engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)

# Create an async session maker
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# --- Lifespan Context Manager (Startup/Shutdown) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI application...")
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Successfully connected to the PostgreSQL database.")
    except OperationalError as e:
        logger.error(f"Failed to connect to the database on startup: {e}")
        pass
    except Exception as e:
        logger.error(f"An unexpected error occurred during DB connection check: {e}")
        pass

    yield

    logger.info("Shutting down FastAPI application.")


# --- FastAPI Application Initialization ---
app = FastAPI(
    title="Daxter API",
    version="0.1.0",
    description="Data Ingestion and AI Dashboard Backend.",
    lifespan=lifespan 
)


# --- Database Session Dependency ---
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session = AsyncSessionLocal()
    try:
        yield session
    except SQLAlchemyError as e:
        logger.error(f"Database error during session processing: {e}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed")
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_db: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        await session.close()


# ---
# API ENDPOINTS (STATUS & INGESTION)
# ---

@app.get("/", tags=["Status"])
async def root():
    return {"project": "Daxter", "status": "Running"}

@app.get("/api/health-check", tags=["Status"])
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1")) 
        return {"status": "OK", "database": "Connected"}
    except Exception as e:
        logger.error(f"Health check failed due to DB query error: {e}")
        raise HTTPException(status_code=503, detail="Database connection failed during query execution")

@app.post(
    "/api/data-ingest",
    response_model=AccountantDataResponse,
    status_code=201,
    tags=["Data Ingestion"]
)
async def ingest_agent_data(
    data: AccountantDataCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Receives and stores new financial data, then triggers the AI analysis workflow.
    (Simulates the Airflow/Data pull step)
    """
    # 1. Persist the raw data to the database
    db_data = AccountantData(**data.model_dump())
    db.add(db_data)
    await db.commit()
    await db.refresh(db_data) 

    # 2. Trigger AI-First Agent Workflow (for Observability)
    # We intentionally don't await the full analysis here, but just the trigger function
    workflow_id = await async_agents.trigger_ai_analysis_workflow(db_data.id)

    # Update the data record with the workflow ID for observability
    db_data.workflow_id = workflow_id
    await db.commit()

    return db_data

# ---
# CORE WORKFLOW: AI INTERACTION (NEW)
# ---

@app.post(
    "/api/ai-summary", 
    response_model=SummaryResponse, 
    tags=["Agent Systems"]
)
async def generate_ai_summary_for_agent(
    request: SummaryRequest, 
    db: AsyncSession = Depends(get_db)
):
    """
    Triggers an AI agent (LangGraph simulation) to analyze recent data and generate a summary or alert.
    """
    # Simulates the multi-agent orchestration and LLM integration
    summary_text = await async_agents.generate_and_save_summary(request, db)

    return SummaryResponse(
        agent_id=request.agent_id, 
        summary_type=request.summary_type,
        summary_text=summary_text
)

# ---
# CORE WORKFLOW: DETAILED AGENT QUERY (NEW)
# ---

@app.get(
    "/api/agent-data/{agent_id}", 
    response_model=Dict[str, Any], 
    tags=["Dashboard"]
)
async def get_agent_dashboard_data(agent_id: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieves recent raw data and related AI summaries for a single client/agent.
    Provides the data for the user-friendly dashboard with observability.
    """

    # 1. Retrieve recent raw data (Observability)
    raw_data_stmt = select(AccountantData).where(AccountantData.agent_id == agent_id).order_by(AccountantData.data_ingested_at.desc()).limit(5)
    raw_data_results = (await db.execute(raw_data_stmt)).scalars().all()

    # 2. Retrieve related AI summaries (Summary/Query capabilities)
    summaries_stmt = select(DataSummary).where(DataSummary.agent_id == agent_id).order_by(DataSummary.created_at.desc()).limit(5)
    summaries_results = (await db.execute(summaries_stmt)).scalars().all()

    if not raw_data_results and not summaries_results:
        raise HTTPException(status_code=404, detail=f"No data or summaries found for Agent ID: {agent_id}")

    return {
        "agent_id": agent_id,
        "latest_raw_data_previews": [AccountantDataResponse.model_validate(d).model_dump() for d in raw_data_results],
        "ai_summaries": [
            {"summary_type": s.summary_type, "text": s.summary_text, "created_at": s.created_at.isoformat(), "workflow_id": s.workflow_id} 
            for s in summaries_results
        ]
 }

# ---
# DASHBOARD AGGREGATION (Your Existing Endpoint)
# ---

@app.get(
    "/api/summary",
    response_model=DashboardSummary,
    tags=["Dashboard"]
)
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """
    Returns key aggregated metrics for the high-level dashboard view.
    """
    # ... (Your existing aggregation logic remains here)
    total_clients_stmt = select(func.count(func.distinct(AccountantData.client_name)))
    total_clients = (await db.execute(total_clients_stmt)).scalar_one_or_none() or 0

    financial_agg_stmt = select(
        func.sum(AccountantData.tax_liability),
        func.sum(AccountantData.total_revenue)
    )
    results = (await db.execute(financial_agg_stmt)).one_or_none()
    total_tax_liability = results[0] if results and results[0] is not None else 0.0
    total_revenue = results[1] if results and results[1] is not None else 0.0

    pending_count_stmt = select(func.count(AccountantData.id)).where(AccountantData.compliance_status == "Pending")
    pending_count = (await db.execute(pending_count_stmt)).scalar_one()

    last_ingestion_stmt = select(func.max(AccountantData.data_ingested_at))
    last_ingestion = (await db.execute(last_ingestion_stmt)).scalar_one_or_none()

    return DashboardSummary(
        total_clients=total_clients,
        total_tax_liability_usd=total_tax_liability,
        total_revenue_usd=total_revenue,
        compliance_pending_count=pending_count,
        last_ingestion_time=last_ingestion
    )