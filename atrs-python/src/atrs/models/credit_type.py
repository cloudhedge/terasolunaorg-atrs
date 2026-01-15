"""Credit type model.

クレジットカード種別情報 - Credit Card Type Information.
"""

from pydantic import BaseModel, Field


class CreditType(BaseModel):
    """Credit card type entity.
    
    Represents a credit card type/brand.
    
    Attributes:
        credit_type_cd: Credit type code (e.g., 'VISA', 'MASTER')
        credit_firm: Credit card company/firm name
    """
    credit_type_cd: str = Field(max_length=10, description="Credit type code")
    credit_firm: str = Field(max_length=50, description="Credit card company name")

    class Config:
        """Pydantic model configuration."""
        from_attributes = True
