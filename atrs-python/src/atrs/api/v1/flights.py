"""Flights API router.

Ported from FlightRestController.java
"""

from datetime import date

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from ...api.deps import DatabaseDep
from ...core.exceptions import FlightNotFoundException, InvalidSearchCriteriaException
from ...models.enums import BoardingClassCd, FareTypeCd, FlightType
from ...services.b0 import TicketSearchService
from ...services.b0.ticket_search_service import (
    FareTypeVacantInfo,
    FlightVacantInfo,
    TicketSearchCriteria,
)

router = APIRouter()


class FareTypeResource(BaseModel):
    """Fare type with vacancy info."""
    fare_type_cd: FareTypeCd
    fare_type_name: str
    fare: int
    vacant_num: int


class FlightResource(BaseModel):
    """Flight with vacancy info."""
    departure_date: date
    flight_name: str
    departure_time: str
    arrival_time: str
    departure_airport_name: str
    arrival_airport_name: str
    boarding_class_cd: BoardingClassCd
    fare_types: list[FareTypeResource]


@router.get("", response_model=list[FlightResource])
async def search_flights(
    departure_date: date = Query(..., description="Departure date"),
    dep_airport_cd: str = Query(..., min_length=3, max_length=3, description="Departure airport code"),
    arr_airport_cd: str = Query(..., min_length=3, max_length=3, description="Arrival airport code"),
    boarding_class_cd: BoardingClassCd = Query(..., description="Boarding class"),
    flight_type: FlightType = Query(FlightType.OW, description="Flight type"),
    db: DatabaseDep = None,
):
    """Search available flights.
    
    Args:
        departure_date: Flight date
        dep_airport_cd: Departure airport code (e.g., 'HND')
        arr_airport_cd: Arrival airport code (e.g., 'ITM')
        boarding_class_cd: Boarding class (N=Normal, S=Special)
        flight_type: One-way or round-trip
        db: Database connection
        
    Returns:
        List of available flights with fare options
        
    Raises:
        HTTPException 400: If search criteria is invalid
        HTTPException 404: If no flights found
    """
    try:
        criteria = TicketSearchCriteria(
            departure_date=departure_date,
            dep_airport_cd=dep_airport_cd,
            arr_airport_cd=arr_airport_cd,
            boarding_class_cd=boarding_class_cd,
            flight_type=flight_type,
        )
        
        service = TicketSearchService(db)
        results = await service.search_flight(criteria)
        
        return [_to_flight_resource(f) for f in results]
        
    except InvalidSearchCriteriaException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except FlightNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No flights found matching criteria",
        )


def _to_flight_resource(flight: FlightVacantInfo) -> FlightResource:
    """Convert FlightVacantInfo to API resource."""
    return FlightResource(
        departure_date=flight.departure_date,
        flight_name=flight.flight_name,
        departure_time=flight.departure_time,
        arrival_time=flight.arrival_time,
        departure_airport_name=flight.departure_airport_name,
        arrival_airport_name=flight.arrival_airport_name,
        boarding_class_cd=flight.boarding_class_cd,
        fare_types=[
            FareTypeResource(
                fare_type_cd=ft.fare_type_cd,
                fare_type_name=ft.fare_type_name,
                fare=ft.fare,
                vacant_num=ft.vacant_num,
            )
            for ft in flight.fare_type_list
        ],
    )
