"""Base repository with common database operations"""

from typing import Any
from databases import Database


class BaseRepository:
    """Base class for all repositories providing common DB operations"""

    def __init__(self, database: Database):
        self._db = database

    async def fetch_one(self, query: str, values: dict[str, Any] | None = None) -> dict | None:
        """Execute query and return single row"""
        return await self._db.fetch_one(query=query, values=values or {})

    async def fetch_all(self, query: str, values: dict[str, Any] | None = None) -> list[dict]:
        """Execute query and return all rows"""
        return await self._db.fetch_all(query=query, values=values or {})

    async def execute(self, query: str, values: dict[str, Any] | None = None) -> None:
        """Execute a query without returning results"""
        await self._db.execute(query=query, values=values or {})

    async def execute_returning(self, query: str, values: dict[str, Any] | None = None) -> Any:
        """Execute query and return the result (for INSERT RETURNING, etc.)"""
        return await self._db.execute(query=query, values=values or {})
