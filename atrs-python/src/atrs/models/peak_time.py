"""Peak time model.

ピーク時期情報 - Peak Time Information.
"""

from datetime import date

from pydantic import BaseModel, Field


class PeakTime(BaseModel):
    """Peak time entity.
    
    Represents a peak travel period with pricing multiplier.
    
    Attributes:
        peak_time_cd: Peak time code
        peak_start_date: Start date of peak period
        peak_end_date: End date of peak period
        multiplication_ratio: Price multiplication ratio (e.g., 150 = 150%)
    """
    peak_time_cd: str = Field(max_length=10, description="Peak time code")
    peak_start_date: date = Field(description="Peak period start date")
    peak_end_date: date = Field(description="Peak period end date")
    multiplication_ratio: int = Field(ge=100, description="Price multiplication ratio (%)")

    class Config:
        """Pydantic model configuration."""
        from_attributes = True
