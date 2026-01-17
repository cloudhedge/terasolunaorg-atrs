"""Ticket reservation service - チケット予約サービス.

Ported from TicketReserveServiceImpl.java
"""

from dataclasses import dataclass
from datetime import date

from databases import Database
from pydantic import BaseModel, EmailStr

from ...core.exceptions import (
    InsufficientSeatsException,
    InvalidFlightException,
    InvalidPassengerException,
)
from ...models import Member, Reservation
from ...models.enums import BoardingClassCd, FareTypeCd, Gender
from ...repositories import FlightRepository, MemberRepository, ReservationRepository
from .ticket_shared_service import TicketSharedService


class PassengerInput(BaseModel):
    """Input data for passenger.
    
    Ported from PassengerResource.java
    """
    family_name: str
    given_name: str
    age: int
    gender: Gender
    customer_no: str | None = None


class FlightSelection(BaseModel):
    """Selected flight for reservation.
    
    Ported from SelectFlightResource.java
    """
    departure_date: date
    flight_name: str
    boarding_class_cd: BoardingClassCd
    fare_type_cd: FareTypeCd


class ReservationInput(BaseModel):
    """Input data for reservation.
    
    Ported from TicketReserveResource.java
    """
    flights: list[FlightSelection]
    passengers: list[PassengerInput]
    rep_family_name: str
    rep_given_name: str
    rep_age: int
    rep_gender: Gender
    rep_tel: str
    rep_mail: EmailStr
    rep_customer_no: str | None = None


@dataclass
class ReservationResult:
    """Result of successful reservation."""
    reserve_no: str
    total_fare: int


