"""Membership shared service - 会員情報共有サービス.

Ported from MembershipSharedServiceImpl.java
"""

from databases import Database

from ...repositories import MemberRepository


class MembershipSharedService:
    """Shared service for membership-related operations.
    
    Provides common membership functionality used across services.
    """

    def __init__(self, db: Database):
        """Initialize service with database connection.
        
        Args:
            db: Database connection instance
        """
        self.db = db
        self.member_repo = MemberRepository(db)

    async def is_member(self, membership_number: str) -> bool:
        """Check if a membership number exists.
        
        Args:
            membership_number: Member's unique ID
            
        Returns:
            True if member exists
        """
        member = await self.member_repo.find_one(membership_number)
        return member is not None
