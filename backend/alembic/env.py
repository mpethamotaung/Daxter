# backend/migrations/env.py

import os
import sys
import asyncio
from logging.config import fileConfig
from dotenv import load_dotenv



from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

#--- Load environment variables from .env file ---
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# --- Add app to Python path ---
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

# --- Import app modules ---
from app.database import Base
from app import models  # ensure models are imported for autogenerate

# ---
# Alembic configuration setup
# ---
config = context.config

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---
# Get Database URL
# ---
def get_database_url() -> str:
    """Fetch the database URL and ensure async dialect is used.
       CRITICAL FIX: Temporarily replaces 'db' with 'localhost' for host-based Alembic execution.
    """
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        # Local fallback, using localhost:5433 as in your original file
        database_url = "postgresql+asyncpg://daxter_user:daxter_password@localhost:5433/daxter_db"
    
    # Ensure async driver prefix
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

    # CRITICAL FIX for ConnectionRefusedError:
    # If running Alembic on the host machine, replace the Docker hostname 'db'
    # with 'localhost' and enforce the mapped port 5433 (based on your fallback).
    if '@db:' in database_url:
        # Example: '...user:pass@db:5432/...' becomes '...user:pass@localhost:5433/...'
        database_url = database_url.replace('@db:', '@localhost:5433')
        
    return database_url

# Metadata for 'autogenerate' support
target_metadata = Base.metadata

# ---
# Offline migrations
# ---
def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# ---
# Online (async) migrations
# ---
async def run_migrations_online():
    """Run migrations in 'online' mode."""
    async_engine = create_async_engine(get_database_url(), poolclass=pool.NullPool)

    async with async_engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await async_engine.dispose()

def do_run_migrations(connection):
    """Execute migrations in online mode."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

# ---
# Entry point
# ---
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())