class TicketReserveService:
    """Service for ticket reservation operations.
    
    Handles flight reservation with seat management.
    """

    def __init__(self, db: Database):
        """Initialize service with database connection.
        
        Args:
            db: Database connection instance
        """
        self.db = db
        self.flight_repo = FlightRepository(db)
        self.reservation_repo = ReservationRepository(db)
        self.member_repo = MemberRepository(db)
        self.ticket_shared = TicketSharedService(db)

    async def calculate_total_fare(
        self, flights: list[FlightSelection], passenger_count: int
    ) -> int:
        """Calculate total fare for reservation.
        
        Args:
            flights: List of selected flights
            passenger_count: Number of passengers
            
        Returns:
            Total fare amount
        """
        total = 0
        flight_masters = await self.flight_repo.find_all_flight_master()
        fm_map = {fm.flight_name: fm for fm in flight_masters}

        for flight in flights:
            fm = fm_map.get(flight.flight_name)
            if not fm:
                continue

            fare = await self.ticket_shared.calculate_fare(
                basic_fare=fm.route.basic_fare,
                departure_date=flight.departure_date,
                boarding_class_cd=flight.boarding_class_cd,
                fare_type_cd=flight.fare_type_cd,
            )
            total += fare * passenger_count

        return total

    async def reserve(
        self, input_data: ReservationInput, member: Member | None = None
    ) -> ReservationResult:
        """Create a reservation.
        
        Args:
            input_data: Reservation input data
            member: Authenticated member (optional)
            
        Returns:
            ReservationResult with reserve_no and total_fare
            
        Raises:
            InvalidFlightException: If flight is invalid
            InsufficientSeatsException: If not enough seats
            InvalidPassengerException: If passenger data is invalid
        """
        # Validate input
        await self._validate_reservation(input_data)

        passenger_count = len(input_data.passengers)
        total_fare = await self.calculate_total_fare(input_data.flights, passenger_count)

        # Use transaction for atomicity
        async with self.db.transaction():
            # Update seat counts with pessimistic locking
            for flight in input_data.flights:
                await self._decrement_seats(flight, passenger_count)

            # Create reservation record
            rep_member = None
            if input_data.rep_customer_no:
                rep_member = await self.member_repo.find_one(input_data.rep_customer_no)

            reservation = Reservation(
                reserve_date=date.today(),
                total_fare=total_fare,
                rep_family_name=input_data.rep_family_name,
                rep_given_name=input_data.rep_given_name,
                rep_age=input_data.rep_age,
                rep_gender=input_data.rep_gender,
                rep_tel=input_data.rep_tel,
                rep_mail=input_data.rep_mail,
                rep_member=rep_member,
            )

            reserve_no = await self.reservation_repo.insert(reservation)

            # Create reserve flight and passenger records
            for flight in input_data.flights:
                reserve_flight_no = await self.reservation_repo.insert_reserve_flight(
                    reserve_no=reserve_no,
                    departure_date=flight.departure_date,
                    flight_name=flight.flight_name,
                    boarding_class_cd=flight.boarding_class_cd,
                    fare_type_cd=flight.fare_type_cd,
                )

                for passenger in input_data.passengers:
                    await self.reservation_repo.insert_passenger(
                        reserve_flight_no=reserve_flight_no,
                        family_name=passenger.family_name,
                        given_name=passenger.given_name,
                        age=passenger.age,
                        gender=passenger.gender,
                        customer_no=passenger.customer_no,
                    )

        return ReservationResult(reserve_no=reserve_no, total_fare=total_fare)

    async def _validate_reservation(self, input_data: ReservationInput) -> None:
        """Validate reservation input.
        
        Args:
            input_data: Reservation input to validate
            
        Raises:
            InvalidFlightException: If flight is invalid
            InvalidPassengerException: If passengers are invalid
        """
        if not input_data.flights:
            raise InvalidFlightException("At least one flight is required")

        if not input_data.passengers:
            raise InvalidPassengerException("At least one passenger is required")

        # Validate each flight
        for flight in input_data.flights:
            await self.ticket_shared.validate_flight(
                flight.departure_date,
                flight.flight_name,
                flight.boarding_class_cd,
                flight.fare_type_cd,
            )

            # Check fare type availability
            available = await self.ticket_shared.is_available_fare_type(
                flight.fare_type_cd, flight.departure_date
            )
            if not available:
                raise InvalidFlightException(
                    f"Fare type {flight.fare_type_cd} not available for this date"
                )

            # Check passenger count for group discount
            min_count = self.ticket_shared.get_required_passenger_count(
                flight.fare_type_cd
            )
            if len(input_data.passengers) < min_count:
                raise InvalidPassengerException(
                    f"Fare type {flight.fare_type_cd} requires at least {min_count} passengers"
                )

    async def _decrement_seats(
        self, flight: FlightSelection, passenger_count: int
    ) -> None:
        """Decrement seat count for a flight.
        
        Uses pessimistic locking to prevent overselling.
        
        Args:
            flight: Flight to update
            passenger_count: Number of seats to reserve
            
        Raises:
            InsufficientSeatsException: If not enough seats
        """
        # Lock the row for update
        flight_data = await self.flight_repo.find_one_for_update(
            departure_date=flight.departure_date,
            flight_name=flight.flight_name,
            boarding_class_cd=flight.boarding_class_cd,
            fare_type_cd=flight.fare_type_cd,
        )

        if not flight_data:
            raise InvalidFlightException("Flight not found")

        vacant_num = flight_data["vacant_num"]
        if vacant_num < passenger_count:
            raise InsufficientSeatsException()

        # Update seat count
        await self.flight_repo.update(
            departure_date=flight.departure_date,
            flight_name=flight.flight_name,
            boarding_class_cd=flight.boarding_class_cd,
            fare_type_cd=flight.fare_type_cd,
            vacant_num=vacant_num - passenger_count,
        )

    async def check_reservation_exists(self, reserve_no: str) -> bool:
        """Check if a reservation exists.
        
        Args:
            reserve_no: Reservation number to check
            
        Returns:
            True if reservation exists
        """
        # This would need a find_by_reserve_no method in the repository
        # For now, return False as placeholder
        return False
