"""Flight repository - フライトリポジトリ."""

from datetime import date
from typing import Any

from ..models import (
    Airport,
    BoardingClass,
    FareType,
    Flight,
    FlightMaster,
    Plane,
    Route,
)
from ..models.enums import BoardingClassCd, FareTypeCd
from .base import BaseRepository


# SQL Queries - ported from FlightRepository.xml

FIND_BY_VACANT_SEAT_SEARCH_CRITERIA_BASE = """
    SELECT
        f.departure_date,
        f.flight_name,
        f.fare_type_cd,
        f.vacant_num,
        f.boarding_class_cd
    FROM
        flight f,
        fare_type ft,
        flight_master fm,
        route r
    WHERE
        f.fare_type_cd = ft.fare_type_cd
    AND
        f.fare_type_cd IN ({fare_type_placeholders})
    AND
        f.flight_name = fm.flight_name
    AND
        fm.route_no = r.route_no
    AND
        r.dep_airport_cd = :dep_airport_cd
    AND
        r.arr_airport_cd = :arr_airport_cd
    AND
        f.departure_date = :departure_date
    AND
        f.boarding_class_cd = :boarding_class_cd
    AND
        :before_day_num BETWEEN ft.rsrv_available_end_day_num AND ft.rsrv_available_start_day_num
    ORDER BY
        ft.display_order ASC,
        fm.departure_time ASC
"""

FIND_ONE_FOR_UPDATE = """
    SELECT
        f.departure_date,
        f.flight_name,
        f.fare_type_cd,
        f.vacant_num,
        f.boarding_class_cd
    FROM
        flight f
    WHERE
        departure_date = :departure_date
    AND
        flight_name = :flight_name
    AND
        boarding_class_cd = :boarding_class_cd
    AND
        fare_type_cd = :fare_type_cd
    FOR UPDATE
"""

UPDATE_FLIGHT = """
    UPDATE
        flight
    SET
        vacant_num = :vacant_num
    WHERE
        departure_date = :departure_date
    AND
        flight_name = :flight_name
    AND
        boarding_class_cd = :boarding_class_cd
    AND
        fare_type_cd = :fare_type_cd
"""

EXISTS = """
    SELECT EXISTS (
        SELECT 1
        FROM flight
        WHERE
            departure_date = :departure_date
        AND
            flight_name = :flight_name
        AND
            boarding_class_cd = :boarding_class_cd
        AND
            fare_type_cd = :fare_type_cd
    )
"""

FIND_ALL_FLIGHT_MASTER = """
    SELECT
        fm.flight_name,
        fm.departure_time,
        fm.arrival_time,
        fm.craft_type,
        p.n_seat_num,
        p.s_seat_num,
        r.route_no,
        r.basic_fare,
        a_dep.airport_cd AS dep_airport_cd,
        a_dep.airport_name AS dep_airport_name,
        a_arr.airport_cd AS arr_airport_cd,
        a_arr.airport_name AS arr_airport_name
    FROM
        flight_master fm,
        plane p,
        route r,
        airport a_dep,
        airport a_arr
    WHERE 
        fm.craft_type = p.craft_type
    AND
        fm.route_no = r.route_no
    AND
        r.dep_airport_cd = a_dep.airport_cd
    AND
        r.arr_airport_cd = a_arr.airport_cd
"""


