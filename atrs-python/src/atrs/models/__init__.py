"""Domain models"""

from .enums import Gender, FareTypeCd, BoardingClassCd, FlightType
from .member import Member, MemberLogin, CreditType
from .flight import (
    Airport,
    Plane,
    Route,
    BoardingClass,
    FareType,
    PeakTime,
    FlightMaster,
    Flight,
)
from .reservation import Reservation, ReserveFlight, Passenger

__all__ = [
    # Enums
    "Gender",
    "FareTypeCd",
    "BoardingClassCd",
    "FlightType",
    # Member
    "Member",
    "MemberLogin",
    "CreditType",
    # Flight
    "Airport",
    "Plane",
    "Route",
    "BoardingClass",
    "FareType",
    "PeakTime",
    "FlightMaster",
    "Flight",
    # Reservation
    "Reservation",
    "ReserveFlight",
    "Passenger",
]
