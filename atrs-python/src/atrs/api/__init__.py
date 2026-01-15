"""API module"""

from fastapi import APIRouter

from .v1 import auth, flights, reservations, members

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(flights.router, prefix="/flights", tags=["flights"])
api_router.include_router(reservations.router, prefix="/reservations", tags=["reservations"])
api_router.include_router(members.router, prefix="/members", tags=["members"])