class FlightRepository(BaseRepository):
    """Repository for Flight entity operations."""

    async def find_by_vacant_seat_search_criteria(
        self,
        dep_airport_cd: str,
        arr_airport_cd: str,
        departure_date: date,
        boarding_class_cd: BoardingClassCd,
        fare_type_list: list[FareTypeCd],
        before_day_num: int,
    ) -> list[dict[str, Any]]:
        """Search available flights by criteria.
        
        Args:
            dep_airport_cd: Departure airport code
            arr_airport_cd: Arrival airport code
            departure_date: Flight date
            boarding_class_cd: Boarding class
            fare_type_list: List of fare types to include
            before_day_num: Days before departure
            
        Returns:
            List of flight data dictionaries
        """
        if not fare_type_list:
            return []

        # Build dynamic IN clause
        placeholders = ", ".join(f":fare_type_{i}" for i in range(len(fare_type_list)))
        query = FIND_BY_VACANT_SEAT_SEARCH_CRITERIA_BASE.format(
            fare_type_placeholders=placeholders
        )

        params = {
            "dep_airport_cd": dep_airport_cd,
            "arr_airport_cd": arr_airport_cd,
            "departure_date": departure_date,
            "boarding_class_cd": boarding_class_cd.value,
            "before_day_num": before_day_num,
        }
        for i, fare_type in enumerate(fare_type_list):
            params[f"fare_type_{i}"] = fare_type.value

        return await self.fetch_all(query, params)

    async def find_one_for_update(
        self,
        departure_date: date,
        flight_name: str,
        boarding_class_cd: BoardingClassCd,
        fare_type_cd: FareTypeCd,
    ) -> dict[str, Any] | None:
        """Find flight with pessimistic lock for update.
        
        Must be called within a transaction.
        
        Args:
            departure_date: Flight date
            flight_name: Flight identifier
            boarding_class_cd: Boarding class
            fare_type_cd: Fare type
            
        Returns:
            Flight data or None
        """
        return await self.fetch_one(
            FIND_ONE_FOR_UPDATE,
            {
                "departure_date": departure_date,
                "flight_name": flight_name,
                "boarding_class_cd": boarding_class_cd.value,
                "fare_type_cd": fare_type_cd.value,
            },
        )

    async def update(
        self,
        departure_date: date,
        flight_name: str,
        boarding_class_cd: BoardingClassCd,
        fare_type_cd: FareTypeCd,
        vacant_num: int,
    ) -> None:
        """Update flight vacant seat count.
        
        Args:
            departure_date: Flight date
            flight_name: Flight identifier
            boarding_class_cd: Boarding class
            fare_type_cd: Fare type
            vacant_num: New vacant seat count
        """
        await self.execute(
            UPDATE_FLIGHT,
            {
                "departure_date": departure_date,
                "flight_name": flight_name,
                "boarding_class_cd": boarding_class_cd.value,
                "fare_type_cd": fare_type_cd.value,
                "vacant_num": vacant_num,
            },
        )

    async def exists(
        self,
        departure_date: date,
        flight_name: str,
        boarding_class_cd: BoardingClassCd,
        fare_type_cd: FareTypeCd,
    ) -> bool:
        """Check if flight exists.
        
        Args:
            departure_date: Flight date
            flight_name: Flight identifier
            boarding_class_cd: Boarding class
            fare_type_cd: Fare type
            
        Returns:
            True if flight exists
        """
        result = await self.fetch_one(
            EXISTS,
            {
                "departure_date": departure_date,
                "flight_name": flight_name,
                "boarding_class_cd": boarding_class_cd.value,
                "fare_type_cd": fare_type_cd.value,
            },
        )
        return result[0] if result else False

    async def find_all_flight_master(self) -> list[FlightMaster]:
        """Find all flight master data with route information.
        
        Returns:
            List of all flight master records
        """
        rows = await self.fetch_all(FIND_ALL_FLIGHT_MASTER)
        return [self._row_to_flight_master(row) for row in rows]

    def _row_to_flight_master(self, row) -> FlightMaster:
        """Convert database row to FlightMaster model."""
        return FlightMaster(
            flight_name=row["flight_name"],
            departure_time=row["departure_time"],
            arrival_time=row["arrival_time"],
            route=Route(
                route_no=row["route_no"],
                basic_fare=row["basic_fare"],
                departure_airport=Airport(
                    code=row["dep_airport_cd"],
                    name=row["dep_airport_name"],
                ),
                arrival_airport=Airport(
                    code=row["arr_airport_cd"],
                    name=row["arr_airport_name"],
                ),
            ),
            plane=Plane(
                craft_type=row["craft_type"],
                n_seat_num=row["n_seat_num"],
                s_seat_num=row["s_seat_num"],
            ),
        )
