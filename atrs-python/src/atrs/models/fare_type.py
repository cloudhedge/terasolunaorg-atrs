"""Fare type model.

運賃種別情報 - Fare Type Information.
"""

from pydantic import BaseModel, Field

from .enums import FareTypeCd


class FareType(BaseModel):
    """Fare type entity.
    
    Represents a fare type with discount rules and booking constraints.
    
    Attributes:
        fare_type_cd: Fare type code
        fare_type_name: Display name
        discount_rate: Discount percentage (0-100)
        rsrv_available_start_day_num: Days before departure when booking starts
        rsrv_available_end_day_num: Days before departure when booking ends
        passenger_min_num: Minimum passengers required for this fare
    """
    fare_type_cd: FareTypeCd = Field(description="Fare type code")
    fare_type_name: str = Field(max_length=50, description="Fare type name")
    discount_rate: int = Field(ge=0, le=100, description="Discount rate percentage")
    rsrv_available_start_day_num: int = Field(ge=0, description="Reservation available start days")
    rsrv_available_end_day_num: int = Field(ge=0, description="Reservation available end days")
    passenger_min_num: int = Field(ge=1, description="Minimum passengers required")

    class Config:
        """Pydantic model configuration."""
        from_attributes = True
