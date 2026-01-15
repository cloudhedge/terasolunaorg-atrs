"""Authentication schemas"""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Login request payload"""
    membership_number: str = Field(min_length=10, max_length=10)
    password: str = Field(min_length=8, max_length=20)


class LoginResponse(BaseModel):
    """Login response with access token"""
    access_token: str
    token_type: str = "bearer"
    membership_number: str
    member_name: str


class TokenData(BaseModel):
    """Data extracted from JWT token"""
    membership_number: str | None = None
