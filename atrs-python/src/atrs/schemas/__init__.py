"""API schemas (request/response models)"""

from .auth import LoginRequest, LoginResponse, TokenData
from .flight import (
    FlightSearchRequest,
    FlightSearchResponse,
    FlightVacantInfoResponse,
    FareTypeInfoResponse,
)
from .reservation import (
    ReservationRequest,
    ReservationResponse,
    PassengerRequest,
)
from .member import (
    MemberRegisterRequest,
    MemberUpdateRequest,
    MemberResponse,
)

__all__ = [
    # Auth
    "LoginRequest",
    "LoginResponse",
    "TokenData",
    # Flight
    "FlightSearchRequest",
    "FlightSearchResponse",
    "FlightVacantInfoResponse",
    "FareTypeInfoResponse",
    # Reservation
    "ReservationRequest",
    "ReservationResponse",
    "PassengerRequest",
    # Member
    "MemberRegisterRequest",
    "MemberUpdateRequest",
    "MemberResponse",
]
