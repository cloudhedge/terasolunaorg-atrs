"""Shared ticket service for common operations"""

from datetime import date, datetime, timedelta
from databases import Database

from ...models import (
    Flight, FlightMaster, Route, FareType, BoardingClass, PeakTime,
    FareTypeCd, BoardingClassCd, FlightType
)
from ...repositories import FlightRepository
from ...core.exceptions import AtrsBusinessException, ErrorCode, InvalidFlightException
from ...core.fare_calculator import FareCalculator
from ...config import settings


class TicketSharedService:
    """Common ticket operations shared across search and reserve"""

    def __init__(self, database: Database):
        self._db = database
        self._flight_repo = FlightRepository(database)

        # Cached master data (loaded on first access)
        self._routes: dict[str, Route] | None = None
        self._fare_types: dict[str, FareType] | None = None
        self._boarding_classes: dict[str, BoardingClass] | None = None
        self._peak_times: list[PeakTime] | None = None
        self._flight_masters: dict[str, FlightMaster] | None = None

    # Properties for lazy-loaded master data
    @property
    def limit_days(self) -> int:
        return settings.reserve_interval_time

    async def get_routes(self) -> dict[str, Route]:
        if self._routes is None:
            routes = await self._flight_repo.find_all_routes()
            self._routes = {f"{r.dep_airport_cd}_{r.arr_airport_cd}": r for r in routes}
        return self._routes

    async def get_fare_types(self) -> dict[str, FareType]:
        if self._fare_types is None:
            fare_types = await self._flight_repo.find_all_fare_types()
            self._fare_types = {ft.fare_type_cd.value: ft for ft in fare_types}
        return self._fare_types

    async def get_boarding_classes(self) -> dict[str, BoardingClass]:
        if self._boarding_classes is None:
            classes = await self._flight_repo.find_all_boarding_classes()
            self._boarding_classes = {bc.boarding_class_cd.value: bc for bc in classes}
        return self._boarding_classes

    async def get_peak_times(self) -> list[PeakTime]:
        if self._peak_times is None:
            self._peak_times = await self._flight_repo.find_all_peak_times()
        return self._peak_times

    async def get_flight_masters(self) -> dict[str, FlightMaster]:
        if self._flight_masters is None:
            masters = await self._flight_repo.find_all_flight_master()
            self._flight_masters = {fm.flight_name: fm for fm in masters}
        return self._flight_masters

    def get_search_limit_date(self) -> date:
        """Get the maximum date that can be searched (today + limit_days)"""
        return date.today() + timedelta(days=self.limit_days)

    async def validate_departure_date(self, departure_date: date) -> None:
        """Validate that departure date is within bookable range"""
        today = date.today()
        limit_date = self.get_search_limit_date()

        if departure_date < today or departure_date > limit_date:
            raise AtrsBusinessException(
                ErrorCode.E_AR_B1_2001,
                limit_days=self.limit_days
            )

    async def get_route_by_airport_codes(
        self, dep_airport_cd: str, arr_airport_cd: str
    ) -> Route | None:
        """Get route by departure and arrival airport codes"""
        routes = await self.get_routes()
        return routes.get(f"{dep_airport_cd}_{arr_airport_cd}")

    def get_fare_type_codes_for_flight_type(self, flight_type: FlightType) -> list[str]:
        """Get applicable fare type codes based on flight type (one-way vs round-trip)"""
        if flight_type == FlightType.OW:
            # One-way fare types
            return [FareTypeCd.OW.value, FareTypeCd.RD1.value, FareTypeCd.RD7.value,
                    FareTypeCd.ED.value, FareTypeCd.LD.value, FareTypeCd.GD.value,
                    FareTypeCd.SOW.value]
        else:
            # Round-trip fare types
            return [FareTypeCd.RT.value, FareTypeCd.SRT.value]

    async def calculate_basic_fare(
        self,
        basic_fare_of_route: int,
        boarding_class_cd: BoardingClassCd,
        departure_date: date,
    ) -> int:
        """Calculate basic fare with boarding class and peak time adjustments"""
        boarding_classes = await self.get_boarding_classes()
        peak_times = await self.get_peak_times()

        boarding_class = boarding_classes.get(boarding_class_cd.value)
        if not boarding_class:
            raise ValueError(f"Unknown boarding class: {boarding_class_cd}")

        return FareCalculator.calculate_basic_fare(
            basic_fare_of_route,
            boarding_class,
            peak_times,
            departure_date,
        )

    def calculate_fare(self, basic_fare: int, discount_rate: int) -> int:
        """Calculate fare with discount applied"""
        return FareCalculator.calculate_fare(basic_fare, discount_rate)

    async def is_available_fare_type(self, fare_type: FareType, dep_date: date) -> bool:
        """Check if fare type is available for booking on given date"""
        today = date.today()

        # Booking window: dep_date - start_days to dep_date - end_days
        rsrv_start_date = dep_date - timedelta(days=fare_type.rsrv_available_start_day_num)
        rsrv_end_date = dep_date - timedelta(days=fare_type.rsrv_available_end_day_num)

        return rsrv_start_date <= today <= rsrv_end_date

    async def flight_exists(self, flight: Flight) -> bool:
        """Check if flight exists in database"""
        return await self._flight_repo.exists(
            departure_date=flight.departure_date,
            flight_name=flight.flight_name,
            boarding_class_cd=flight.boarding_class_cd.value,
            fare_type_cd=flight.fare_type_cd.value,
        )

    async def validate_flight_list(self, flights: list[Flight]) -> None:
        """Validate flight list for booking (1 for one-way, 2 for round-trip)"""
        if not flights:
            raise InvalidFlightException("Flight list cannot be empty")

        if len(flights) > 2:
            raise InvalidFlightException("Flight list cannot have more than 2 flights")

        # Validate outward flight
        outward = flights[0]
        if not await self.flight_exists(outward):
            raise InvalidFlightException(f"Outward flight not found: {outward.flight_name}")

        # For round-trip, validate return flight
        if len(flights) == 2:
            homeward = flights[1]
            if not await self.flight_exists(homeward):
                raise InvalidFlightException(f"Return flight not found: {homeward.flight_name}")

            # Validate timing (return must be after outward arrival + interval)
            await self._validate_round_trip_timing(outward, homeward)

            # Validate routes are reverse of each other
            await self._validate_round_trip_routes(outward, homeward)

        # Validate fare types
        self._validate_fare_types(flights)

    async def _validate_round_trip_timing(
        self, outward: Flight, homeward: Flight
    ) -> None:
        """Validate return flight departs after outward arrival + interval"""
        flight_masters = await self.get_flight_masters()

        outward_master = flight_masters.get(outward.flight_name)
        homeward_master = flight_masters.get(homeward.flight_name)

        if not outward_master or not homeward_master:
            raise InvalidFlightException("Flight master not found")

        # Parse times (format: "0930" -> 9:30)
        outward_arr = self._parse_time(outward_master.arrival_time)
        homeward_dep = self._parse_time(homeward_master.departure_time)

        # Combine with dates
        outward_arr_dt = datetime.combine(outward.departure_date, outward_arr)
        homeward_dep_dt = datetime.combine(homeward.departure_date, homeward_dep)

        # Check interval
        min_interval = timedelta(minutes=settings.reserve_interval_time)
        if homeward_dep_dt < outward_arr_dt + min_interval:
            raise AtrsBusinessException(
                ErrorCode.E_AR_B2_2001,
                interval=settings.reserve_interval_time
            )

    async def _validate_round_trip_routes(
        self, outward: Flight, homeward: Flight
    ) -> None:
        """Validate return route is reverse of outward route"""
        flight_masters = await self.get_flight_masters()

        outward_master = flight_masters.get(outward.flight_name)
        homeward_master = flight_masters.get(homeward.flight_name)

        if not outward_master or not homeward_master:
            raise InvalidFlightException("Flight master not found")

        outward_route = outward_master.route
        homeward_route = homeward_master.route

        # Check routes are reverse
        if (outward_route.dep_airport_cd != homeward_route.arr_airport_cd or
            outward_route.arr_airport_cd != homeward_route.dep_airport_cd):
            raise InvalidFlightException("Return route must be reverse of outward route")

    def _validate_fare_types(self, flights: list[Flight]) -> None:
        """Validate fare types are appropriate for one-way or round-trip"""
        one_way_types = {FareTypeCd.OW, FareTypeCd.RD1, FareTypeCd.RD7,
                        FareTypeCd.ED, FareTypeCd.LD, FareTypeCd.GD, FareTypeCd.SOW}
        round_trip_types = {FareTypeCd.RT, FareTypeCd.SRT}

        if len(flights) == 1:
            # One-way: must use one-way fare type
            if flights[0].fare_type_cd not in one_way_types:
                raise InvalidFlightException(
                    f"One-way flight must use one-way fare type, got {flights[0].fare_type_cd}"
                )
        else:
            # Round-trip: both must use round-trip fare types
            for flight in flights:
                if flight.fare_type_cd not in round_trip_types:
                    raise InvalidFlightException(
                        f"Round-trip flight must use round-trip fare type, got {flight.fare_type_cd}"
                    )

    @staticmethod
    def _parse_time(time_str: str) -> datetime.time:
        """Parse time string like '0930' to time object"""
        hour = int(time_str[:2])
        minute = int(time_str[2:])
        return datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time()
