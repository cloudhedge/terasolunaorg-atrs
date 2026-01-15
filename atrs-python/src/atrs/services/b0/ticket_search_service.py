"""Ticket search service - チケット検索サービス.

Ported from TicketSearchServiceImpl.java
"""

from dataclasses import dataclass
from datetime import date

from databases import Database
from pydantic import BaseModel

from ...core.exceptions import FlightNotFoundException, InvalidSearchCriteriaException
from ...models.enums import BoardingClassCd, FareTypeCd, FlightType
from ...repositories import FlightRepository
from .ticket_shared_service import TicketSharedService


class TicketSearchCriteria(BaseModel):
    """Search criteria for flight search.
    
    Ported from TicketSearchCriteriaDto.java
    """
    departure_date: date
    dep_airport_cd: str
    arr_airport_cd: str
    boarding_class_cd: BoardingClassCd
    flight_type: FlightType = FlightType.OW


@dataclass
class FareTypeVacantInfo:
    """Vacant seat info for a specific fare type.
    
    Ported from FareTypeVacantInfoDto.java
    """
    fare_type_cd: FareTypeCd
    fare_type_name: str
    fare: int
    vacant_num: int


@dataclass
class FlightVacantInfo:
    """Flight vacancy information.
    
    Ported from FlightVacantInfoDto.java
    """
    departure_date: date
    flight_name: str
    departure_time: str
    arrival_time: str
    departure_airport_name: str
    arrival_airport_name: str
    boarding_class_cd: BoardingClassCd
    fare_type_list: list[FareTypeVacantInfo]


class TicketSearchService:
    """Service for searching available flights.
    
    Provides flight search functionality with vacancy information.
    """

    def __init__(self, db: Database):
        """Initialize service with database connection.
        
        Args:
            db: Database connection instance
        """
        self.db = db
        self.flight_repo = FlightRepository(db)
        self.ticket_shared = TicketSharedService(db)

    async def search_flight(
        self, criteria: TicketSearchCriteria
    ) -> list[FlightVacantInfo]:
        """Search for available flights matching criteria.
        
        Args:
            criteria: Search criteria
            
        Returns:
            List of flights with vacancy information
            
        Raises:
            InvalidSearchCriteriaException: If criteria is invalid
            FlightNotFoundException: If no flights found
        """
        # Validate search criteria
        self._validate_criteria(criteria)

        # Calculate days before departure
        days_before = (criteria.departure_date - date.today()).days

        # Get applicable fare types
        fare_types = await self._get_applicable_fare_types(
            criteria.boarding_class_cd, criteria.flight_type
        )

        if not fare_types:
            raise FlightNotFoundException()

        # Search flights
        results = await self.flight_repo.find_by_vacant_seat_search_criteria(
            dep_airport_cd=criteria.dep_airport_cd,
            arr_airport_cd=criteria.arr_airport_cd,
            departure_date=criteria.departure_date,
            boarding_class_cd=criteria.boarding_class_cd,
            fare_type_list=fare_types,
            before_day_num=days_before,
        )

        if not results:
            raise FlightNotFoundException()

        # Get flight master data for display
        flight_masters = await self.flight_repo.find_all_flight_master()
        flight_master_map = {fm.flight_name: fm for fm in flight_masters}

        # Group results by flight
        return await self._build_flight_vacant_info(
            results, flight_master_map, criteria
        )

    def _validate_criteria(self, criteria: TicketSearchCriteria) -> None:
        """Validate search criteria.
        
        Args:
            criteria: Search criteria to validate
            
        Raises:
            InvalidSearchCriteriaException: If criteria is invalid
        """
        today = date.today()
        limit_date = self.ticket_shared.get_search_limit_date()

        if criteria.departure_date < today:
            raise InvalidSearchCriteriaException("Departure date cannot be in the past")

        if criteria.departure_date > limit_date:
            raise InvalidSearchCriteriaException(
                f"Cannot search more than {limit_date} days ahead"
            )

        if criteria.dep_airport_cd == criteria.arr_airport_cd:
            raise InvalidSearchCriteriaException(
                "Departure and arrival airports must be different"
            )

    async def _get_applicable_fare_types(
        self, boarding_class_cd: BoardingClassCd, flight_type: FlightType
    ) -> list[FareTypeCd]:
        """Get fare types applicable for the search.
        
        Args:
            boarding_class_cd: Boarding class
            flight_type: One-way or round-trip
            
        Returns:
            List of applicable fare type codes
        """
        # Normal class fare types
        if boarding_class_cd == BoardingClassCd.N:
            if flight_type == FlightType.OW:
                return [
                    FareTypeCd.OW,
                    FareTypeCd.RD1,
                    FareTypeCd.RD7,
                    FareTypeCd.ED,
                    FareTypeCd.LD,
                    FareTypeCd.GD,
                ]
            else:  # Round trip
                return [
                    FareTypeCd.RT,
                    FareTypeCd.RD1,
                    FareTypeCd.RD7,
                    FareTypeCd.ED,
                    FareTypeCd.LD,
                    FareTypeCd.GD,
                ]
        
        # Special class fare types
        else:
            if flight_type == FlightType.OW:
                return [FareTypeCd.SOW, FareTypeCd.SRD]
            else:
                return [FareTypeCd.SRT, FareTypeCd.SRD]

    async def _build_flight_vacant_info(
        self, results: list, flight_master_map: dict, criteria: TicketSearchCriteria
    ) -> list[FlightVacantInfo]:
        """Build flight vacancy info from search results.
        
        Args:
            results: Raw search results
            flight_master_map: Flight master data
            criteria: Original search criteria
            
        Returns:
            List of FlightVacantInfo
        """
        # Group by flight_name
        flights_dict: dict[str, list] = {}
        for row in results:
            flight_name = row["flight_name"]
            if flight_name not in flights_dict:
                flights_dict[flight_name] = []
            flights_dict[flight_name].append(row)

        # Build result list
        result = []
        fare_types_dict = await self.ticket_shared.get_fare_types()

        for flight_name, rows in flights_dict.items():
            fm = flight_master_map.get(flight_name)
            if not fm:
                continue

            fare_type_list = []
            for row in rows:
                fare_type_cd = FareTypeCd(row["fare_type_cd"])
                ft = fare_types_dict.get(fare_type_cd)
                if not ft:
                    continue

                # Calculate fare
                fare = await self.ticket_shared.calculate_fare(
                    basic_fare=fm.route.basic_fare,
                    departure_date=criteria.departure_date,
                    boarding_class_cd=criteria.boarding_class_cd,
                    fare_type_cd=fare_type_cd,
                )

                fare_type_list.append(
                    FareTypeVacantInfo(
                        fare_type_cd=fare_type_cd,
                        fare_type_name=ft.fare_type_name,
                        fare=fare,
                        vacant_num=row["vacant_num"],
                    )
                )

            if fare_type_list:
                result.append(
                    FlightVacantInfo(
                        departure_date=criteria.departure_date,
                        flight_name=flight_name,
                        departure_time=fm.departure_time,
                        arrival_time=fm.arrival_time,
                        departure_airport_name=fm.route.departure_airport.name,
                        arrival_airport_name=fm.route.arrival_airport.name,
                        boarding_class_cd=criteria.boarding_class_cd,
                        fare_type_list=fare_type_list,
                    )
                )

        return result
