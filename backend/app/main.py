import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from typing import AsyncGenerator
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Database Configuration ---
# Read the DATABASE_URL from environment variables (set in docker-compose.yml)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable is not set.")
    # Fallback/development URL for running outside of Docker (optional)
    # exit(1) 

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
            await conn.execute("SELECT 1")
        logger.info("Successfully connected to the PostgreSQL database.")
    except OperationalError as e:
        logger.error(f"Failed to connect to the database on startup: {e}")
        # In a real app, you might use exponential backoff/retry here
        pass
    except Exception as e:
        logger.error(f"An unexpected error occurred during DB connection check: {e}")
        pass
        
    yield
    
    # Shutdown Events: Close any necessary resources (none required for this simple demo)
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
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except SQLAlchemyError as e:
        logger.error(f"Database error during session processing: {e}")
        raise HTTPException(status_code=500, detail="Database operation failed")
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_db: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


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
        await db.execute("SELECT 1") 
        return {"status": "OK", "database": "Connected"}
    except Exception as e:
        # If the query fails for any reason (e.g., connection lost), return a failure status.
        logger.error(f"Health check failed due to DB query error: {e}")
        raise HTTPException(status_code=503, detail="Database connection failed during query execution")

# Additional endpoints (e.g., /api/summary, /api/ai-assistant) will be added here later.