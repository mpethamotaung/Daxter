import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context

# --- Project-Specific Imports ---
# 1. Import the Base class and our models file
from app.database import Base 
from app import models 
# --------------------------------

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python's standard logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata for autogenerate support
# This tells Alembic which models to compare against the database.
target_metadata = Base.metadata

# --- Custom Function to get the DB URL ---
def get_database_url():
    """Retrieves the database URL from environment variables."""
    # Use the same logic as main.py to get the URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # Fallback for local testing outside of Docker if needed
        # Update with your local connection string if not using Docker
        return "postgresql+asyncpg://daxter_user:daxter_password@localhost:5433/daxter_db" 
    
    # Adjust URL for async support (change postgresql to postgresql+asyncpg)
    return database_url.replace("postgresql://", "postgresql+asyncpg://")

# --- Async Functionality for Alembic ---
def run_migrations_offline() -> None:
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

def do_run_migrations(connection) -> None:
    """Core function to run migrations against a live database connection."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            url=get_database_url(),
            poolclass=pool.NullPool,
        )
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())