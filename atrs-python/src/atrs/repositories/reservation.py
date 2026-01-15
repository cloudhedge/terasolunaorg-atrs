"""Reservation repository for data access"""

from datetime import date

from .base import BaseRepository
from .sql import reservation as sql
from ..models import Reservation, ReserveFlight, Passenger, ReservationSummary, Gender


class ReservationRepository(BaseRepository):
    """Repository for reservation data access"""

    async def get_next_reserve_no(self) -> str:
        """Generate next reservation number from sequence"""
        row = await self.fetch_one(sql.GET_NEXT_RESERVE_NO)
        return row["to_char"]

    async def get_next_reserve_flight_no(self) -> int:
        """Generate next reserve flight number from sequence"""
        row = await self.fetch_one(sql.GET_NEXT_RESERVE_FLIGHT_NO)
        return row["nextval"]

    async def get_next_passenger_no(self) -> int:
        """Generate next passenger number from sequence"""
        row = await self.fetch_one(sql.GET_NEXT_PASSENGER_NO)
        return row["nextval"]

    async def insert(self, reservation: Reservation) -> str:
        """Insert reservation and return reservation number"""
        reserve_no = await self.get_next_reserve_no()

        await self.execute(sql.INSERT_RESERVATION, {
            "reserve_no": reserve_no,
            "reserve_date": reservation.reserve_date,
            "total_fare": reservation.total_fare,
            "rep_family_name": reservation.rep_family_name,
            "rep_given_name": reservation.rep_given_name,
            "rep_age": reservation.rep_age,
            "rep_gender": reservation.rep_gender.value,
            "rep_tel": reservation.rep_tel,
            "rep_mail": reservation.rep_mail,
            "rep_customer_no": reservation.rep_customer_no or "",
        })

        return reserve_no

    async def insert_reserve_flight(
        self,
        reserve_no: str,
        departure_date: date,
        flight_name: str,
        boarding_class_cd: str,
        fare_type_cd: str,
    ) -> int:
        """Insert reserve flight and return reserve flight number"""
        reserve_flight_no = await self.get_next_reserve_flight_no()

        await self.execute(sql.INSERT_RESERVE_FLIGHT, {
            "reserve_flight_no": reserve_flight_no,
            "reserve_no": reserve_no,
            "departure_date": departure_date,
            "flight_name": flight_name,
            "boarding_class_cd": boarding_class_cd,
            "fare_type_cd": fare_type_cd,
        })

        return reserve_flight_no

    async def insert_passenger(
        self,
        reserve_flight_no: int,
        family_name: str,
        given_name: str,
        age: int,
        gender: Gender,
        customer_no: str | None = None,
    ) -> int:
        """Insert passenger and return passenger number"""
        passenger_no = await self.get_next_passenger_no()

        await self.execute(sql.INSERT_PASSENGER, {
            "passenger_no": passenger_no,
            "reserve_flight_no": reserve_flight_no,
            "family_name": family_name,
            "given_name": given_name,
            "age": age,
            "gender": gender.value,
            "customer_no": customer_no or "",
        })

        return passenger_no

    async def find_all_by_membership_number_for_report(
        self, membership_number: str
    ) -> list[ReservationSummary]:
        """Get reservation history for a member (for CSV report)"""
        rows = await self.fetch_all(
            sql.FIND_ALL_BY_MEMBERSHIP_NUMBER_FOR_REPORT,
            {"membership_number": membership_number}
        )

        return [
            ReservationSummary(
                reserve_no=row["reserve_no"],
                reserve_date=row["reserve_date"],
                total_fare=row["total_fare"],
                rep_family_name=row["rep_family_name"],
                rep_given_name=row["rep_given_name"],
                departure_date=row["departure_date"],
                flight_name=row["flight_name"],
                dep_airport_name=row["dep_airport_name"],
                arr_airport_name=row["arr_airport_name"],
            )
            for row in rows
        ]
