"""Plane model.

航空機情報 - Plane/Aircraft Information.
"""

from pydantic import BaseModel, Field


class Plane(BaseModel):
    """Plane/Aircraft entity.
    
    Represents an aircraft type with seat configuration.
    
    Attributes:
        craft_type: Aircraft type identifier
        n_seat_num: Number of normal/economy seats
        s_seat_num: Number of special/business seats
    """
    craft_type: str = Field(max_length=10, description="Aircraft type")
    n_seat_num: int = Field(ge=0, description="Normal seat count")
    s_seat_num: int = Field(ge=0, description="Special seat count")

    class Config:
        """Pydantic model configuration."""
        from_attributes = True

    @property
    def total_seats(self) -> int:
        """Get total number of seats."""
        return self.n_seat_num + self.s_seat_num
