"""Authentication login service - 認証ログインサービス.

Ported from AuthLoginServiceImpl.java and AtrsUserDetailsService.java
"""

from datetime import datetime, timezone

from databases import Database

from ...core.exceptions import InvalidPasswordException, MemberNotFoundException
from ...core.security import create_access_token, hash_password, verify_password, Token
from ...models import Member
from ...repositories import MemberRepository


class AuthLoginService:
    """Service for authentication login operations.
    
    Handles member authentication and JWT token generation.
    """

    def __init__(self, db: Database):
        """Initialize service with database connection.
        
        Args:
            db: Database connection instance
        """
        self.db = db
        self.member_repo = MemberRepository(db)

    async def authenticate(self, membership_number: str, password: str) -> Token:
        """Authenticate member and return JWT token.
        
        Args:
            membership_number: Member's unique ID
            password: Plain text password
            
        Returns:
            Token with access_token
            
        Raises:
            MemberNotFoundException: If member not found
            InvalidPasswordException: If password is invalid
        """
        # Find member for login
        login_data = await self.member_repo.find_one_for_login(membership_number)
        if not login_data:
            raise MemberNotFoundException()

        # Verify password
        stored_password = login_data["password"]
        if not verify_password(password, stored_password):
            raise InvalidPasswordException()

        # Update login status
        await self.member_repo.update_to_login_status(
            membership_number=membership_number,
            login_date_time=datetime.now(timezone.utc),
            login_flg=True,
        )

        # Generate JWT token
        access_token = create_access_token(data={"sub": membership_number})
        return Token(access_token=access_token)

    async def get_member(self, membership_number: str) -> Member | None:
        """Get member by membership number.
        
        Args:
            membership_number: Member's unique ID
            
        Returns:
            Member if found, None otherwise
        """
        return await self.member_repo.find_one(membership_number)
