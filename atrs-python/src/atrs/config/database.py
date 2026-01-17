"""Database connection configuration."""

from databases import Database

from .settings import settings

database = Database(settings.database_url)


async def get_database() -> Database:
    """Dependency to get database connection."""
    return database
