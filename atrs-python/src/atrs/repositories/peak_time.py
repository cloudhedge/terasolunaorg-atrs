"""Peak time repository - ピーク時期情報リポジトリ."""

from ..models import PeakTime
from .base import BaseRepository


# SQL Queries - ported from PeakTimeRepository.xml
FIND_ALL = """
    SELECT
        peak_time_cd,
        peak_start_date,
        peak_end_date,
        multiplication_ratio
    FROM
        peak_time
"""


class PeakTimeRepository(BaseRepository):
    """Repository for PeakTime entity operations."""

    async def find_all(self) -> list[PeakTime]:
        """Find all peak time periods.
        
        Returns:
            List of all peak time configurations
        """
        rows = await self.fetch_all(FIND_ALL)
        return [
            PeakTime(
                peak_time_cd=row["peak_time_cd"],
                peak_start_date=row["peak_start_date"],
                peak_end_date=row["peak_end_date"],
                multiplication_ratio=row["multiplication_ratio"],
            )
            for row in rows
        ]
