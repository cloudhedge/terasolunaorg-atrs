"""Flight search service"""

from dataclasses import dataclass
from datetime import date, timedelta
from databases import Database

from ...models import Flight, FlightType, BoardingClassCd, FareTypeCd
from ...repositories import FlightRepository
from ...core.exceptions import AtrsBusinessException, ErrorCode, FlightNotFoundException
from .shared_service import TicketSharedService


@dataclass
class FareTypeVacantInfo:
    """Vacancy info for a specific fare type"""
    fare_type_name: str
    fare: str  # Formatted fare string
    vacant_num: int


@dataclass
class FlightVacantInfo:
    """Flight vacancy search result"""
    flight_name: str
    dep_airport_name: str
    arr_airport_name: str
    dep_time: str  # Formatted time "09:30"
    arr_time: str
    dep_date: str  # Formatted date
    boarding_class_cd: BoardingClassCd
    fare_type_info: dict[FareTypeCd, FareTypeVacantInfo]

    def add_fare_type_info(self, fare_type_cd: FareTypeCd, info: FareTypeVacantInfo):
        self.fare_type_info[fare_type_cd] = info


@dataclass
class SearchCriteria:
    """Search criteria for flight vacancy search"""
    dep_airport_cd: str
    arr_airport_cd: str
    dep_date: date
    boarding_class_cd: BoardingClassCd
    flight_type: FlightType


class TicketSearchService:
    """Service for searching available flights"""

    def __init__(self, database: Database):
        self._db = database
        self._flight_repo = FlightRepository(database)
        self._shared_service = TicketSharedService(database)

    async def search_flights(self, criteria: SearchCriteria) -> list[FlightVacantInfo]:
        """
        Search for available flights matching criteria.

        Returns list of flights grouped by departure time with fare type options.
        """
        # Validate departure date is within bookable range
        await self._shared_service.validate_departure_date(criteria.dep_date)

        # Get route for the airports
        route = await self._shared_service.get_route_by_airport_codes(
            criteria.dep_airport_cd, criteria.arr_airport_cd
        )
        if not route:
            raise AtrsBusinessException(ErrorCode.E_AR_B1_2002)

        # Calculate days before departure
        today = date.today()
        before_day_num = (criteria.dep_date - today).days

        # Get applicable fare types for flight type
        fare_type_codes = self._shared_service.get_fare_type_codes_for_flight_type(
            criteria.flight_type
        )

        # Search for flights
        flights = await self._flight_repo.find_by_vacant_seat_search_criteria(
            dep_airport_cd=criteria.dep_airport_cd,
            arr_airport_cd=criteria.arr_airport_cd,
            departure_date=criteria.dep_date,
            boarding_class_cd=criteria.boarding_class_cd.value,
            before_day_num=before_day_num,
            fare_type_list=fare_type_codes,
        )

        if not flights:
            raise FlightNotFoundException()

        # Enrich flights with master data
        await self._enrich_flights(flights)

        # Calculate basic fare for the route
        basic_fare = await self._shared_service.calculate_basic_fare(
            route.basic_fare,
            criteria.boarding_class_cd,
            criteria.dep_date,
        )

        # Group flights by departure time and create result DTOs
        return self._create_flight_vacant_info_list(flights, basic_fare)

    async def _enrich_flights(self, flights: list[Flight]) -> None:
        """Populate flights with related entities from master data"""
        fare_types = await self._shared_service.get_fare_types()
        flight_masters = await self._shared_service.get_flight_masters()
        boarding_classes = await self._shared_service.get_boarding_classes()

        for flight in flights:
            # Set fare type
            flight.fare_type = fare_types.get(flight.fare_type_cd.value)

            # Set flight master
            flight.flight_master = flight_masters.get(flight.flight_name)

            # Set boarding class
            flight.boarding_class = boarding_classes.get(flight.boarding_class_cd.value)

    def _create_flight_vacant_info_list(
        self, flights: list[Flight], basic_fare: int
    ) -> list[FlightVacantInfo]:
        """Create grouped vacancy info list from flights"""
        # Group by departure time
        vacant_info_map: dict[str, FlightVacantInfo] = {}

        for flight in flights:
            flight_master = flight.flight_master
            if not flight_master:
                continue

            departure_time = flight_master.departure_time
            vacant_info = vacant_info_map.get(departure_time)

            if vacant_info is None:
                vacant_info = self._create_flight_vacant_info(flight)
                vacant_info_map[departure_time] = vacant_info

            # Add fare type info
            fare_type = flight.fare_type
            if fare_type:
                fare = self._shared_service.calculate_fare(
                    basic_fare, fare_type.discount_rate
                )
                fare_type_info = FareTypeVacantInfo(
                    fare_type_name=fare_type.fare_type_name,
                    fare=f"{fare:,}",  # Format with thousands separator
                    vacant_num=flight.vacant_num,
                )
                vacant_info.add_fare_type_info(fare_type.fare_type_cd, fare_type_info)

        return list(vacant_info_map.values())

    def _create_flight_vacant_info(self, flight: Flight) -> FlightVacantInfo:
        """Create vacancy info for a single flight"""
        flight_master = flight.flight_master
        route = flight_master.route if flight_master else None

        return FlightVacantInfo(
            flight_name=flight_master.flight_name if flight_master else "",
            dep_airport_name=route.departure_airport.airport_name if route and route.departure_airport else "",
            arr_airport_name=route.arrival_airport.airport_name if route and route.arrival_airport else "",
            dep_time=self._format_time(flight_master.departure_time) if flight_master else "",
            arr_time=self._format_time(flight_master.arrival_time) if flight_master else "",
            dep_date=flight.departure_date.strftime("%Y/%m/%d"),
            boarding_class_cd=flight.boarding_class_cd,
            fare_type_info={},
        )

    @staticmethod
    def _format_time(time_str: str) -> str:
        """Format time string from '0930' to '09:30'"""
        if len(time_str) == 4:
            return f"{time_str[:2]}:{time_str[2:]}"
        return time_str
