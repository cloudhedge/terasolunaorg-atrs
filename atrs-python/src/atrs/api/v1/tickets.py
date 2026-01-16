"""Tickets API router.

Ported from TicketRestController.java
"""

from datetime import date

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, EmailStr

from ...api.deps import CurrentUser, DatabaseDep
from ...core.exceptions import (
    InsufficientSeatsException,
    InvalidFlightException,
    InvalidPassengerException,
)
from ...models.enums import BoardingClassCd, FareTypeCd, Gender
from ...services.b0 import TicketReserveService
from ...services.b0.ticket_reserve_service import (
    FlightSelection,
    PassengerInput,
    ReservationInput,
)

router = APIRouter()


class FlightSelectionRequest(BaseModel):
    """Flight selection for reservation."""
    departure_date: date
    flight_name: str
    boarding_class_cd: BoardingClassCd
    fare_type_cd: FareTypeCd


class PassengerRequest(BaseModel):
    """Passenger information."""
    family_name: str
    given_name: str
    age: int
    gender: Gender
    customer_no: str | None = None


class TicketReserveRequest(BaseModel):
    """Ticket reservation request."""
    flights: list[FlightSelectionRequest]
    passengers: list[PassengerRequest]
    rep_family_name: str
    rep_given_name: str
    rep_age: int
    rep_gender: Gender
    rep_tel: str
    rep_mail: EmailStr
    rep_customer_no: str | None = None


class ReservationResponse(BaseModel):
    """Reservation response."""
    reserve_no: str
    total_fare: int
    message: str = "Reservation successful"


@router.post("", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    request: TicketReserveRequest,
    db: DatabaseDep = None,
):
    """Create a new ticket reservation.
    
    Args:
        request: Reservation request with flights, passengers, and representative info
        db: Database connection
        
    Returns:
        ReservationResponse with reserve_no and total_fare
        
    Raises:
        HTTPException 400: If reservation data is invalid
        HTTPException 409: If not enough seats available
    """
    try:
        # Convert request to service input
        input_data = ReservationInput(
            flights=[
                FlightSelection(
                    departure_date=f.departure_date,
                    flight_name=f.flight_name,
                    boarding_class_cd=f.boarding_class_cd,
                    fare_type_cd=f.fare_type_cd,
                )
                for f in request.flights
            ],
            passengers=[
                PassengerInput(
                    family_name=p.family_name,
                    given_name=p.given_name,
                    age=p.age,
                    gender=p.gender,
                    customer_no=p.customer_no,
                )
                for p in request.passengers
            ],
            rep_family_name=request.rep_family_name,
            rep_given_name=request.rep_given_name,
            rep_age=request.rep_age,
            rep_gender=request.rep_gender,
            rep_tel=request.rep_tel,
            rep_mail=request.rep_mail,
            rep_customer_no=request.rep_customer_no,
        )

        service = TicketReserveService(db)
        result = await service.reserve(input_data)

        return ReservationResponse(
            reserve_no=result.reserve_no,
            total_fare=result.total_fare,
        )

    except InvalidFlightException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except InvalidPassengerException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except InsufficientSeatsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Not enough seats available",
        )


@router.get("/check")
async def check_reservation(
    reserve_no: str = Query(..., min_length=10, max_length=10, description="Reservation number"),
    db: DatabaseDep = None,
):
    """Check if a reservation exists.
    
    Args:
        reserve_no: Reservation number to check
        db: Database connection
        
    Returns:
        Exists status
    """
    service = TicketReserveService(db)
    exists = await service.check_reservation_exists(reserve_no)
    return {"reserve_no": reserve_no, "exists": exists}
