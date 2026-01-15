"""Reservation-related domain models"""

from datetime import date
from pydantic import BaseModel, Field, EmailStr

from .enums import Gender, BoardingClassCd, FareTypeCd
from .flight import Flight


class Passenger(BaseModel):
    """Passenger information for a reservation"""
    passenger_no: int
    reserve_flight_no: int
    family_name: str = Field(max_length=10)
    given_name: str = Field(max_length=10)
    age: int
    gender: Gender
    customer_no: str | None = Field(default=None, max_length=10)  # If member


class ReserveFlight(BaseModel):
    """A specific flight within a reservation"""
    reserve_flight_no: int
    reserve_no: str = Field(max_length=10)

    # Flight composite key
    departure_date: date
    flight_name: str = Field(max_length=6)
    boarding_class_cd: BoardingClassCd
    fare_type_cd: FareTypeCd

    # Related objects
    flight: Flight | None = None
    passengers: list[Passenger] = Field(default_factory=list)


class Reservation(BaseModel):
    """Ticket reservation"""
    reserve_no: str = Field(max_length=10)
    reserve_date: date
    total_fare: int

    # Representative passenger info
    rep_family_name: str = Field(max_length=10)
    rep_given_name: str = Field(max_length=10)
    rep_age: int
    rep_gender: Gender
    rep_tel: str = Field(max_length=13)
    rep_mail: EmailStr
    rep_customer_no: str | None = Field(default=None, max_length=10)  # If member

    # Related objects
    reserve_flights: list[ReserveFlight] = Field(default_factory=list)


class ReservationSummary(BaseModel):
    """Lightweight reservation for history reports"""
    reserve_no: str
    reserve_date: date
    total_fare: int
    rep_family_name: str
    rep_given_name: str
    departure_date: date
    flight_name: str
    dep_airport_name: str
    arr_airport_name: str
