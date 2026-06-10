"""Database engine, session factory, and shared declarative base."""

import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv(override=True)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db():
    """Provide an async database session for request-scoped dependencies."""
    async with AsyncSessionLocal() as session:
        yield session
