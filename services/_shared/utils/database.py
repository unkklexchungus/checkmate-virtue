"""
Shared database utilities for async SQLModel operations.
"""

from typing import AsyncGenerator, Optional
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import text
import logging

from ..config.settings import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database manager for async operations."""
    
    def __init__(self, schema: Optional[str] = None):
        self.schema = schema or settings.database.schema
        self._async_engine: Optional[AsyncEngine] = None
        self._async_session_maker: Optional[async_sessionmaker[AsyncSession]] = None
        self._sync_engine: Optional[Session] = None
    
    @property
    def async_engine(self) -> AsyncEngine:
        """Get async engine with schema configuration."""
        if self._async_engine is None:
            url = settings.database.url
            self._async_engine = create_async_engine(
                url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                echo=settings.service.debug,
                connect_args={
                    "server_settings": {
                        "search_path": self.schema
                    }
                }
            )
        return self._async_engine
    
    @property
    def async_session_maker(self) -> async_sessionmaker[AsyncSession]:
        """Get async session maker."""
        if self._async_session_maker is None:
            self._async_session_maker = async_sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
        return self._async_session_maker
    
    @property
    def sync_engine(self) -> Session:
        """Get sync engine for migrations."""
        if self._sync_engine is None:
            url = settings.database.sync_url
            self._sync_engine = create_engine(
                url,
                poolclass=StaticPool,
                echo=settings.service.debug
            )
        return self._sync_engine
    
    async def create_schema(self) -> None:
        """Create schema if it doesn't exist."""
        async with self.async_engine.begin() as conn:
            await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {self.schema}"))
            await conn.execute(text(f"SET search_path TO {self.schema}"))
    
    async def create_tables(self, models: list[type[SQLModel]]) -> None:
        """Create tables for the given models."""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    
    async def drop_tables(self, models: list[type[SQLModel]]) -> None:
        """Drop tables for the given models."""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session."""
        async with self.async_session_maker() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                logger.error(f"Database session error: {e}")
                raise
            finally:
                await session.close()
    
    async def close(self) -> None:
        """Close database connections."""
        if self._async_engine:
            await self._async_engine.dispose()
        if self._sync_engine:
            self._sync_engine.dispose()


# Global database manager instances for each service
customer_db = DatabaseManager(schema="customers")
vehicle_db = DatabaseManager(schema="vehicles")
appointment_db = DatabaseManager(schema="appointments")
workshop_db = DatabaseManager(schema="workshop")
inventory_db = DatabaseManager(schema="inventory")
notification_db = DatabaseManager(schema="notifications")
api_gateway_db = DatabaseManager(schema="api_gateway")


def get_db_manager(service_name: str) -> DatabaseManager:
    """Get database manager for specific service."""
    managers = {
        "customer": customer_db,
        "vehicle": vehicle_db,
        "appointment": appointment_db,
        "workshop": workshop_db,
        "inventory": inventory_db,
        "notification": notification_db,
        "api_gateway": api_gateway_db,
    }
    return managers.get(service_name, customer_db)
