"""Tests for ticket search service."""

import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from atrs.core.exceptions import FlightNotFoundException, InvalidSearchCriteriaException
from atrs.models.enums import BoardingClassCd, FareTypeCd, FlightType
from atrs.services.b0.ticket_search_service import (
    TicketSearchCriteria,
    TicketSearchService,
)
from atrs.services.b0.ticket_shared_service import TicketSharedService


class TestTicketSearchCriteria:
    """Test TicketSearchCriteria model."""

    def test_criteria_creation(self):
        """Test criteria model creation."""
        criteria = TicketSearchCriteria(
            departure_date=date.today() + timedelta(days=7),
            dep_airport_cd="HND",
            arr_airport_cd="ITM",
            boarding_class_cd=BoardingClassCd.N,
            flight_type=FlightType.OW,
        )
        
        assert criteria.dep_airport_cd == "HND"
        assert criteria.arr_airport_cd == "ITM"
        assert criteria.boarding_class_cd == BoardingClassCd.N

    def test_criteria_default_flight_type(self):
        """Test default flight type is one-way."""
        criteria = TicketSearchCriteria(
            departure_date=date.today() + timedelta(days=7),
            dep_airport_cd="HND",
            arr_airport_cd="ITM",
            boarding_class_cd=BoardingClassCd.N,
        )
        
        assert criteria.flight_type == FlightType.OW


class TestTicketSearchServiceValidation:
    """Test TicketSearchService validation."""

    def test_validate_past_date_raises(self):
        """Test validation rejects past departure date."""
        mock_db = MagicMock()
        service = TicketSearchService(mock_db)
        
        criteria = TicketSearchCriteria(
            departure_date=date.today() - timedelta(days=1),
            dep_airport_cd="HND",
            arr_airport_cd="ITM",
            boarding_class_cd=BoardingClassCd.N,
        )
        
        with pytest.raises(InvalidSearchCriteriaException) as exc_info:
            service._validate_criteria(criteria)
        
        assert "past" in exc_info.value.message.lower()

    def test_validate_same_airports_raises(self):
        """Test validation rejects same departure and arrival."""
        mock_db = MagicMock()
        service = TicketSearchService(mock_db)
        
        criteria = TicketSearchCriteria(
            departure_date=date.today() + timedelta(days=7),
            dep_airport_cd="HND",
            arr_airport_cd="HND",  # Same as departure
            boarding_class_cd=BoardingClassCd.N,
        )
        
        with pytest.raises(InvalidSearchCriteriaException) as exc_info:
            service._validate_criteria(criteria)
        
        assert "different" in exc_info.value.message.lower()


class TestTicketSharedService:
    """Test TicketSharedService."""

    def test_get_search_limit_date(self):
        """Test search limit date calculation."""
        mock_db = MagicMock()
        service = TicketSharedService(mock_db)
        
        limit_date = service.get_search_limit_date()
        expected = date.today() + timedelta(days=30)
        
        assert limit_date == expected

    def test_is_ladies_discount_applicable(self):
        """Test ladies discount check."""
        mock_db = MagicMock()
        service = TicketSharedService(mock_db)
        
        from atrs.models.enums import Gender
        
        assert service.is_ladies_discount_applicable(Gender.F) is True
        assert service.is_ladies_discount_applicable(Gender.M) is False

    def test_get_required_passenger_count_group(self):
        """Test group discount requires 3+ passengers."""
        mock_db = MagicMock()
        service = TicketSharedService(mock_db)
        
        assert service.get_required_passenger_count(FareTypeCd.GD) == 3

    def test_get_required_passenger_count_normal(self):
        """Test normal fare requires 1 passenger."""
        mock_db = MagicMock()
        service = TicketSharedService(mock_db)
        
        assert service.get_required_passenger_count(FareTypeCd.OW) == 1
        assert service.get_required_passenger_count(FareTypeCd.RT) == 1
