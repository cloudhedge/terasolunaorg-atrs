"""Member login model.

カード会員ログイン情報 - Member Login Information.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class MemberLogin(BaseModel):
    """Member login entity.
    
    Represents member authentication and login status.
    
    Attributes:
        password: Hashed password
        last_password: Previous hashed password
        login_date_time: Last login timestamp
        login_flg: Whether member is currently logged in
    """
    password: str = Field(description="Hashed password")
    last_password: str | None = Field(default=None, description="Previous hashed password")
    login_date_time: datetime | None = Field(default=None, description="Last login timestamp")
    login_flg: bool = Field(default=False, description="Login status flag")

    class Config:
        """Pydantic model configuration."""
        from_attributes = True
