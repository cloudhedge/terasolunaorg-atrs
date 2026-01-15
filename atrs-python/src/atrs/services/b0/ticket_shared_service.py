"""Ticket shared service - チケット共有サービス.

Ported from TicketSharedServiceImpl.java
"""

from datetime import date, timedelta

from databases import Database

from ...core.exceptions import FareTypeNotAvailableException, InvalidFlightException
from ...models import FareType, PeakTime
from ...models.enums import BoardingClassCd, FareTypeCd, Gender
from ...repositories import (
    BoardingClassRepository,
    FareTypeRepository,
    FlightRepository,
    PeakTimeRepository,
)


# Constants ported from Java
SEARCH_LIMIT_DAY = 30  # Maximum days ahead for search


class TicketSharedService:
    """Shared service for ticket-related operations.
    
    Provides common ticket functionality used across services.
    """

    def __init__(self, db: Database):
        """Initialize service with database connection.
        
        Args:
            db: Database connection instance
        """
        self.db = db
        self.flight_repo = FlightRepository(db)
        self.fare_type_repo = FareTypeRepository(db)
        self.boarding_class_repo = BoardingClassRepository(db)
        self.peak_time_repo = PeakTimeRepository(db)
        
        # Cached data
        self._fare_types: dict[FareTypeCd, FareType] | None = None
        self._peak_times: list[PeakTime] | None = None

    def get_search_limit_date(self) -> date:
        """Get the maximum date for flight search.
        
        Returns:
            Date SEARCH_LIMIT_DAY days from today
        """
        return date.today() + timedelta(days=SEARCH_LIMIT_DAY)

    async def get_fare_types(self) -> dict[FareTypeCd, FareType]:
        """Get all fare types as a dictionary.
        
        Returns:
            Dictionary of fare type code to FareType
        """
        if self._fare_types is None:
            fare_types = await self.fare_type_repo.find_all()
            self._fare_types = {ft.fare_type_cd: ft for ft in fare_types}
        return self._fare_types

    async def get_peak_times(self) -> list[PeakTime]:
        """Get all peak time periods.
        
        Returns:
            List of peak time configurations
        """
        if self._peak_times is None:
            self._peak_times = await self.peak_time_repo.find_all()
        return self._peak_times

    async def validate_flight(
        self,
        departure_date: date,
        flight_name: str,
        boarding_class_cd: BoardingClassCd,
        fare_type_cd: FareTypeCd,
    ) -> None:
        """Validate that a flight exists.
        
        Args:
            departure_date: Flight date
            flight_name: Flight identifier
            boarding_class_cd: Boarding class
            fare_type_cd: Fare type
            
        Raises:
            InvalidFlightException: If flight does not exist
        """
        exists = await self.flight_repo.exists(
            departure_date, flight_name, boarding_class_cd, fare_type_cd
        )
        if not exists:
            raise InvalidFlightException("Flight does not exist")

    async def is_available_fare_type(
        self, fare_type_cd: FareTypeCd, departure_date: date
    ) -> bool:
        """Check if fare type is available for the given date.
        
        Args:
            fare_type_cd: Fare type to check
            departure_date: Flight date
            
        Returns:
            True if fare type is available
        """
        fare_types = await self.get_fare_types()
        fare_type = fare_types.get(fare_type_cd)
        if not fare_type:
            return False

        days_before = (departure_date - date.today()).days
        return (
            fare_type.rsrv_available_end_day_num
            <= days_before
            <= fare_type.rsrv_available_start_day_num
        )

    async def calculate_basic_fare(
        self,
        basic_fare: int,
        departure_date: date,
        boarding_class_cd: BoardingClassCd,
    ) -> int:
        """Calculate basic fare with peak time and boarding class adjustments.
        
        Args:
            basic_fare: Route's base fare
            departure_date: Flight date
            boarding_class_cd: Boarding class
            
        Returns:
            Adjusted basic fare
        """
        # Get peak time ratio
        peak_ratio = await self._get_peak_ratio(departure_date)
        
        # Get boarding class extra charge
        boarding_classes = await self.boarding_class_repo.find_all()
        extra_charge = 0
        for bc in boarding_classes:
            if bc.boarding_class_cd == boarding_class_cd:
                extra_charge = bc.extra_charge
                break

        # Calculate: (basic_fare * peak_ratio / 100) + extra_charge
        return int(basic_fare * peak_ratio / 100) + extra_charge

    async def calculate_fare(
        self,
        basic_fare: int,
        departure_date: date,
        boarding_class_cd: BoardingClassCd,
        fare_type_cd: FareTypeCd,
    ) -> int:
        """Calculate final fare with discount.
        
        Args:
            basic_fare: Route's base fare
            departure_date: Flight date
            boarding_class_cd: Boarding class
            fare_type_cd: Fare type
            
        Returns:
            Final fare after discount
        """
        # Get adjusted basic fare
        adjusted_fare = await self.calculate_basic_fare(
            basic_fare, departure_date, boarding_class_cd
        )
        
        # Apply discount
        fare_types = await self.get_fare_types()
        fare_type = fare_types.get(fare_type_cd)
        if not fare_type:
            return adjusted_fare

        discount_rate = fare_type.discount_rate
        return int(adjusted_fare * (100 - discount_rate) / 100)

    async def _get_peak_ratio(self, target_date: date) -> int:
        """Get peak time ratio for a date.
        
        Args:
            target_date: Date to check
            
        Returns:
            Multiplication ratio (100 = normal, >100 = peak)
        """
        peak_times = await self.get_peak_times()
        for peak_time in peak_times:
            if peak_time.peak_start_date <= target_date <= peak_time.peak_end_date:
                return peak_time.multiplication_ratio
        return 100  # Normal ratio

    def is_ladies_discount_applicable(self, gender: Gender) -> bool:
        """Check if ladies discount is applicable.
        
        Args:
            gender: Passenger's gender
            
        Returns:
            True if female
        """
        return gender == Gender.F

    def get_required_passenger_count(self, fare_type_cd: FareTypeCd) -> int:
        """Get minimum passenger count for fare type.
        
        For group discounts, returns minimum required passengers.
        
        Args:
            fare_type_cd: Fare type to check
            
        Returns:
            Minimum passenger count (1 for most fare types)
        """
        if fare_type_cd == FareTypeCd.GD:
            return 3  # Group discount requires 3+ passengers
        return 1
