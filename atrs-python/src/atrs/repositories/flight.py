"""Flight repository for data access"""

from datetime import date

from .base import BaseRepository
from .sql import flight as sql
from ..models import (
    Flight, FlightMaster, Route, Airport, Plane,
    FareType, BoardingClass, PeakTime, BoardingClassCd, FareTypeCd
)


class FlightRepository(BaseRepository):
    """Repository for flight data access"""

    async def find_by_vacant_seat_search_criteria(
        self,
        dep_airport_cd: str,
        arr_airport_cd: str,
        departure_date: date,
        boarding_class_cd: str,
        before_day_num: int,
        fare_type_list: list[str],
    ) -> list[Flight]:
        """Search for available flights matching criteria"""
        # Build parameterized IN clause
        fare_params = {f"ft_{i}": ft for i, ft in enumerate(fare_type_list)}
        fare_placeholders = ", ".join(f":ft_{i}" for i in range(len(fare_type_list)))

        query = sql.FIND_BY_VACANT_SEAT_SEARCH_CRITERIA.format(
            fare_types=fare_placeholders
        )

        values = {
            "dep_airport_cd": dep_airport_cd,
            "arr_airport_cd": arr_airport_cd,
            "departure_date": departure_date,
            "boarding_class_cd": boarding_class_cd,
            "before_day_num": before_day_num,
            **fare_params,
        }

        rows = await self.fetch_all(query, values)

        return [
            Flight(
                departure_date=row["departure_date"],
                flight_name=row["flight_name"],
                boarding_class_cd=BoardingClassCd(row["boarding_class_cd"]),
                fare_type_cd=FareTypeCd(row["fare_type_cd"]),
                vacant_num=row["vacant_num"],
            )
            for row in rows
        ]

    async def find_one_for_update(
        self,
        departure_date: date,
        flight_name: str,
        boarding_class_cd: str,
        fare_type_cd: str,
    ) -> Flight | None:
        """Find flight with row lock for update (pessimistic locking)"""
        row = await self.fetch_one(sql.FIND_ONE_FOR_UPDATE, {
            "departure_date": departure_date,
            "flight_name": flight_name,
            "boarding_class_cd": boarding_class_cd,
            "fare_type_cd": fare_type_cd,
        })

        if not row:
            return None

        return Flight(
            departure_date=row["departure_date"],
            flight_name=row["flight_name"],
            boarding_class_cd=BoardingClassCd(row["boarding_class_cd"]),
            fare_type_cd=FareTypeCd(row["fare_type_cd"]),
            vacant_num=row["vacant_num"],
        )

    async def update(self, flight: Flight) -> None:
        """Update flight vacancy count"""
        await self.execute(sql.UPDATE_VACANT_NUM, {
            "departure_date": flight.departure_date,
            "flight_name": flight.flight_name,
            "boarding_class_cd": flight.boarding_class_cd.value,
            "fare_type_cd": flight.fare_type_cd.value,
            "vacant_num": flight.vacant_num,
        })

    async def exists(
        self,
        departure_date: date,
        flight_name: str,
        boarding_class_cd: str,
        fare_type_cd: str,
    ) -> bool:
        """Check if flight exists"""
        row = await self.fetch_one(sql.EXISTS, {
            "departure_date": departure_date,
            "flight_name": flight_name,
            "boarding_class_cd": boarding_class_cd,
            "fare_type_cd": fare_type_cd,
        })
        return row["exists"] if row else False

    async def find_all_flight_master(self) -> list[FlightMaster]:
        """Get all flight master data with route info"""
        rows = await self.fetch_all(sql.FIND_ALL_FLIGHT_MASTER)

        return [
            FlightMaster(
                flight_name=row["flight_name"],
                route_no=row["route_no"],
                departure_time=row["departure_time"],
                arrival_time=row["arrival_time"],
                craft_type=row["craft_type"],
                route=Route(
                    route_no=row["route_no"],
                    dep_airport_cd=row["dep_airport_cd"],
                    arr_airport_cd=row["arr_airport_cd"],
                    flight_time=row["flight_time"],
                    basic_fare=row["basic_fare"],
                    departure_airport=Airport(
                        airport_cd=row["dep_airport_cd"],
                        airport_name=row["dep_airport_name"],
                        display_order=0,
                    ),
                    arrival_airport=Airport(
                        airport_cd=row["arr_airport_cd"],
                        airport_name=row["arr_airport_name"],
                        display_order=0,
                    ),
                ),
            )
            for row in rows
        ]

    async def find_all_routes(self) -> list[Route]:
        """Get all routes"""
        rows = await self.fetch_all(sql.FIND_ALL_ROUTES)
        return [
            Route(
                route_no=row["route_no"],
                dep_airport_cd=row["dep_airport_cd"],
                arr_airport_cd=row["arr_airport_cd"],
                flight_time=row["flight_time"],
                basic_fare=row["basic_fare"],
            )
            for row in rows
        ]

    async def find_all_fare_types(self) -> list[FareType]:
        """Get all fare types"""
        rows = await self.fetch_all(sql.FIND_ALL_FARE_TYPES)
        return [
            FareType(
                fare_type_cd=FareTypeCd(row["fare_type_cd"]),
                fare_type_name=row["fare_type_name"],
                discount_rate=row["discount_rate"],
                rsrv_available_start_day_num=row["rsrv_available_start_day_num"],
                rsrv_available_end_day_num=row["rsrv_available_end_day_num"],
                passenger_min_num=row["passenger_min_num"],
                display_order=row["display_order"],
            )
            for row in rows
        ]

    async def find_all_boarding_classes(self) -> list[BoardingClass]:
        """Get all boarding classes"""
        rows = await self.fetch_all(sql.FIND_ALL_BOARDING_CLASSES)
        return [
            BoardingClass(
                boarding_class_cd=BoardingClassCd(row["boarding_class_cd"]),
                boarding_class_name=row["boarding_class_name"],
                extra_charge=row["extra_charge"],
                display_order=row["display_order"],
            )
            for row in rows
        ]

    async def find_all_peak_times(self) -> list[PeakTime]:
        """Get all peak time periods"""
        rows = await self.fetch_all(sql.FIND_ALL_PEAK_TIMES)
        return [
            PeakTime(
                peak_time_cd=row["peak_time_cd"],
                peak_start_date=row["peak_start_date"],
                peak_end_date=row["peak_end_date"],
                multiplication_ratio=row["multiplication_ratio"],
            )
            for row in rows
        ]

    async def find_all_airports(self) -> list[Airport]:
        """Get all airports"""
        rows = await self.fetch_all(sql.FIND_ALL_AIRPORTS)
        return [
            Airport(
                airport_cd=row["airport_cd"],
                airport_name=row["airport_name"],
                display_order=row["display_order"],
            )
            for row in rows
        ]
