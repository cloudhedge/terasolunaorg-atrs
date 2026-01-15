"""Member repository for data access"""

from datetime import datetime

from .base import BaseRepository
from .sql import member as sql
from ..models import Member, MemberLogin, CreditType


class MemberRepository(BaseRepository):
    """Repository for member data access"""

    async def find_one_for_login(self, membership_number: str) -> Member | None:
        """Find member with login info for authentication"""
        row = await self.fetch_one(sql.FIND_ONE_FOR_LOGIN, {
            "membership_number": membership_number
        })
        if not row:
            return None

        return Member(
            customer_no=row["customer_no"],
            kanji_family_name=row["kanji_family_name"],
            kanji_given_name=row["kanji_given_name"],
            kana_family_name="",  # Not loaded in login query
            kana_given_name="",
            birthday=datetime.now().date(),  # Placeholder
            gender="M",
            tel="",
            zip_code="",
            address="",
            mail="placeholder@example.com",
            credit_no="",
            credit_term="",
            credit_type_cd="",
            member_login=MemberLogin(
                customer_no=row["customer_no"],
                password=row["password"],
                last_password=row["last_password"],
                login_date_time=row["login_date_time"],
                login_flg=row["login_flg"],
            ),
        )

    async def find_one(self, membership_number: str) -> Member | None:
        """Find member with full details"""
        row = await self.fetch_one(sql.FIND_ONE, {
            "membership_number": membership_number
        })
        if not row:
            return None

        return Member(
            customer_no=row["customer_no"],
            kanji_family_name=row["kanji_family_name"],
            kanji_given_name=row["kanji_given_name"],
            kana_family_name=row["kana_family_name"],
            kana_given_name=row["kana_given_name"],
            birthday=row["birthday"],
            gender=row["gender"],
            tel=row["tel"],
            zip_code=row["zip_code"],
            address=row["address"],
            mail=row["mail"],
            credit_no=row["credit_no"],
            credit_term=row["credit_term"],
            credit_type_cd=row["credit_type_cd"],
            credit_type=CreditType(
                credit_type_cd=row["credit_type_cd"],
                credit_firm=row["credit_firm"],
                display_order=0,
            ),
            member_login=MemberLogin(
                customer_no=row["customer_no"],
                password=row["password"],
                last_password=row["last_password"],
                login_date_time=row["login_date_time"],
                login_flg=row["login_flg"],
            ),
        )

    async def update_to_login_status(
        self, membership_number: str, login_date_time: datetime, login_flg: bool
    ) -> None:
        """Update login status after successful authentication"""
        await self.execute(sql.UPDATE_TO_LOGIN_STATUS, {
            "membership_number": membership_number,
            "login_date_time": login_date_time,
            "login_flg": login_flg,
        })

    async def update_to_logout_status(self, membership_number: str) -> None:
        """Update login status on logout"""
        await self.execute(sql.UPDATE_TO_LOGOUT_STATUS, {
            "membership_number": membership_number,
            "login_flg": False,
        })

    async def get_next_member_number(self) -> str:
        """Generate next membership number from sequence"""
        row = await self.fetch_one(sql.GET_NEXT_MEMBER_NUMBER)
        return row["to_char"]

    async def insert(self, member: Member) -> str:
        """Insert new member and return membership number"""
        customer_no = await self.get_next_member_number()

        await self.execute(sql.INSERT_MEMBER, {
            "customer_no": customer_no,
            "kanji_family_name": member.kanji_family_name,
            "kanji_given_name": member.kanji_given_name,
            "kana_family_name": member.kana_family_name,
            "kana_given_name": member.kana_given_name,
            "birthday": member.birthday,
            "gender": member.gender.value,
            "tel": member.tel,
            "zip_code": member.zip_code,
            "address": member.address,
            "mail": member.mail,
            "credit_no": member.credit_no,
            "credit_type_cd": member.credit_type_cd,
            "credit_term": member.credit_term,
        })

        return customer_no

    async def insert_member_login(self, customer_no: str, password: str) -> None:
        """Insert member login record"""
        await self.execute(sql.INSERT_MEMBER_LOGIN, {
            "customer_no": customer_no,
            "password": password,
            "last_password": None,
            "login_flg": False,
        })

    async def update(self, member: Member) -> None:
        """Update member information"""
        await self.execute(sql.UPDATE_MEMBER, {
            "customer_no": member.membership_number,
            "kanji_family_name": member.kanji_family_name,
            "kanji_given_name": member.kanji_given_name,
            "kana_family_name": member.kana_family_name,
            "kana_given_name": member.kana_given_name,
            "birthday": member.birthday,
            "gender": member.gender.value,
            "tel": member.tel,
            "zip_code": member.zip_code,
            "address": member.address,
            "mail": member.mail,
            "credit_no": member.credit_no,
            "credit_type_cd": member.credit_type_cd,
            "credit_term": member.credit_term,
        })

    async def update_member_login_password(
        self, customer_no: str, new_password: str
    ) -> None:
        """Update member password (moves current to last_password)"""
        await self.execute(sql.UPDATE_MEMBER_LOGIN_PASSWORD, {
            "customer_no": customer_no,
            "password": new_password,
        })
