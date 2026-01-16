"""API module."""

from fastapi import APIRouter

from .v1 import auth, flights, tickets

api_router = APIRouter()

# Include versioned routers
api_router.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
api_router.include_router(flights.router, prefix="/v1/flights", tags=["flights"])
api_router.include_router(tickets.router, prefix="/v1/tickets", tags=["tickets"])
