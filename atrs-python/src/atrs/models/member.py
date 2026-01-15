"""Member-related domain models"""

from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr

from .enums import Gender


class CreditType(BaseModel):
    """Credit card type reference data"""
    credit_type_cd: str = Field(max_length=3)
    credit_firm: str = Field(max_length=80)
    display_order: int


class MemberLogin(BaseModel):
    """Member login credentials and status"""
    customer_no: str = Field(max_length=10)
    password: str = Field(max_length=124)
    last_password: str | None = Field(default=None, max_length=124)
    login_date_time: datetime | None = None
    login_flg: bool = False


class Member(BaseModel):
    """Card member information"""
    membership_number: str = Field(max_length=10, alias="customer_no")
    kanji_family_name: str = Field(max_length=10)
    kanji_given_name: str = Field(max_length=10)
    kana_family_name: str = Field(max_length=10)
    kana_given_name: str = Field(max_length=10)
    birthday: date
    gender: Gender
    tel: str = Field(max_length=13)
    zip_code: str = Field(max_length=7)
    address: str = Field(max_length=60)
    mail: EmailStr
    credit_no: str = Field(max_length=16)
    credit_term: str = Field(max_length=5)
    credit_type_cd: str = Field(max_length=3)

    # Related objects (populated by repository)
    credit_type: CreditType | None = None
    member_login: MemberLogin | None = None

    class Config:
        populate_by_name = True
