"""Boarding class model.

搭乗クラス情報 - Boarding Class Information.
"""

from pydantic import BaseModel, Field

from .enums import BoardingClassCd


class BoardingClass(BaseModel):
    """Boarding class entity.
    
    Represents a boarding class (Normal or Special) with its extra charge.
    
    Attributes:
        boarding_class_cd: Boarding class code (N=Normal, S=Special)
        boarding_class_name: Display name
        extra_charge: Additional charge for this class
    """
    boarding_class_cd: BoardingClassCd = Field(description="Boarding class code")
    boarding_class_name: str = Field(max_length=20, description="Boarding class name")
    extra_charge: int = Field(ge=0, description="Extra charge amount")

    class Config:
        """Pydantic model configuration."""
        from_attributes = True
