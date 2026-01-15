"""Ticket reservation service"""

from dataclasses import dataclass
from datetime import date
from databases import Database

from ...models import (
    Flight, Reservation, ReserveFlight, Passenger,
    Gender, FareTypeCd, Member
)
from ...repositories import FlightRepository, ReservationRepository, MemberRepository
from ...core.exceptions import AtrsBusinessException, ErrorCode
from ...core.fare_calculator import FareCalculator
from .shared_service import TicketSharedService


@dataclass
class ReservationResult:
    """Result of a successful reservation"""
    reserve_no: str
    payment_date: date


@dataclass
class PassengerInput:
    """Input data for a passenger"""
    family_name: str
    given_name: str
    age: int
    gender: Gender
    customer_no: str | None = None


@dataclass
class ReservationInput:
    """Input data for creating a reservation"""
    # Representative info
    rep_family_name: str
    rep_given_name: str
    rep_age: int
    rep_gender: Gender
    rep_tel: str
    rep_mail: str
    rep_customer_no: str | None = None

    # Flights and passengers
    flights: list[Flight]
    passengers: list[PassengerInput]


class TicketReserveService:
    """Service for making flight reservations"""

    # Configuration (would be loaded from settings in production)
    REPRESENTATIVE_MIN_AGE = 18
    ADULT_PASSENGER_MIN_AGE = 12
    CHILD_FARE_RATE = 50  # 50% of adult fare

    def __init__(self, database: Database):
        self._db = database
        self._flight_repo = FlightRepository(database)
        self._reservation_repo = ReservationRepository(database)
        self._member_repo = MemberRepository(database)
        self._shared_service = TicketSharedService(database)

    async def calculate_total_fare(
        self, flights: list[Flight], passengers: list[PassengerInput]
    ) -> int:
        """Calculate total fare for flights and passengers"""
        boarding_classes = await self._shared_service.get_boarding_classes()
        peak_times = await self._shared_service.get_peak_times()

        # Enrich flights with master data
        await self._enrich_flights(flights)

        # Create Passenger objects for calculation
        passenger_objs = [
            Passenger(
                passenger_no=0,
                reserve_flight_no=0,
                family_name=p.family_name,
                given_name=p.given_name,
                age=p.age,
                gender=p.gender,
            )
            for p in passengers
        ]

        return FareCalculator.calculate_total_fare(
            flights=flights,
            passengers=passenger_objs,
            boarding_classes=boarding_classes,
            peak_times=peak_times,
            adult_min_age=self.ADULT_PASSENGER_MIN_AGE,
            child_fare_rate=self.CHILD_FARE_RATE,
        )

    async def validate_reservation(self, input_data: ReservationInput) -> None:
        """Validate reservation data before processing"""
        # Validate representative age
        if input_data.rep_age < self.REPRESENTATIVE_MIN_AGE:
            raise AtrsBusinessException(
                ErrorCode.E_AR_B2_2004,
                min_age=self.REPRESENTATIVE_MIN_AGE
            )

        # Validate flight list
        await self._shared_service.validate_flight_list(input_data.flights)

        # Validate representative member info (if provided)
        if input_data.rep_customer_no:
            await self._validate_representative_member(input_data)

        # Validate passengers
        await self._validate_passengers(input_data)

        # Validate fare type rules
        await self._validate_fare_type_rules(input_data)

    async def register_reservation(
        self, input_data: ReservationInput
    ) -> ReservationResult:
        """
        Register a new reservation.

        This method:
        1. Validates and updates seat vacancy (with pessimistic locking)
        2. Creates reservation record
        3. Creates reserve flight records
        4. Creates passenger records

        Returns reservation number and payment date.
        """
        # Enrich flights with master data
        await self._enrich_flights(input_data.flights)

        # Calculate total fare
        total_fare = await self.calculate_total_fare(
            input_data.flights, input_data.passengers
        )

        # Validate and update vacancy for each flight
        for flight in input_data.flights:
            await self._validate_and_update_vacancy(flight, len(input_data.passengers))

        # Create reservation
        reservation = Reservation(
            reserve_no="",  # Will be generated
            reserve_date=date.today(),
            total_fare=total_fare,
            rep_family_name=input_data.rep_family_name,
            rep_given_name=input_data.rep_given_name,
            rep_age=input_data.rep_age,
            rep_gender=input_data.rep_gender,
            rep_tel=input_data.rep_tel,
            rep_mail=input_data.rep_mail,
            rep_customer_no=input_data.rep_customer_no,
        )

        # Insert reservation
        reserve_no = await self._reservation_repo.insert(reservation)

        # Insert reserve flights and passengers
        for flight in input_data.flights:
            reserve_flight_no = await self._reservation_repo.insert_reserve_flight(
                reserve_no=reserve_no,
                departure_date=flight.departure_date,
                flight_name=flight.flight_name,
                boarding_class_cd=flight.boarding_class_cd.value,
                fare_type_cd=flight.fare_type_cd.value,
            )

            # Insert passengers for this flight
            for passenger in input_data.passengers:
                await self._reservation_repo.insert_passenger(
                    reserve_flight_no=reserve_flight_no,
                    family_name=passenger.family_name,
                    given_name=passenger.given_name,
                    age=passenger.age,
                    gender=passenger.gender,
                    customer_no=passenger.customer_no,
                )

        # Payment date is the outward flight departure date
        payment_date = input_data.flights[0].departure_date

        return ReservationResult(
            reserve_no=reserve_no,
            payment_date=payment_date,
        )

    async def find_member(self, membership_number: str) -> Member | None:
        """Find member by membership number"""
        return await self._member_repo.find_one(membership_number)

    async def _enrich_flights(self, flights: list[Flight]) -> None:
        """Populate flights with related entities from master data"""
        fare_types = await self._shared_service.get_fare_types()
        flight_masters = await self._shared_service.get_flight_masters()
        boarding_classes = await self._shared_service.get_boarding_classes()

        for flight in flights:
            flight.fare_type = fare_types.get(flight.fare_type_cd.value)
            flight.flight_master = flight_masters.get(flight.flight_name)
            flight.boarding_class = boarding_classes.get(flight.boarding_class_cd.value)

    async def _validate_and_update_vacancy(
        self, flight: Flight, passenger_count: int
    ) -> None:
        """Validate seat availability and update vacancy with pessimistic locking"""
        # Check if fare type is still available
        if flight.fare_type:
            is_available = await self._shared_service.is_available_fare_type(
                flight.fare_type, flight.departure_date
            )
            if not is_available:
                raise AtrsBusinessException(ErrorCode.E_AR_B2_2008)

        # Get flight with lock for update
        locked_flight = await self._flight_repo.find_one_for_update(
            departure_date=flight.departure_date,
            flight_name=flight.flight_name,
            boarding_class_cd=flight.boarding_class_cd.value,
            fare_type_cd=flight.fare_type_cd.value,
        )

        if not locked_flight:
            raise AtrsBusinessException(ErrorCode.E_AR_B2_2008)

        # Check if enough seats available
        if locked_flight.vacant_num < passenger_count:
            raise AtrsBusinessException(ErrorCode.E_AR_B2_2009)

        # Update vacancy
        locked_flight.vacant_num -= passenger_count
        await self._flight_repo.update(locked_flight)

    async def _validate_representative_member(
        self, input_data: ReservationInput
    ) -> None:
        """Validate representative member info matches database"""
        member = await self._member_repo.find_one(input_data.rep_customer_no)

        if not member:
            raise AtrsBusinessException(ErrorCode.E_AR_B2_2002)

        # Check info matches
        if (input_data.rep_family_name != member.kana_family_name or
            input_data.rep_given_name != member.kana_given_name or
            input_data.rep_gender != member.gender):
            raise AtrsBusinessException(ErrorCode.E_AR_B2_2003)

    async def _validate_passengers(self, input_data: ReservationInput) -> None:
        """Validate passenger info against member records"""
        for i, passenger in enumerate(input_data.passengers, 1):
            if passenger.customer_no:
                member = await self._member_repo.find_one(passenger.customer_no)

                if not member:
                    raise AtrsBusinessException(
                        ErrorCode.E_AR_B2_2005, position=i
                    )

                # Check info matches
                if (passenger.family_name != member.kana_family_name or
                    passenger.given_name != member.kana_given_name or
                    passenger.gender != member.gender):
                    raise AtrsBusinessException(
                        ErrorCode.E_AR_B2_2006, position=i
                    )

    async def _validate_fare_type_rules(self, input_data: ReservationInput) -> None:
        """Validate fare type specific rules (ladies discount, group discount)"""
        for flight in input_data.flights:
            fare_type_cd = flight.fare_type_cd

            if fare_type_cd == FareTypeCd.LD:
                # Ladies discount: all passengers must be female
                for passenger in input_data.passengers:
                    if passenger.gender == Gender.M:
                        raise AtrsBusinessException(ErrorCode.E_AR_B2_2007)

            elif fare_type_cd == FareTypeCd.GD:
                # Group discount: minimum passenger count
                fare_types = await self._shared_service.get_fare_types()
                fare_type = fare_types.get(fare_type_cd.value)
                if fare_type and len(input_data.passengers) < fare_type.passenger_min_num:
                    raise AtrsBusinessException(
                        ErrorCode.E_AR_B2_2010,
                        fare_type=fare_type.fare_type_name,
                        min_passengers=fare_type.passenger_min_num,
                    )
