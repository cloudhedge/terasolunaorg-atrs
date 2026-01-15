"""Repository module for data access."""

from .base import BaseRepository
from .route import RouteRepository
from .peak_time import PeakTimeRepository
from .boarding_class import BoardingClassRepository
from .fare_type import FareTypeRepository
from .member import MemberRepository
from .flight import FlightRepository
from .reservation import ReservationRepository

__all__ = [
    "BaseRepository",
    "RouteRepository",
    "PeakTimeRepository",
    "BoardingClassRepository",
    "FareTypeRepository",
    "MemberRepository",
    "FlightRepository",
    "ReservationRepository",
]
