"""Base repository with common database operations."""

from typing import Any

from databases import Database


class BaseRepository:
    """Base repository class with common database operations.
    
    All repositories should inherit from this class.
    """

    def __init__(self, db: Database):
        """Initialize repository with database connection.
        
        Args:
            db: Database connection instance
        """
        self.db = db

    async def fetch_one(self, query: str, values: dict[str, Any] | None = None) -> Any:
        """Fetch a single row from the database.
        
        Args:
            query: SQL query string
            values: Query parameters
            
        Returns:
            Single row result or None
        """
        return await self.db.fetch_one(query, values or {})

    async def fetch_all(self, query: str, values: dict[str, Any] | None = None) -> list[Any]:
        """Fetch all matching rows from the database.
        
        Args:
            query: SQL query string
            values: Query parameters
            
        Returns:
            List of row results
        """
        return await self.db.fetch_all(query, values or {})

    async def execute(self, query: str, values: dict[str, Any] | None = None) -> Any:
        """Execute a query (INSERT, UPDATE, DELETE).
        
        Args:
            query: SQL query string
            values: Query parameters
            
        Returns:
            Last inserted ID or affected row count
        """
        return await self.db.execute(query, values or {})
