"""Member repository - カード会員リポジトリ."""

from datetime import datetime

from ..models import CreditType, Member, MemberLogin
from ..models.enums import Gender
from .base import BaseRepository


# SQL Queries - ported from MemberRepository.xml

FIND_ONE_FOR_LOGIN = """
    SELECT
        m.customer_no,
        m.kanji_family_name,
        m.kanji_given_name,
        m_l.password,
        m_l.last_password,
        m_l.login_date_time,
        m_l.login_flg
    FROM
        member m,
        member_login m_l
    WHERE
        m.customer_no = :membership_number
    AND
        m.customer_no = m_l.customer_no
"""

UPDATE_TO_LOGIN_STATUS = """
    UPDATE
        member_login
    SET
        login_date_time = :login_date_time,
        login_flg = :login_flg
    WHERE
        customer_no = :membership_number
"""

UPDATE_TO_LOGOUT_STATUS = """
    UPDATE
        member_login
    SET
        login_flg = :login_flg
    WHERE
        customer_no = :membership_number
"""

FIND_ONE = """
    SELECT
        m.customer_no,
        m.kanji_family_name,
        m.kanji_given_name,
        m.kana_family_name,
        m.kana_given_name,
        m.birthday,
        m.gender,
        m.tel,
        m.zip_code,
        m.address,
        m.mail,
        m.credit_no,
        m.credit_term,
        m_l.password,
        m_l.last_password,
        m_l.login_date_time,
        m_l.login_flg,
        c_t.credit_type_cd,
        c_t.credit_firm
    FROM
        member m,
        member_login m_l,
        credit_type c_t
    WHERE
        m.customer_no = :membership_number
    AND
        m.customer_no = m_l.customer_no
    AND
        m.credit_type_cd = c_t.credit_type_cd
"""

GET_NEXT_MEMBER_ID = """
    SELECT TO_CHAR(NEXTVAL('sq_member_1'), 'FM0999999999')
"""

INSERT_MEMBER = """
    INSERT INTO member (
        customer_no,
        kanji_family_name,
        kanji_given_name,
        kana_family_name,
        kana_given_name,
        birthday,
        gender,
        tel,
        zip_code,
        address,
        mail,
        credit_no,
        credit_type_cd,
        credit_term
    )
    VALUES (
        :membership_number,
        :kanji_family_name,
        :kanji_given_name,
        :kana_family_name,
        :kana_given_name,
        :birthday,
        :gender,
        :tel,
        :zip_code,
        :address,
        :mail,
        :credit_no,
        :credit_type_cd,
        :credit_term
    )
"""

INSERT_MEMBER_LOGIN = """
    INSERT INTO member_login (
        customer_no,
        password,
        last_password,
        login_flg
    )
    VALUES (
        :membership_number,
        :password,
        :last_password,
        :login_flg
    )
"""

UPDATE_MEMBER = """
    UPDATE member SET
        kanji_family_name = :kanji_family_name,
        kanji_given_name = :kanji_given_name,
        kana_family_name = :kana_family_name,
        kana_given_name = :kana_given_name,
        birthday = :birthday,
        gender = :gender,
        tel = :tel,
        zip_code = :zip_code,
        address = :address,
        mail = :mail,
        credit_no = :credit_no,
        credit_type_cd = :credit_type_cd,
        credit_term = :credit_term
    WHERE
        customer_no = :membership_number
"""

UPDATE_MEMBER_LOGIN = """
    UPDATE member_login SET
        last_password = password,
        password = :password
    WHERE
        customer_no = :membership_number
"""


