"""Passenger model.

搭乗者情報 - Passenger Information.
"""

from pydantic import BaseModel, Field

from .enums import Gender
from .member import Member


class Passenger(BaseModel):
    """Passenger entity.
    
    Represents a passenger on a flight reservation.
    
    Attributes:
        passenger_no: Unique passenger ID
        reserve_flight_no: Associated reserve flight ID
        family_name: Passenger's family name
        given_name: Passenger's given name
        age: Passenger's age
        gender: Passenger's gender
        member: Associated member (if registered)
    """
    passenger_no: int | None = Field(default=None, description="Passenger number")
    reserve_flight_no: int | None = Field(default=None, description="Reserve flight number")
    family_name: str = Field(max_length=20, description="Family name")
    given_name: str = Field(max_length=20, description="Given name")
    age: int = Field(ge=0, le=150, description="Age")
    gender: Gender = Field(description="Gender")
    member: Member | None = Field(default=None, description="Associated member")

    class Config:
        """Pydantic model configuration."""
        from_attributes = True

    @property
    def full_name(self) -> str:
        """Get full name."""
        return f"{self.family_name} {self.given_name}"
