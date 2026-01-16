"""Security module for authentication and authorization.

Ported from Spring Security configuration.
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from ..config.settings import settings


# Password hashing context (BCrypt, same as Java)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class Token(BaseModel):
    """JWT token response model."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data encoded in JWT token."""
    membership_number: str | None = None
    exp: datetime | None = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password.
    
    Args:
        plain_password: Plain text password
        hashed_password: BCrypt hashed password
        
    Returns:
        True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash a password using BCrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        BCrypt hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token.
    
    Args:
        data: Data to encode in token
        expires_delta: Token expiration time (default from settings)
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> TokenData | None:
    """Decode and validate a JWT access token.
    
    Args:
        token: JWT token string
        
    Returns:
        TokenData if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        membership_number: str = payload.get("sub")
        if membership_number is None:
            return None
        return TokenData(membership_number=membership_number)
    except JWTError:
        return None


async def get_current_user_optional(
    token: str = Depends(oauth2_scheme)
) -> TokenData | None:
    """Get current user from token, returns None if not authenticated.
    
    Args:
        token: JWT token from request
        
    Returns:
        TokenData if authenticated, None otherwise
    """
    return decode_access_token(token)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Get current authenticated user from token.
    
    Args:
        token: JWT token from request
        
    Returns:
        TokenData with user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = decode_access_token(token)
    if token_data is None:
        raise credentials_exception
    return token_data


def require_role(role: str):
    """Dependency factory for role-based access control.
    
    Args:
        role: Required role name
        
    Returns:
        Dependency function that checks for role
    """
    async def role_checker(user: TokenData = Depends(get_current_user)) -> TokenData:
        # For now, all authenticated users have ROLE_MEMBER
        # In production, check user's roles
        if role == "MEMBER":
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Required role: {role}",
        )
    return role_checker


# Type aliases for dependency injection
CurrentUser = Annotated[TokenData, Depends(get_current_user)]
OptionalUser = Annotated[TokenData | None, Depends(get_current_user_optional)]
