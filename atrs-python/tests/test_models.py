"""Tests for domain models."""

import pytest
from datetime import date

from atrs.models import (
    Airport,
    BoardingClass,
    FareType,
    Flight,
    Member,
    Passenger,
)
from atrs.models.enums import (
    BoardingClassCd,
    FareTypeCd,
    FlightType,
    Gender,
)


class TestEnums:
    """Test enum types."""

    def test_gender_values(self):
        """Test Gender enum values."""
        assert Gender.M.value == "M"
        assert Gender.F.value == "F"
        assert Gender.M.label == "Male"
        assert Gender.F.label == "Female"

    def test_boarding_class_cd_values(self):
        """Test BoardingClassCd enum values."""
        assert BoardingClassCd.N.value == "N"
        assert BoardingClassCd.S.value == "S"
        assert BoardingClassCd.N.label == "Normal"
        assert BoardingClassCd.S.label == "Special"

    def test_fare_type_cd_values(self):
        """Test FareTypeCd enum values."""
        assert FareTypeCd.OW.value == "OW"
        assert FareTypeCd.RT.value == "RT"
        assert FareTypeCd.GD.value == "GD"

    def test_flight_type_values(self):
        """Test FlightType enum values."""
        assert FlightType.OW.value == "OW"
        assert FlightType.RT.value == "RT"
        assert FlightType.OW.label == "One Way"
        assert FlightType.RT.label == "Round Trip"


class TestAirport:
    """Test Airport model."""

    def test_airport_creation(self):
        """Test Airport model creation."""
        airport = Airport(code="HND", name="羽田空港", display_order=1)
        assert airport.code == "HND"
        assert airport.name == "羽田空港"
        assert airport.display_order == 1

    def test_airport_optional_display_order(self):
        """Test Airport with optional display_order."""
        airport = Airport(code="ITM", name="伊丹空港")
        assert airport.display_order is None


class TestBoardingClass:
    """Test BoardingClass model."""

    def test_boarding_class_creation(self):
        """Test BoardingClass model creation."""
        bc = BoardingClass(
            boarding_class_cd=BoardingClassCd.N,
            boarding_class_name="普通席",
            extra_charge=0,
        )
        assert bc.boarding_class_cd == BoardingClassCd.N
        assert bc.boarding_class_name == "普通席"
        assert bc.extra_charge == 0


class TestFareType:
    """Test FareType model."""

    def test_fare_type_creation(self):
        """Test FareType model creation."""
        ft = FareType(
            fare_type_cd=FareTypeCd.OW,
            fare_type_name="片道運賃",
            discount_rate=0,
            rsrv_available_start_day_num=30,
            rsrv_available_end_day_num=0,
            passenger_min_num=1,
        )
        assert ft.fare_type_cd == FareTypeCd.OW
        assert ft.discount_rate == 0
        assert ft.passenger_min_num == 1


class TestPassenger:
    """Test Passenger model."""

    def test_passenger_creation(self):
        """Test Passenger model creation."""
        passenger = Passenger(
            family_name="山田",
            given_name="太郎",
            age=30,
            gender=Gender.M,
        )
        assert passenger.family_name == "山田"
        assert passenger.given_name == "太郎"
        assert passenger.age == 30
        assert passenger.gender == Gender.M

    def test_passenger_full_name(self):
        """Test Passenger full_name property."""
        passenger = Passenger(
            family_name="田中",
            given_name="花子",
            age=25,
            gender=Gender.F,
        )
        assert passenger.full_name == "田中 花子"


class TestMemberValidation:
    """Test Member model validation."""

    def test_birthday_must_be_past(self):
        """Test that birthday validation rejects future dates."""
        from datetime import timedelta
        from pydantic import ValidationError
        from atrs.models import CreditType

        future_date = date.today() + timedelta(days=1)
        
        with pytest.raises(ValidationError) as exc_info:
            Member(
                membership_number="0000000001",
                kanji_family_name="山田",
                kanji_given_name="太郎",
                kana_family_name="ヤマダ",
                kana_given_name="タロウ",
                birthday=future_date,
                gender=Gender.M,
                tel="03-1234-5678",
                zip_code="100-0001",
                address="東京都千代田区",
                mail="test@example.com",
                credit_no="4111111111111111",
                credit_term="12/25",
                credit_type=CreditType(credit_type_cd="VISA", credit_firm="Visa Inc."),
            )
        
        assert "birthday" in str(exc_info.value)
