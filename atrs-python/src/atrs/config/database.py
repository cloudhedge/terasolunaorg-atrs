"""Database connection management using databases library"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from databases import Database

from .settings import settings


class DatabaseManager:
    """Manages database connection lifecycle"""

    def __init__(self, url: str, min_size: int = 5, max_size: int = 20):
        self._database = Database(
            url,
            min_size=min_size,
            max_size=max_size,
        )

    @property
    def database(self) -> Database:
        return self._database

    async def connect(self) -> None:
        await self._database.connect()

    async def disconnect(self) -> None:
        await self._database.disconnect()

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator:
        """Context manager for database transactions"""
        async with self._database.transaction():
            yield


# Global database manager instance
_db_manager: DatabaseManager | None = None


def get_database_manager() -> DatabaseManager:
    """Get or create the database manager singleton"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(
            url=settings.database_url,
            min_size=settings.db_pool_min_size,
            max_size=settings.db_pool_max_size,
        )
    return _db_manager


async def get_database() -> Database:
    """Dependency for FastAPI routes"""
    return get_database_manager().database
