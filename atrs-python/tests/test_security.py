"""Tests for core security module."""

import pytest
from datetime import timedelta

from atrs.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    """Test password hashing functions."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "secret123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert hashed.startswith("$2b$")  # BCrypt prefix

    def test_verify_password_success(self):
        """Test successful password verification."""
        password = "mypassword"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_password_failure(self):
        """Test failed password verification."""
        password = "mypassword"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False


class TestJWTTokens:
    """Test JWT token functions."""

    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "0000000001"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token(self):
        """Test JWT token decoding."""
        membership_number = "0000000001"
        token = create_access_token({"sub": membership_number})
        
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert decoded.membership_number == membership_number

    def test_decode_invalid_token(self):
        """Test decoding invalid token returns None."""
        invalid_token = "invalid.token.here"
        
        decoded = decode_access_token(invalid_token)
        
        assert decoded is None

    def test_token_with_custom_expiration(self):
        """Test token creation with custom expiration."""
        data = {"sub": "0000000001"}
        expires = timedelta(hours=1)
        
        token = create_access_token(data, expires_delta=expires)
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert decoded.membership_number == "0000000001"
