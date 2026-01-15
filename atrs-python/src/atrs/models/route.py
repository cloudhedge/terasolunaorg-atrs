"""Route model.

区間情報 - Route Information.
"""

from pydantic import BaseModel, Field

from .airport import Airport


class Route(BaseModel):
    """Route entity.
    
    Represents a flight route between two airports with base fare.
    
    Attributes:
        route_no: Route identifier
        basic_fare: Base fare for this route
        departure_airport: Departure airport
        arrival_airport: Arrival airport
    """
    route_no: int = Field(description="Route number")
    basic_fare: int = Field(ge=0, description="Basic fare amount")
    departure_airport: Airport = Field(description="Departure airport")
    arrival_airport: Airport = Field(description="Arrival airport")

    class Config:
        """Pydantic model configuration."""
        from_attributes = True
