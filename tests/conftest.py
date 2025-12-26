"""Pytest configuration and fixtures."""
import pytest
import asyncio
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Set test environment before importing config
os.environ["TELEGRAM_BOT_TOKEN"] = "test_token_123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["ADMIN_TELEGRAM_IDS"] = "123456789"

from shared.database import Base
from shared.config import settings


# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# Remove deprecated event_loop fixture - pytest-asyncio handles this automatically


@pytest.fixture
async def test_engine():
    """Create test database engine for each test."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a new database session for a test."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
