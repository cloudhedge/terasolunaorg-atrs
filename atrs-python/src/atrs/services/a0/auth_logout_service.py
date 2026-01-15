"""Authentication logout service - 認証ログアウトサービス.

Ported from AuthLogoutServiceImpl.java
"""

from databases import Database

from ...repositories import MemberRepository


class AuthLogoutService:
    """Service for authentication logout operations."""

    def __init__(self, db: Database):
        """Initialize service with database connection.
        
        Args:
            db: Database connection instance
        """
        self.db = db
        self.member_repo = MemberRepository(db)

    async def logout(self, membership_number: str) -> None:
        """Logout member by updating login status.
        
        Args:
            membership_number: Member's unique ID
        """
        await self.member_repo.update_to_logout_status(membership_number)
