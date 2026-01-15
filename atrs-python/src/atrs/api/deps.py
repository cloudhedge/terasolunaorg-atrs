"""API dependencies for dependency injection"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from databases import Database

from ..config import get_database
from ..core.security import decode_access_token
from ..models import Member
from ..repositories import MemberRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_db() -> Database:
    """Get database connection"""
    return await get_database()


async def get_current_user(
    db: Annotated[Database, Depends(get_db)],
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> Member | None:
    """Get current authenticated user (returns None if not authenticated)"""
    if not token:
        return None

    payload = decode_access_token(token)
    if not payload:
        return None

    membership_number = payload.get("sub")
    if not membership_number:
        return None

    member_repo = MemberRepository(db)
    return await member_repo.find_one(membership_number)


async def get_current_user_required(
    current_user: Annotated[Member | None, Depends(get_current_user)],
) -> Member:
    """Get current user or raise 401 if not authenticated"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


# Type aliases for dependency injection
DatabaseDep = Annotated[Database, Depends(get_db)]
CurrentUserDep = Annotated[Member | None, Depends(get_current_user)]
CurrentUserRequiredDep = Annotated[Member, Depends(get_current_user_required)]
