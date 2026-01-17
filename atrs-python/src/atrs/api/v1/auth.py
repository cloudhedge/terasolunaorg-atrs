"""Authentication API router.

Ported from AuthApiController.java and related controllers.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from ...api.deps import CurrentUser, DatabaseDep
from ...core.exceptions import InvalidPasswordException, MemberNotFoundException
from ...core.security import Token
from ...services.a0 import AuthLoginService, AuthLogoutService

router = APIRouter()


class LoginResponse(BaseModel):
    """Login response with token."""
    access_token: str
    token_type: str = "bearer"
    membership_number: str


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: DatabaseDep = None,
):
    """Authenticate member and return JWT token.
    
    Args:
        form_data: OAuth2 form with username (membership_number) and password
        db: Database connection
        
    Returns:
        LoginResponse with access token
        
    Raises:
        HTTPException 401: If authentication fails
    """
    try:
        service = AuthLoginService(db)
        token = await service.authenticate(
            membership_number=form_data.username,
            password=form_data.password,
        )
        return LoginResponse(
            access_token=token.access_token,
            token_type=token.token_type,
            membership_number=form_data.username,
        )
    except (MemberNotFoundException, InvalidPasswordException):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid membership number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
async def logout(
    current_user: CurrentUser,
    db: DatabaseDep = None,
):
    """Logout current user.
    
    Args:
        current_user: Authenticated user
        db: Database connection
        
    Returns:
        Success message
    """
    service = AuthLogoutService(db)
    await service.logout(current_user.membership_number)
    return {"message": "Successfully logged out"}


@router.get("/me")
async def get_current_member(
    current_user: CurrentUser,
    db: DatabaseDep = None,
):
    """Get current authenticated member info.
    
    Args:
        current_user: Authenticated user
        db: Database connection
        
    Returns:
        Member information
    """
    service = AuthLoginService(db)
    member = await service.get_member(current_user.membership_number)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )
    return {
        "membership_number": member.membership_number,
        "name": member.full_name_kanji,
        "email": member.mail,
    }
