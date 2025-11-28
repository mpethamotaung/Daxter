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
       Prioritizes environment variable and minimally adjusts based on Docker context.
    """
    database_url = os.getenv("DATABASE_URL")
    
    
    if not database_url:
        # Fallback if env var is not set
        print("No DATABASE_URL in env, using fallback.")
        database_url = "postgresql+asyncpg://daxter_user:daxter_password@localhost:5432/daxter_db"
    
    # Ensure async driver prefix
    if database_url.startswith("postgresql://") and "+asyncpg" not in database_url:
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    
    # If running in Docker, ensure 'db:5432'; else use local settings
    if os.getenv("DOCKER_ENV") or 'docker' in os.getenv('HOSTNAME', '').lower():
        print("Detected Docker environment.")
        # Force 'db:5432' if not already set correctly
        if '@localhost' in database_url:
            database_url = database_url.replace('@localhost', '@db')
        if ':5433' in database_url:
            database_url = database_url.replace(':5433', ':5432')
        elif ':5432' not in database_url and '@db:' in database_url:
            # Ensure port is explicitly 5432
            parts = database_url.split('/')
            host_part = parts[0].rsplit(':', 1)[0] if ':' in parts[0] else parts[0]
            database_url = f"{host_part}:5432/{parts[1]}" if len(parts) > 1 else f"{host_part}:5432/db"
    else:
        print("Detected local environment.")
        # Local machine: force 'localhost:5432'
        if '@db' in database_url:
            database_url = database_url.replace('@db', '@localhost')
        if ':5432' not in database_url and '@localhost' in database_url:
            parts = database_url.split('/')
            host_part = parts[0].rsplit(':', 1)[0] if ':' in parts[0] else parts[0]
            database_url = f"{host_part}:5432/{parts[1]}" if len(parts) > 1 else f"{host_part}:5432/db"
    
    print(f"Final DATABASE_URL used: {database_url}")  # Debug log to see final URL
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