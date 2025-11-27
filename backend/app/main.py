import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from typing import AsyncGenerator
import logging

#Imports for SQLAlchemy models and Pydantic schemas
from sqlalchemy import select, func, text
from .models import AccountantData
from .schemas import AccountantDataCreate, AccountantDataResponse, DashboardSummary

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Database Configuration ---
# Read the DATABASE_URL from environment variables (set in docker-compose.yml)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set.")
    

# Adjust URL for async support if needed (FastAPI standard practice)
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
    # Startup Events: Check DB connection
    logger.info("Starting up FastAPI application...")
    try:
        # A simple check to confirm the database is reachable
        async with engine.connect() as conn:
            # Execute a simple query
            await conn.execute(text("SELECT 1"))
        logger.info("Successfully connected to the PostgreSQL database.")
    except OperationalError as e:
        logger.error(f"Failed to connect to the database on startup: {e}")
        # In a real app, you might use exponential backoff/retry here
        pass
    except Exception as e:
        logger.error(f"An unexpected error occurred during DB connection check: {e}")
        pass
        
    yield
    
    # Shutdown Events: Close any necessary resources 
    logger.info("Shutting down FastAPI application.")


# --- FastAPI Application Initialization ---
app = FastAPI(
    title="Daxter API",
    version="0.1.0",
    description="Data Ingestion and AI Dashboard Backend.",
    lifespan=lifespan # Attach the startup/shutdown logic
)


# --- Database Session Dependency ---
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an active database session."""
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


# --- API Endpoints ---

@app.get("/", tags=["Status"])
async def root():
    return {"project": "Daxter", "status": "Running"}


@app.get("/api/health-check", tags=["Status"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Checks the server status and database connectivity.
    """
    try:
        # If the database session is successfully acquired, we can execute a simple query.
        # The 'get_db' dependency already handles basic acquisition, but this confirms execution.
        await db.execute(text("SELECT 1")) 
        return {"status": "OK", "database": "Connected"}
    except Exception as e:
        # If the query fails for any reason (e.g., connection lost), return a failure status.
        logger.error(f"Health check failed due to DB query error: {e}")
        raise HTTPException(status_code=503, detail="Database connection failed during query execution")
    
# Add the Data Ingestion Endpoint
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
    Recieves and stores new financial data from an external agent system.
    """
    # 1. Convert Pydantic model data to SQLAlchemy model object
    db_data = AccountantData(**data.model_dump())

    # 2. Add to sessions and commit
    db.add(db_data)
    await db.commit()
    await db.refresh(db_data) # Populate 'id' and 'data_ingested_at' fields

    # 3. Return the created object, convert back to a Pydantic response schema
    return db_data

# Add the Dashboard Summary Endpoint 
@app.get(
    "/api/summary",
    response_model=DashboardSummary,
    tags=["Dashboard"]
)
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """
    Returns key aggregated metrics for the dashboard view.
    """

    #Use SQLAlchemy functions for efficient database aggregation

    # 1. Total Clients (Distinct client_name count)
    total_clients_stmt = select(func.count(func.distinct(AccountantData.client_name)))
    total_clients = (await db.execute(total_clients_stmt)).scalar_one_or_none() or 0

    # 2. Financial Aggregation (Total Liability and Total Revenue)
    financial_agg_stmt = select(
        func.sum(AccountantData.tax_liability),
        func.sum(AccountantData.total_revenue)
    )
    results = (await db.execute(financial_agg_stmt)).one_or_none()
    total_tax_liability = results[0] if results and results[0] is not None else 0.0
    total_revenue = results[1] if results and results[1] is not None else 0.0

    # 3. Compliance Pending Count
    pending_count_stmt = select(func.count(AccountantData.id)).where(AccountantData.compliance_status == "Pending")
    pending_count = (await db.execute(pending_count_stmt)).scalar_one()

    # 4. Last Ingestion Time
    last_ingestion_stmt = select(func.max(AccountantData.data_ingested_at))
    last_ingestion = (await db.execute(last_ingestion_stmt)).scalar_one_or_none()

    # Construct and return the summary response
    return DashboardSummary(
        total_clients=total_clients,
        total_tax_liability_usd=total_tax_liability,
        total_revenue_usd=total_revenue,
        compliance_pending_count=pending_count,
        last_ingestion_time=last_ingestion
    )