"""Tests for exception classes."""

import pytest

from atrs.core.exceptions import (
    AtrsException,
    FlightNotFoundException,
    InsufficientSeatsException,
    InvalidFlightException,
    InvalidPasswordException,
    InvalidSearchCriteriaException,
    MemberNotFoundException,
)


class TestAtrsException:
    """Test base AtrsException."""

    def test_exception_attributes(self):
        """Test exception has code and message."""
        exc = AtrsException("E_TEST_001", "Test error message")
        
        assert exc.code == "E_TEST_001"
        assert exc.message == "Test error message"
        assert str(exc) == "Test error message"


class TestAuthExceptions:
    """Test authentication exceptions."""

    def test_member_not_found(self):
        """Test MemberNotFoundException."""
        exc = MemberNotFoundException()
        
        assert exc.code == "E_AR_A1_2001"
        assert "not found" in exc.message.lower()

    def test_invalid_password(self):
        """Test InvalidPasswordException."""
        exc = InvalidPasswordException()
        
        assert exc.code == "E_AR_A1_2002"
        assert "password" in exc.message.lower()


class TestTicketSearchExceptions:
    """Test ticket search exceptions."""

    def test_flight_not_found(self):
        """Test FlightNotFoundException."""
        exc = FlightNotFoundException()
        
        assert exc.code == "E_AR_B1_2001"
        assert "flight" in exc.message.lower()

    def test_invalid_search_criteria(self):
        """Test InvalidSearchCriteriaException."""
        exc = InvalidSearchCriteriaException("Date is invalid")
        
        assert exc.code == "E_AR_B1_2002"
        assert exc.message == "Date is invalid"


class TestTicketReserveExceptions:
    """Test ticket reservation exceptions."""

    def test_insufficient_seats(self):
        """Test InsufficientSeatsException."""
        exc = InsufficientSeatsException()
        
        assert exc.code == "E_AR_B2_2001"
        assert "seat" in exc.message.lower()

    def test_invalid_flight(self):
        """Test InvalidFlightException."""
        exc = InvalidFlightException("Flight does not exist")
        
        assert exc.code == "E_AR_B2_2002"
        assert exc.message == "Flight does not exist"


class TestExceptionInheritance:
    """Test exception inheritance."""

    def test_all_inherit_from_base(self):
        """Test all exceptions inherit from AtrsException."""
        exceptions = [
            MemberNotFoundException(),
            InvalidPasswordException(),
            FlightNotFoundException(),
            InsufficientSeatsException(),
        ]
        
        for exc in exceptions:
            assert isinstance(exc, AtrsException)
            assert isinstance(exc, Exception)
