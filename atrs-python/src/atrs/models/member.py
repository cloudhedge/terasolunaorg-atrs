"""Member model.

カード会員情報 - Card Member Information.
"""

from datetime import date

from pydantic import BaseModel, EmailStr, Field, field_validator

from .credit_type import CreditType
from .enums import Gender
from .member_login import MemberLogin


class Member(BaseModel):
    """Member entity.
    
    Represents a registered member/customer.
    
    Attributes:
        membership_number: Unique member ID (10 digits)
        kanji_family_name: Family name in Kanji
        kanji_given_name: Given name in Kanji
        kana_family_name: Family name in Katakana
        kana_given_name: Given name in Katakana
        birthday: Date of birth
        gender: Gender (M/F)
        tel: Telephone number
        zip_code: Postal code
        address: Address
        mail: Email address
        credit_no: Credit card number (masked)
        credit_term: Credit card expiration (MM/YY)
        credit_type: Credit card type
        member_login: Login information
    """
    membership_number: str = Field(
        min_length=10, max_length=10, description="Membership number (10 digits)"
    )
    kanji_family_name: str = Field(max_length=20, description="Family name in Kanji")
    kanji_given_name: str = Field(max_length=20, description="Given name in Kanji")
    kana_family_name: str = Field(max_length=40, description="Family name in Katakana")
    kana_given_name: str = Field(max_length=40, description="Given name in Katakana")
    birthday: date = Field(description="Date of birth")
    gender: Gender = Field(description="Gender")
    tel: str = Field(max_length=15, description="Telephone number")
    zip_code: str = Field(max_length=10, description="Postal code")
    address: str = Field(max_length=100, description="Address")
    mail: EmailStr = Field(description="Email address")
    credit_no: str = Field(max_length=20, description="Credit card number")
    credit_term: str = Field(max_length=5, description="Credit card expiration")
    credit_type: CreditType = Field(description="Credit card type")
    member_login: MemberLogin | None = Field(default=None, description="Login information")

    @field_validator("birthday")
    @classmethod
    def birthday_must_be_past(cls, v: date) -> date:
        """Validate that birthday is in the past."""
        if v >= date.today():
            raise ValueError("Birthday must be in the past")
        return v

    class Config:
        """Pydantic model configuration."""
        from_attributes = True

    @property
    def full_name_kanji(self) -> str:
        """Get full name in Kanji."""
        return f"{self.kanji_family_name} {self.kanji_given_name}"

    @property
    def full_name_kana(self) -> str:
        """Get full name in Katakana."""
        return f"{self.kana_family_name} {self.kana_given_name}"
