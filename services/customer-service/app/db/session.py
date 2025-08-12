"""
Database session configuration for customer service.
"""

from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession

from _shared.utils.database import customer_db


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for customer service."""
    async for session in customer_db.get_session():
        yield session
