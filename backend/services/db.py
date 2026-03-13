"""
CricketIQ Database Configuration.
Handles both sync and async database connections.

To run async models with SQLAlchemy, your DATABASE_URL should use the 'postgresql+asyncpg://' scheme.
To run sync migrations or scripts, use 'postgresql://' or 'postgresql+psycopg2://'
"""
import os
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

DATABASE_URL: str = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:postgres@localhost:5432/cricketiq"
)
DATABASE_URL_SYNC: str = os.getenv(
    "DATABASE_URL_SYNC", 
    "postgresql://postgres:postgres@localhost:5432/cricketiq"
)

# --- Async Setup (FastAPI) ---
async_engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=os.getenv("DEBUG", "false").lower() == "true",
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Dependency for getting an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# --- Sync Setup (Scripts/Migrations) ---
sync_engine = create_engine(
    DATABASE_URL_SYNC,
    pool_pre_ping=True,
    echo=False,
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False,
)

@contextmanager
def get_sync_session() -> Generator[Session, None, None]:
    """Context manager for scripts that need a synchronous database session."""
    session = SyncSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def init_db() -> None:
    """Initialize the database by creating all tables based on loaded models."""
    from backend.models import Base
    
    # Base.metadata.create_all requires a synchronous engine.
    print("Initializing database tables...")
    Base.metadata.create_all(bind=sync_engine)
    print("Database tables created successfully.")
