"""Airport model.

空港情報 - Airport Information.
"""

from pydantic import BaseModel, Field


class Airport(BaseModel):
    """Airport entity.
    
    Represents an airport with its code, name, and display order.
    
    Attributes:
        code: Airport code (e.g., 'HND', 'ITM')
        name: Airport name (e.g., '羽田空港')
        display_order: Order for display in lists
    """
    code: str = Field(max_length=3, description="Airport code")
    name: str = Field(max_length=50, description="Airport name")
    display_order: int | None = Field(default=None, description="Display order in lists")

    class Config:
        """Pydantic model configuration."""
        from_attributes = True
