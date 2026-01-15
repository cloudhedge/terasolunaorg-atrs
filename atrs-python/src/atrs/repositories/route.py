"""Route repository - 区間情報リポジトリ."""

from ..models import Airport, Route
from .base import BaseRepository


# SQL Queries - ported from RouteRepository.xml
FIND_ALL = """
    SELECT
        r.route_no,
        r.basic_fare,
        a_dep.airport_cd AS dep_airport_cd,
        a_dep.airport_name AS dep_airport_name,
        a_arr.airport_cd AS arr_airport_cd,
        a_arr.airport_name AS arr_airport_name
    FROM
        route r,
        airport a_dep,
        airport a_arr
    WHERE
        r.dep_airport_cd = a_dep.airport_cd
    AND
        r.arr_airport_cd = a_arr.airport_cd
"""


class RouteRepository(BaseRepository):
    """Repository for Route entity operations."""

    async def find_all(self) -> list[Route]:
        """Find all routes with departure and arrival airports.
        
        Returns:
            List of all routes with airport information
        """
        rows = await self.fetch_all(FIND_ALL)
        return [self._row_to_route(row) for row in rows]

    def _row_to_route(self, row) -> Route:
        """Convert database row to Route model."""
        return Route(
            route_no=row["route_no"],
            basic_fare=row["basic_fare"],
            departure_airport=Airport(
                code=row["dep_airport_cd"],
                name=row["dep_airport_name"],
                display_order=None,
            ),
            arrival_airport=Airport(
                code=row["arr_airport_cd"],
                name=row["arr_airport_name"],
                display_order=None,
            ),
        )