class MemberRepository(BaseRepository):
    """Repository for Member entity operations."""

    async def find_one_for_login(self, membership_number: str) -> dict | None:
        """Find member for login authentication.
        
        Args:
            membership_number: Member's unique ID
            
        Returns:
            Dict with basic member info and credentials, or None
        """
        return await self.fetch_one(
            FIND_ONE_FOR_LOGIN, {"membership_number": membership_number}
        )

    async def update_to_login_status(
        self, membership_number: str, login_date_time: datetime, login_flg: bool = True
    ) -> None:
        """Update member login status.
        
        Args:
            membership_number: Member's unique ID
            login_date_time: Login timestamp
            login_flg: Login flag (default True)
        """
        await self.execute(
            UPDATE_TO_LOGIN_STATUS,
            {
                "membership_number": membership_number,
                "login_date_time": login_date_time,
                "login_flg": login_flg,
            },
        )

    async def update_to_logout_status(self, membership_number: str) -> None:
        """Update member logout status.
        
        Args:
            membership_number: Member's unique ID
        """
        await self.execute(
            UPDATE_TO_LOGOUT_STATUS,
            {"membership_number": membership_number, "login_flg": False},
        )

    async def find_one(self, membership_number: str) -> Member | None:
        """Find member by membership number with full details.
        
        Args:
            membership_number: Member's unique ID
            
        Returns:
            Member with all details including credit info, or None
        """
        row = await self.fetch_one(FIND_ONE, {"membership_number": membership_number})
        if not row:
            return None
        return self._row_to_member(row)

    async def get_next_member_id(self) -> str:
        """Get next member ID from sequence.
        
        Returns:
            10-digit formatted member ID
        """
        result = await self.fetch_one(GET_NEXT_MEMBER_ID)
        return result[0]

    async def insert(self, member: Member) -> str:
        """Insert a new member.
        
        Args:
            member: Member to insert
            
        Returns:
            Generated membership number
        """
        membership_number = await self.get_next_member_id()
        await self.execute(
            INSERT_MEMBER,
            {
                "membership_number": membership_number,
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
                "credit_type_cd": member.credit_type.credit_type_cd,
                "credit_term": member.credit_term,
            },
        )
        return membership_number

    async def insert_member_login(
        self, membership_number: str, password: str, last_password: str | None = None
    ) -> None:
        """Insert member login record.
        
        Args:
            membership_number: Member's unique ID
            password: Hashed password
            last_password: Previous password (optional)
        """
        await self.execute(
            INSERT_MEMBER_LOGIN,
            {
                "membership_number": membership_number,
                "password": password,
                "last_password": last_password,
                "login_flg": False,
            },
        )

    async def update(self, member: Member) -> None:
        """Update member information.
        
        Args:
            member: Member with updated information
        """
        await self.execute(
            UPDATE_MEMBER,
            {
                "membership_number": member.membership_number,
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
                "credit_type_cd": member.credit_type.credit_type_cd,
                "credit_term": member.credit_term,
            },
        )

    async def update_member_login(self, membership_number: str, password: str) -> None:
        """Update member password (saves old password to last_password).
        
        Args:
            membership_number: Member's unique ID
            password: New hashed password
        """
        await self.execute(
            UPDATE_MEMBER_LOGIN,
            {"membership_number": membership_number, "password": password},
        )

    def _row_to_member(self, row) -> Member:
        """Convert database row to Member model."""
        return Member(
            membership_number=row["customer_no"],
            kanji_family_name=row["kanji_family_name"],
            kanji_given_name=row["kanji_given_name"],
            kana_family_name=row["kana_family_name"],
            kana_given_name=row["kana_given_name"],
            birthday=row["birthday"],
            gender=Gender(row["gender"]),
            tel=row["tel"],
            zip_code=row["zip_code"],
            address=row["address"],
            mail=row["mail"],
            credit_no=row["credit_no"],
            credit_term=row["credit_term"],
            credit_type=CreditType(
                credit_type_cd=row["credit_type_cd"],
                credit_firm=row["credit_firm"],
            ),
            member_login=MemberLogin(
                password=row["password"],
                last_password=row["last_password"],
                login_date_time=row["login_date_time"],
                login_flg=row["login_flg"],
            ),
        )
