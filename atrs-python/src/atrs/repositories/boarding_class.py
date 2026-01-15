"""Boarding class repository - 搭乗クラスリポジトリ."""

from ..models import BoardingClass
from ..models.enums import BoardingClassCd
from .base import BaseRepository


# SQL Queries - ported from BoardingClassRepository.xml
FIND_ALL = """
    SELECT
        boarding_class_cd,
        boarding_class_name,
        extra_charge
    FROM
        boarding_class
"""


class BoardingClassRepository(BaseRepository):
    """Repository for BoardingClass entity operations."""

    async def find_all(self) -> list[BoardingClass]:
        """Find all boarding classes.
        
        Returns:
            List of all boarding class configurations
        """
        rows = await self.fetch_all(FIND_ALL)
        return [
            BoardingClass(
                boarding_class_cd=BoardingClassCd(row["boarding_class_cd"]),
                boarding_class_name=row["boarding_class_name"],
                extra_charge=row["extra_charge"],
            )
            for row in rows
        ]
