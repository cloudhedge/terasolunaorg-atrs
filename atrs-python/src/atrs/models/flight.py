"""Flight-related domain models"""

from datetime import date
from pydantic import BaseModel, Field

from .enums import BoardingClassCd, FareTypeCd


class Airport(BaseModel):
    """Airport reference data"""
    airport_cd: str = Field(max_length=3)
    airport_name: str = Field(max_length=15)
    display_order: int


class Plane(BaseModel):
    """Aircraft type reference data"""
    craft_type: str = Field(max_length=16)
    n_seat_num: int  # Normal class seat count
    s_seat_num: int  # Special class seat count


class Route(BaseModel):
    """Flight route information"""
    route_no: int
    dep_airport_cd: str = Field(max_length=3)
    arr_airport_cd: str = Field(max_length=3)
    flight_time: str = Field(max_length=4)  # e.g., "0130" = 1hr 30min
    basic_fare: int

    # Related objects
    departure_airport: Airport | None = None
    arrival_airport: Airport | None = None


class BoardingClass(BaseModel):
    """Boarding class reference data"""
    boarding_class_cd: BoardingClassCd
    boarding_class_name: str | None = Field(default=None, max_length=10)
    extra_charge: int
    display_order: int


class FareType(BaseModel):
    """Fare type reference data with discount rules"""
    fare_type_cd: FareTypeCd
    fare_type_name: str = Field(max_length=10)
    discount_rate: int  # Percentage discount (0-100)
    rsrv_available_start_day_num: int  # Days before departure to start booking
    rsrv_available_end_day_num: int    # Days before departure to end booking
    passenger_min_num: int  # Minimum passengers for group fares
    display_order: int


class PeakTime(BaseModel):
    """Peak time periods with fare multipliers"""
    peak_time_cd: str = Field(max_length=10)
    peak_start_date: date
    peak_end_date: date
    multiplication_ratio: int  # Percentage multiplier (e.g., 110 = 10% increase)


class FlightMaster(BaseModel):
    """Flight master/template information"""
    flight_name: str = Field(max_length=6)
    route_no: int
    departure_time: str = Field(max_length=4)  # e.g., "0900"
    arrival_time: str = Field(max_length=4)    # e.g., "1030"
    craft_type: str = Field(max_length=16)

    # Related objects
    route: Route | None = None
    plane: Plane | None = None


class Flight(BaseModel):
    """Available flight instance with vacancy"""
    # Composite primary key fields
    departure_date: date
    flight_name: str = Field(max_length=6)
    boarding_class_cd: BoardingClassCd
    fare_type_cd: FareTypeCd

    # Data
    vacant_num: int

    # Related objects
    flight_master: FlightMaster | None = None
    boarding_class: BoardingClass | None = None
    fare_type: FareType | None = None

    @property
    def has_vacancy(self) -> bool:
        return self.vacant_num > 0
