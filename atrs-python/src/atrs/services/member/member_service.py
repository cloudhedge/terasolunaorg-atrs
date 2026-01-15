"""Member registration and update service"""

from dataclasses import dataclass
from datetime import date
from databases import Database

from ...models import Member, Gender
from ...repositories import MemberRepository
from ...core.security import get_password_hash


@dataclass
class MemberRegistrationInput:
    """Input data for member registration"""
    kanji_family_name: str
    kanji_given_name: str
    kana_family_name: str
    kana_given_name: str
    birthday: date
    gender: Gender
    tel: str
    zip_code: str
    address: str
    mail: str
    credit_no: str
    credit_type_cd: str
    credit_term: str
    password: str


@dataclass
class MemberUpdateInput:
    """Input data for member update"""
    kanji_family_name: str
    kanji_given_name: str
    kana_family_name: str
    kana_given_name: str
    birthday: date
    gender: Gender
    tel: str
    zip_code: str
    address: str
    mail: str
    credit_no: str
    credit_type_cd: str
    credit_term: str
    new_password: str | None = None  # Optional password change


class MemberService:
    """Service for member registration and updates"""

    def __init__(self, database: Database):
        self._db = database
        self._member_repo = MemberRepository(database)

    async def register(self, input_data: MemberRegistrationInput) -> str:
        """
        Register a new member.

        Returns the generated membership number.
        """
        # Create member model
        member = Member(
            customer_no="",  # Will be generated
            kanji_family_name=input_data.kanji_family_name,
            kanji_given_name=input_data.kanji_given_name,
            kana_family_name=input_data.kana_family_name,
            kana_given_name=input_data.kana_given_name,
            birthday=input_data.birthday,
            gender=input_data.gender,
            tel=input_data.tel,
            zip_code=input_data.zip_code,
            address=input_data.address,
            mail=input_data.mail,
            credit_no=input_data.credit_no,
            credit_type_cd=input_data.credit_type_cd,
            credit_term=input_data.credit_term,
        )

        # Insert member
        customer_no = await self._member_repo.insert(member)

        # Hash password and insert login record
        hashed_password = get_password_hash(input_data.password)
        await self._member_repo.insert_member_login(customer_no, hashed_password)

        return customer_no

    async def update(self, membership_number: str, input_data: MemberUpdateInput) -> None:
        """Update member information"""
        # Get existing member
        member = await self._member_repo.find_one(membership_number)
        if not member:
            raise ValueError(f"Member not found: {membership_number}")

        # Update member data
        updated_member = Member(
            customer_no=membership_number,
            kanji_family_name=input_data.kanji_family_name,
            kanji_given_name=input_data.kanji_given_name,
            kana_family_name=input_data.kana_family_name,
            kana_given_name=input_data.kana_given_name,
            birthday=input_data.birthday,
            gender=input_data.gender,
            tel=input_data.tel,
            zip_code=input_data.zip_code,
            address=input_data.address,
            mail=input_data.mail,
            credit_no=input_data.credit_no,
            credit_type_cd=input_data.credit_type_cd,
            credit_term=input_data.credit_term,
        )

        await self._member_repo.update(updated_member)

        # Update password if provided
        if input_data.new_password:
            hashed_password = get_password_hash(input_data.new_password)
            await self._member_repo.update_member_login_password(
                membership_number, hashed_password
            )

    async def get_member(self, membership_number: str) -> Member | None:
        """Get member by membership number"""
        return await self._member_repo.find_one(membership_number)

    async def check_member_exists(self, membership_number: str) -> bool:
        """Check if member exists"""
        member = await self._member_repo.find_one(membership_number)
        return member is not None
