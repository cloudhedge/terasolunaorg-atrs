"""Flight search schemas"""

from datetime import date
from pydantic import BaseModel, Field

from ..models.enums import BoardingClassCd, FlightType, FareTypeCd


class FlightSearchRequest(BaseModel):
    """Flight search request parameters"""
    dep_airport_cd: str = Field(min_length=3, max_length=3)
    arr_airport_cd: str = Field(min_length=3, max_length=3)
    dep_date: date
    boarding_class_cd: BoardingClassCd
    flight_type: FlightType


class FareTypeInfoResponse(BaseModel):
    """Fare type vacancy info"""
    fare_type_cd: FareTypeCd
    fare_type_name: str
    fare: str  # Formatted fare string
    vacant_num: int


class FlightVacantInfoResponse(BaseModel):
    """Single flight vacancy info"""
    flight_name: str
    dep_airport_name: str
    arr_airport_name: str
    dep_time: str
    arr_time: str
    dep_date: str
    boarding_class_cd: BoardingClassCd
    fare_types: list[FareTypeInfoResponse]


class FlightSearchResponse(BaseModel):
    """Flight search response"""
    flights: list[FlightVacantInfoResponse]
    total_count: int
