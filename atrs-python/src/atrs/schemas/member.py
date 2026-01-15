"""Member schemas"""

from datetime import date
from pydantic import BaseModel, Field, EmailStr

from ..models.enums import Gender


class MemberRegisterRequest(BaseModel):
    """Member registration request"""
    kanji_family_name: str = Field(max_length=10)
    kanji_given_name: str = Field(max_length=10)
    kana_family_name: str = Field(max_length=10)
    kana_given_name: str = Field(max_length=10)
    birthday: date
    gender: Gender
    tel: str = Field(max_length=13)
    zip_code: str = Field(min_length=7, max_length=7)
    address: str = Field(max_length=60)
    mail: EmailStr
    credit_no: str = Field(min_length=16, max_length=16)
    credit_type_cd: str = Field(max_length=3)
    credit_term: str = Field(max_length=5)
    password: str = Field(min_length=8, max_length=20)


class MemberUpdateRequest(BaseModel):
    """Member update request"""
    kanji_family_name: str = Field(max_length=10)
    kanji_given_name: str = Field(max_length=10)
    kana_family_name: str = Field(max_length=10)
    kana_given_name: str = Field(max_length=10)
    birthday: date
    gender: Gender
    tel: str = Field(max_length=13)
    zip_code: str = Field(min_length=7, max_length=7)
    address: str = Field(max_length=60)
    mail: EmailStr
    credit_no: str = Field(min_length=16, max_length=16)
    credit_type_cd: str = Field(max_length=3)
    credit_term: str = Field(max_length=5)
    new_password: str | None = Field(default=None, min_length=8, max_length=20)


class MemberResponse(BaseModel):
    """Member response (excludes sensitive data)"""
    membership_number: str
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


class MemberRegisterResponse(BaseModel):
    """Member registration response"""
    membership_number: str
    message: str = "Registration successful"
