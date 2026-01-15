"""Authentication service for login/logout"""

from dataclasses import dataclass
from datetime import datetime
from databases import Database

from ...models import Member
from ...repositories import MemberRepository
from ...core.security import verify_password, create_access_token


@dataclass
class LoginResult:
    """Result of successful login"""
    member: Member
    access_token: str
    token_type: str = "bearer"


class AuthService:
    """Service for authentication operations"""

    def __init__(self, database: Database):
        self._db = database
        self._member_repo = MemberRepository(database)

    async def authenticate(
        self, membership_number: str, password: str
    ) -> LoginResult | None:
        """
        Authenticate a member by membership number and password.

        Returns LoginResult on success, None on failure.
        """
        # Validate input length (membership number must be 10 chars)
        if len(membership_number) != 10:
            return None

        # Validate password length (8-20 chars)
        if len(password) < 8 or len(password) > 20:
            return None

        # Find member
        member = await self._member_repo.find_one_for_login(membership_number)
        if not member or not member.member_login:
            return None

        # Verify password
        if not verify_password(password, member.member_login.password):
            return None

        # Update login status
        await self._member_repo.update_to_login_status(
            membership_number=membership_number,
            login_date_time=datetime.now(),
            login_flg=True,
        )

        # Create access token
        access_token = create_access_token(
            data={"sub": membership_number}
        )

        return LoginResult(
            member=member,
            access_token=access_token,
        )

    async def logout(self, membership_number: str) -> None:
        """Log out a member"""
        await self._member_repo.update_to_logout_status(membership_number)

    async def get_current_member(self, membership_number: str) -> Member | None:
        """Get full member details for authenticated user"""
        return await self._member_repo.find_one(membership_number)
