"""Authentication API endpoints"""

from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from ...services.auth import AuthService
from ...schemas.auth import LoginRequest, LoginResponse
from ..deps import DatabaseDep, CurrentUserRequiredDep

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    db: DatabaseDep,
    form_data: Annotated[OAuth2PasswordRequestForm, ...],
) -> LoginResponse:
    """
    Authenticate user and return access token.

    Use membership_number as username.
    """
    auth_service = AuthService(db)
    result = await auth_service.authenticate(form_data.username, form_data.password)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid membership number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    member = result.member
    return LoginResponse(
        access_token=result.access_token,
        token_type=result.token_type,
        membership_number=member.membership_number,
        member_name=f"{member.kanji_family_name} {member.kanji_given_name}",
    )


@router.post("/logout")
async def logout(
    db: DatabaseDep,
    current_user: CurrentUserRequiredDep,
) -> dict:
    """Log out current user"""
    auth_service = AuthService(db)
    await auth_service.logout(current_user.membership_number)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=LoginResponse)
async def get_current_user_info(
    current_user: CurrentUserRequiredDep,
) -> dict:
    """Get current authenticated user info"""
    return {
        "access_token": "",  # Not returned on /me endpoint
        "token_type": "bearer",
        "membership_number": current_user.membership_number,
        "member_name": f"{current_user.kanji_family_name} {current_user.kanji_given_name}",
    }
