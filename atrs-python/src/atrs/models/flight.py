"""Flight model.

フライト情報 - Flight Information.
"""

from datetime import date

from pydantic import BaseModel, Field

from .boarding_class import BoardingClass
from .enums import BoardingClassCd, FareTypeCd
from .fare_type import FareType
from .flight_master import FlightMaster


class Flight(BaseModel):
    """Flight entity.
    
    Represents a flight on a specific date with available seats.
    
    Attributes:
        departure_date: Date of the flight
        vacant_num: Number of vacant seats
        fare_type: Fare type information
        flight_master: Static flight information
        boarding_class: Boarding class information
    """
    departure_date: date = Field(description="Departure date")
    vacant_num: int = Field(ge=0, description="Number of vacant seats")
    fare_type: FareType = Field(description="Fare type")
    flight_master: FlightMaster = Field(description="Flight master information")
    boarding_class: BoardingClass = Field(description="Boarding class")

    class Config:
        """Pydantic model configuration."""
        from_attributes = True


class FlightKey(BaseModel):
    """Flight composite primary key.
    
    Used for lookups and updates.
    """
    departure_date: date
    flight_name: str
    boarding_class_cd: BoardingClassCd
    fare_type_cd: FareTypeCd
