"""Flight master model.

フライト基本情報 - Flight Master Information.
"""

from pydantic import BaseModel, Field

from .plane import Plane
from .route import Route


class FlightMaster(BaseModel):
    """Flight master entity.
    
    Represents static flight schedule information.
    
    Attributes:
        flight_name: Flight identifier (e.g., 'NH001')
        departure_time: Scheduled departure time (HH:MM format)
        arrival_time: Scheduled arrival time (HH:MM format)
        route: Flight route
        plane: Aircraft type
    """
    flight_name: str = Field(max_length=10, description="Flight name/number")
    departure_time: str = Field(max_length=5, description="Departure time (HH:MM)")
    arrival_time: str = Field(max_length=5, description="Arrival time (HH:MM)")
    route: Route = Field(description="Flight route")
    plane: Plane = Field(description="Aircraft information")

    class Config:
        """Pydantic model configuration."""
        from_attributes = True
