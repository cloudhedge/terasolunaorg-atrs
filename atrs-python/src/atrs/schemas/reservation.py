"""Reservation schemas"""

from datetime import date
from pydantic import BaseModel, Field, EmailStr

from ..models.enums import Gender, BoardingClassCd, FareTypeCd


class FlightSelectionRequest(BaseModel):
    """Flight selection for reservation"""
    departure_date: date
    flight_name: str = Field(max_length=6)
    boarding_class_cd: BoardingClassCd
    fare_type_cd: FareTypeCd


class PassengerRequest(BaseModel):
    """Passenger information"""
    family_name: str = Field(max_length=10)
    given_name: str = Field(max_length=10)
    age: int = Field(ge=0, le=150)
    gender: Gender
    customer_no: str | None = Field(default=None, max_length=10)


class ReservationRequest(BaseModel):
    """Reservation request payload"""
    # Representative info
    rep_family_name: str = Field(max_length=10)
    rep_given_name: str = Field(max_length=10)
    rep_age: int = Field(ge=0, le=150)
    rep_gender: Gender
    rep_tel: str = Field(max_length=13)
    rep_mail: EmailStr
    rep_customer_no: str | None = Field(default=None, max_length=10)

    # Flights (1 for one-way, 2 for round-trip)
    flights: list[FlightSelectionRequest] = Field(min_length=1, max_length=2)

    # Passengers
    passengers: list[PassengerRequest] = Field(min_length=1, max_length=10)


class ReservationResponse(BaseModel):
    """Reservation response"""
    reserve_no: str
    payment_date: date
    total_fare: int


class FareCalculationRequest(BaseModel):
    """Request for fare calculation"""
    flights: list[FlightSelectionRequest]
    passengers: list[PassengerRequest]


class FareCalculationResponse(BaseModel):
    """Fare calculation response"""
    total_fare: int
