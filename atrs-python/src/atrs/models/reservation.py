"""Reservation model.

予約情報 - Reservation Information.
"""

from datetime import date

from pydantic import BaseModel, EmailStr, Field

from .enums import Gender
from .member import Member
from .reserve_flight import ReserveFlight


class Reservation(BaseModel):
    """Reservation entity.
    
    Represents a complete flight reservation.
    
    Attributes:
        reserve_no: Unique reservation number (10 digits)
        reserve_date: Date reservation was made
        total_fare: Total fare amount
        rep_family_name: Representative's family name
        rep_given_name: Representative's given name
        rep_age: Representative's age
        rep_gender: Representative's gender
        rep_tel: Representative's telephone
        rep_mail: Representative's email
        rep_member: Representative's member info (if registered)
        reserve_flight_list: List of reserved flights
    """
    reserve_no: str | None = Field(default=None, max_length=10, description="Reservation number")
    reserve_date: date = Field(description="Reservation date")
    total_fare: int = Field(ge=0, description="Total fare amount")
    rep_family_name: str = Field(max_length=20, description="Representative family name")
    rep_given_name: str = Field(max_length=20, description="Representative given name")
    rep_age: int = Field(ge=0, le=150, description="Representative age")
    rep_gender: Gender = Field(description="Representative gender")
    rep_tel: str = Field(max_length=15, description="Representative telephone")
    rep_mail: EmailStr = Field(description="Representative email")
    rep_member: Member | None = Field(default=None, description="Representative member info")
    reserve_flight_list: list[ReserveFlight] = Field(
        default_factory=list, description="List of reserved flights"
    )

    class Config:
        """Pydantic model configuration."""
        from_attributes = True

    @property
    def rep_full_name(self) -> str:
        """Get representative's full name."""
        return f"{self.rep_family_name} {self.rep_given_name}"
