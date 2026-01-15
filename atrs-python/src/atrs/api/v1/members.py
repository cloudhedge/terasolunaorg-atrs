"""Member management API endpoints"""

from fastapi import APIRouter, HTTPException, status

from ...services.member import MemberService
from ...services.member.member_service import MemberRegistrationInput, MemberUpdateInput
from ...schemas.member import (
    MemberRegisterRequest,
    MemberUpdateRequest,
    MemberResponse,
    MemberRegisterResponse,
)
from ..deps import DatabaseDep, CurrentUserRequiredDep

router = APIRouter()


@router.post("/register", response_model=MemberRegisterResponse)
async def register_member(
    db: DatabaseDep,
    request: MemberRegisterRequest,
) -> MemberRegisterResponse:
    """Register a new member"""
    member_service = MemberService(db)

    input_data = MemberRegistrationInput(
        kanji_family_name=request.kanji_family_name,
        kanji_given_name=request.kanji_given_name,
        kana_family_name=request.kana_family_name,
        kana_given_name=request.kana_given_name,
        birthday=request.birthday,
        gender=request.gender,
        tel=request.tel,
        zip_code=request.zip_code,
        address=request.address,
        mail=request.mail,
        credit_no=request.credit_no,
        credit_type_cd=request.credit_type_cd,
        credit_term=request.credit_term,
        password=request.password,
    )

    try:
        membership_number = await member_service.register(input_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return MemberRegisterResponse(membership_number=membership_number)


@router.get("/me", response_model=MemberResponse)
async def get_current_member(
    current_user: CurrentUserRequiredDep,
) -> MemberResponse:
    """Get current authenticated member's profile"""
    return MemberResponse(
        membership_number=current_user.membership_number,
        kanji_family_name=current_user.kanji_family_name,
        kanji_given_name=current_user.kanji_given_name,
        kana_family_name=current_user.kana_family_name,
        kana_given_name=current_user.kana_given_name,
        birthday=current_user.birthday,
        gender=current_user.gender,
        tel=current_user.tel,
        zip_code=current_user.zip_code,
        address=current_user.address,
        mail=current_user.mail,
    )


@router.put("/me", response_model=MemberResponse)
async def update_current_member(
    db: DatabaseDep,
    current_user: CurrentUserRequiredDep,
    request: MemberUpdateRequest,
) -> MemberResponse:
    """Update current authenticated member's profile"""
    member_service = MemberService(db)

    input_data = MemberUpdateInput(
        kanji_family_name=request.kanji_family_name,
        kanji_given_name=request.kanji_given_name,
        kana_family_name=request.kana_family_name,
        kana_given_name=request.kana_given_name,
        birthday=request.birthday,
        gender=request.gender,
        tel=request.tel,
        zip_code=request.zip_code,
        address=request.address,
        mail=request.mail,
        credit_no=request.credit_no,
        credit_type_cd=request.credit_type_cd,
        credit_term=request.credit_term,
        new_password=request.new_password,
    )

    try:
        await member_service.update(current_user.membership_number, input_data)
        # Get updated member
        updated_member = await member_service.get_member(current_user.membership_number)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return MemberResponse(
        membership_number=updated_member.membership_number,
        kanji_family_name=updated_member.kanji_family_name,
        kanji_given_name=updated_member.kanji_given_name,
        kana_family_name=updated_member.kana_family_name,
        kana_given_name=updated_member.kana_given_name,
        birthday=updated_member.birthday,
        gender=updated_member.gender,
        tel=updated_member.tel,
        zip_code=updated_member.zip_code,
        address=updated_member.address,
        mail=updated_member.mail,
    )


@router.get("/{membership_number}/exists")
async def check_member_exists(
    db: DatabaseDep,
    membership_number: str,
) -> dict:
    """Check if a member exists (for availability check)"""
    member_service = MemberService(db)
    exists = await member_service.check_member_exists(membership_number)
    return {"exists": exists}
