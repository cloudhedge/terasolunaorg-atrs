"""Flight search API endpoints"""

from fastapi import APIRouter, HTTPException, status, Query
from datetime import date

from ...models.enums import BoardingClassCd, FlightType
from ...services.ticket import TicketSearchService
from ...services.ticket.search_service import SearchCriteria
from ...schemas.flight import (
    FlightSearchResponse,
    FlightVacantInfoResponse,
    FareTypeInfoResponse,
)
from ...core.exceptions import AtrsBusinessException, FlightNotFoundException
from ..deps import DatabaseDep

router = APIRouter()


@router.get("/search", response_model=FlightSearchResponse)
async def search_flights(
    db: DatabaseDep,
    dep_airport_cd: str = Query(min_length=3, max_length=3),
    arr_airport_cd: str = Query(min_length=3, max_length=3),
    dep_date: date = Query(...),
    boarding_class_cd: BoardingClassCd = Query(...),
    flight_type: FlightType = Query(default=FlightType.RT),
) -> FlightSearchResponse:
    """
    Search for available flights.

    Returns flights with vacancy info grouped by departure time.
    """
    search_service = TicketSearchService(db)

    criteria = SearchCriteria(
        dep_airport_cd=dep_airport_cd,
        arr_airport_cd=arr_airport_cd,
        dep_date=dep_date,
        boarding_class_cd=boarding_class_cd,
        flight_type=flight_type,
    )

    try:
        results = await search_service.search_flights(criteria)
    except FlightNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No flights found matching the search criteria",
        )
    except AtrsBusinessException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Convert to response format
    flights = [
        FlightVacantInfoResponse(
            flight_name=r.flight_name,
            dep_airport_name=r.dep_airport_name,
            arr_airport_name=r.arr_airport_name,
            dep_time=r.dep_time,
            arr_time=r.arr_time,
            dep_date=r.dep_date,
            boarding_class_cd=r.boarding_class_cd,
            fare_types=[
                FareTypeInfoResponse(
                    fare_type_cd=cd,
                    fare_type_name=info.fare_type_name,
                    fare=info.fare,
                    vacant_num=info.vacant_num,
                )
                for cd, info in r.fare_type_info.items()
            ],
        )
        for r in results
    ]

    return FlightSearchResponse(
        flights=flights,
        total_count=len(flights),
    )
