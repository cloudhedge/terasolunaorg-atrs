"""Reservation repository - 予約情報リポジトリ."""

from datetime import date
from typing import Any

from ..models import Passenger, Reservation, ReserveFlight
from ..models.enums import BoardingClassCd, FareTypeCd, Gender
from .base import BaseRepository


# SQL Queries - ported from ReservationRepository.xml

GET_NEXT_RESERVATION_ID = """
    SELECT TO_CHAR(NEXTVAL('sq_reservation_1'), 'FM0999999999')
"""

GET_NEXT_RESERVE_FLIGHT_ID = """
    SELECT NEXTVAL('sq_reserve_flight_1')
"""

GET_NEXT_PASSENGER_ID = """
    SELECT NEXTVAL('sq_passenger_1')
"""

INSERT_RESERVATION = """
    INSERT INTO reservation (
        reserve_no,
        reserve_date,
        total_fare,
        rep_family_name,
        rep_given_name,
        rep_age,
        rep_gender,
        rep_tel,
        rep_mail,
        rep_customer_no
    )
    VALUES (
        :reserve_no,
        :reserve_date,
        :total_fare,
        :rep_family_name,
        :rep_given_name,
        :rep_age,
        :rep_gender,
        :rep_tel,
        :rep_mail,
        NULLIF(:rep_customer_no, '')
    )
"""

INSERT_RESERVE_FLIGHT = """
    INSERT INTO reserve_flight (
        reserve_flight_no,
        reserve_no,
        departure_date,
        flight_name,
        boarding_class_cd,
        fare_type_cd
    )
    VALUES (
        :reserve_flight_no,
        :reserve_no,
        :departure_date,
        :flight_name,
        :boarding_class_cd,
        :fare_type_cd
    )
"""

INSERT_PASSENGER = """
    INSERT INTO passenger (
        passenger_no,
        reserve_flight_no,
        family_name,
        given_name,
        age,
        gender,
        customer_no
    )
    VALUES (
        :passenger_no,
        :reserve_flight_no,
        :family_name,
        :given_name,
        :age,
        :gender,
        NULLIF(:customer_no, '')
    )
"""

FIND_ALL_BY_MEMBERSHIP_NUMBER_FOR_REPORT = """
    SELECT
        r.reserve_no,
        r.reserve_date,
        r.total_fare,
        rf.reserve_flight_no,
        rf.departure_date,
        rf.flight_name
    FROM
        reservation r
    JOIN
        reserve_flight rf
    ON
        rf.reserve_no = r.reserve_no
    WHERE
        r.rep_customer_no = :membership_number
    ORDER BY
        r.reserve_no,
        rf.reserve_flight_no
"""


class ReservationRepository(BaseRepository):
    """Repository for Reservation entity operations."""

    async def get_next_reservation_id(self) -> str:
        """Get next reservation ID from sequence.
        
        Returns:
            10-digit formatted reservation number
        """
        result = await self.fetch_one(GET_NEXT_RESERVATION_ID)
        return result[0]

    async def get_next_reserve_flight_id(self) -> int:
        """Get next reserve flight ID from sequence.
        
        Returns:
            Integer reserve flight ID
        """
        result = await self.fetch_one(GET_NEXT_RESERVE_FLIGHT_ID)
        return result[0]

    async def get_next_passenger_id(self) -> int:
        """Get next passenger ID from sequence.
        
        Returns:
            Integer passenger ID
        """
        result = await self.fetch_one(GET_NEXT_PASSENGER_ID)
        return result[0]

    async def insert(self, reservation: Reservation) -> str:
        """Insert a new reservation.
        
        Args:
            reservation: Reservation to insert
            
        Returns:
            Generated reservation number
        """
        reserve_no = await self.get_next_reservation_id()
        rep_customer_no = ""
        if reservation.rep_member:
            rep_customer_no = reservation.rep_member.membership_number

        await self.execute(
            INSERT_RESERVATION,
            {
                "reserve_no": reserve_no,
                "reserve_date": reservation.reserve_date,
                "total_fare": reservation.total_fare,
                "rep_family_name": reservation.rep_family_name,
                "rep_given_name": reservation.rep_given_name,
                "rep_age": reservation.rep_age,
                "rep_gender": reservation.rep_gender.value,
                "rep_tel": reservation.rep_tel,
                "rep_mail": reservation.rep_mail,
                "rep_customer_no": rep_customer_no,
            },
        )
        return reserve_no

    async def insert_reserve_flight(
        self,
        reserve_no: str,
        departure_date: date,
        flight_name: str,
        boarding_class_cd: BoardingClassCd,
        fare_type_cd: FareTypeCd,
    ) -> int:
        """Insert a reserve flight record.
        
        Args:
            reserve_no: Parent reservation number
            departure_date: Flight date
            flight_name: Flight identifier
            boarding_class_cd: Boarding class
            fare_type_cd: Fare type
            
        Returns:
            Generated reserve flight ID
        """
        reserve_flight_no = await self.get_next_reserve_flight_id()
        await self.execute(
            INSERT_RESERVE_FLIGHT,
            {
                "reserve_flight_no": reserve_flight_no,
                "reserve_no": reserve_no,
                "departure_date": departure_date,
                "flight_name": flight_name,
                "boarding_class_cd": boarding_class_cd.value,
                "fare_type_cd": fare_type_cd.value,
            },
        )
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
        """Insert a passenger record.
        
        Args:
            reserve_flight_no: Parent reserve flight ID
            family_name: Passenger's family name
            given_name: Passenger's given name
            age: Passenger's age
            gender: Passenger's gender
            customer_no: Member ID if passenger is registered member
            
        Returns:
            Generated passenger ID
        """
        passenger_no = await self.get_next_passenger_id()
        await self.execute(
            INSERT_PASSENGER,
            {
                "passenger_no": passenger_no,
                "reserve_flight_no": reserve_flight_no,
                "family_name": family_name,
                "given_name": given_name,
                "age": age,
                "gender": gender.value,
                "customer_no": customer_no or "",
            },
        )
        return passenger_no

    async def find_all_by_membership_number_for_report(
        self, membership_number: str
    ) -> list[dict[str, Any]]:
        """Find all reservations for a member for reporting.
        
        Args:
            membership_number: Member's unique ID
            
        Returns:
            List of reservation data with flight details
        """
        return await self.fetch_all(
            FIND_ALL_BY_MEMBERSHIP_NUMBER_FOR_REPORT,
            {"membership_number": membership_number},
        )
