"""Domain models module."""

from .enums import BoardingClassCd, FareTypeCd, FlightType, Gender
from .airport import Airport
from .boarding_class import BoardingClass
from .credit_type import CreditType
from .fare_type import FareType
from .peak_time import PeakTime
from .plane import Plane
from .route import Route
from .flight_master import FlightMaster
from .flight import Flight
from .member_login import MemberLogin
from .member import Member
from .passenger import Passenger
from .reserve_flight import ReserveFlight
from .reservation import Reservation

__all__ = [
    # Enums
    "BoardingClassCd",
    "FareTypeCd",
    "FlightType",
    "Gender",
    # Entities
    "Airport",
    "BoardingClass",
    "CreditType",
    "FareType",
    "PeakTime",
    "Plane",
    "Route",
    "FlightMaster",
    "Flight",
    "MemberLogin",
    "Member",
    "Passenger",
    "ReserveFlight",
    "Reservation",
]
