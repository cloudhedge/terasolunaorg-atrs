"""API dependencies for dependency injection."""

from typing import Annotated

from databases import Database
from fastapi import Depends

from ..config.database import get_database
from ..core.security import TokenData, get_current_user

# Type aliases for dependency injection
DatabaseDep = Annotated[Database, Depends(get_database)]
CurrentUser = Annotated[TokenData, Depends(get_current_user)]
