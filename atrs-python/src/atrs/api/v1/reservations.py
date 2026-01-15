"""Reservation API endpoints"""

from fastapi import APIRouter, HTTPException, status

from ...models import Flight, Gender
from ...models.enums import BoardingClassCd, FareTypeCd
from ...services.ticket import TicketReserveService
from ...services.ticket.reserve_service import ReservationInput, PassengerInput
from ...schemas.reservation import (
    ReservationRequest,
    ReservationResponse,
    FareCalculationRequest,
    FareCalculationResponse,
)
from ...core.exceptions import AtrsBusinessException, InvalidFlightException
from ..deps import DatabaseDep

router = APIRouter()


def _create_flights_from_request(request_flights) -> list[Flight]:
    """Convert request flight selections to Flight models"""
    return [
        Flight(
            departure_date=f.departure_date,
            flight_name=f.flight_name,
            boarding_class_cd=f.boarding_class_cd,
            fare_type_cd=f.fare_type_cd,
            vacant_num=0,
        )
        for f in request_flights
    ]


def _create_passengers_from_request(request_passengers) -> list[PassengerInput]:
    """Convert request passengers to PassengerInput"""
    return [
        PassengerInput(
            family_name=p.family_name,
            given_name=p.given_name,
            age=p.age,
            gender=p.gender,
            customer_no=p.customer_no,
        )
        for p in request_passengers
    ]


@router.post("/calculate-fare", response_model=FareCalculationResponse)
async def calculate_fare(
    db: DatabaseDep,
    request: FareCalculationRequest,
) -> FareCalculationResponse:
    """Calculate total fare for selected flights and passengers"""
    reserve_service = TicketReserveService(db)

    flights = _create_flights_from_request(request.flights)
    passengers = _create_passengers_from_request(request.passengers)

    try:
        total_fare = await reserve_service.calculate_total_fare(flights, passengers)
    except (AtrsBusinessException, InvalidFlightException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return FareCalculationResponse(total_fare=total_fare)


@router.post("", response_model=ReservationResponse)
async def create_reservation(
    db: DatabaseDep,
    request: ReservationRequest,
) -> ReservationResponse:
    """
    Create a new reservation.

    This will:
    1. Validate the reservation data
    2. Lock and update seat availability
    3. Create reservation records
    """
    reserve_service = TicketReserveService(db)

    flights = _create_flights_from_request(request.flights)
    passengers = _create_passengers_from_request(request.passengers)

    input_data = ReservationInput(
        rep_family_name=request.rep_family_name,
        rep_given_name=request.rep_given_name,
        rep_age=request.rep_age,
        rep_gender=request.rep_gender,
        rep_tel=request.rep_tel,
        rep_mail=request.rep_mail,
        rep_customer_no=request.rep_customer_no,
        flights=flights,
        passengers=passengers,
    )

    try:
        # Validate reservation
        await reserve_service.validate_reservation(input_data)

        # Register reservation
        result = await reserve_service.register_reservation(input_data)
    except AtrsBusinessException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except InvalidFlightException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Calculate total fare for response
    total_fare = await reserve_service.calculate_total_fare(flights, passengers)

    return ReservationResponse(
        reserve_no=result.reserve_no,
        payment_date=result.payment_date,
        total_fare=total_fare,
    )
