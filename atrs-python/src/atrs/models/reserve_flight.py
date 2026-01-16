"""Reserve flight model.

予約フライト情報 - Reserved Flight Information.
"""

from pydantic import BaseModel, Field

from .flight import Flight
from .passenger import Passenger


class ReserveFlight(BaseModel):
    """Reserve flight entity.
    
    Links a reservation to a specific flight with passengers.
    
    Attributes:
        reserve_flight_no: Unique reserve flight ID
        reserve_no: Associated reservation number
        flight: Flight information
        passenger_list: List of passengers on this flight
    """
    reserve_flight_no: int | None = Field(default=None, description="Reserve flight number")
    reserve_no: str | None = Field(default=None, description="Reservation number")
    flight: Flight = Field(description="Flight information")
    passenger_list: list[Passenger] = Field(default_factory=list, description="Passenger list")

    class Config:
        """Pydantic model configuration."""
        from_attributes = True
