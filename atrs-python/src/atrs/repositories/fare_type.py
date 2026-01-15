"""Fare type repository - 運賃種別リポジトリ."""

from ..models import FareType
from ..models.enums import FareTypeCd
from .base import BaseRepository


# SQL Queries - ported from FareTypeRepository.xml
FIND_ALL = """
    SELECT
        fare_type_cd,
        fare_type_name,
        discount_rate,
        rsrv_available_start_day_num,
        rsrv_available_end_day_num,
        passenger_min_num
    FROM
        fare_type
"""


class FareTypeRepository(BaseRepository):
    """Repository for FareType entity operations."""

    async def find_all(self) -> list[FareType]:
        """Find all fare types.
        
        Returns:
            List of all fare type configurations
        """
        rows = await self.fetch_all(FIND_ALL)
        return [
            FareType(
                fare_type_cd=FareTypeCd(row["fare_type_cd"]),
                fare_type_name=row["fare_type_name"],
                discount_rate=row["discount_rate"],
                rsrv_available_start_day_num=row["rsrv_available_start_day_num"],
                rsrv_available_end_day_num=row["rsrv_available_end_day_num"],
                passenger_min_num=row["passenger_min_num"],
            )
            for row in rows
        ]
