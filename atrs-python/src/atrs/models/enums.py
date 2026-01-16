"""Enumeration types for ATRS domain models.

Java enums mapped to Python str Enums for database compatibility.
"""

from enum import Enum


class Gender(str, Enum):
    """性別 - Gender enumeration.
    
    Values:
        F: Female (女性)
        M: Male (男性)
    """
    F = "F"
    M = "M"

    @property
    def label(self) -> str:
        """Get display label for gender."""
        return {"F": "Female", "M": "Male"}[self.value]


class BoardingClassCd(str, Enum):
    """搭乗クラスコード - Boarding class code enumeration.
    
    Values:
        N: Normal/Economy seat (一般席)
        S: Special/Business seat (特別席)
    """
    N = "N"
    S = "S"

    @property
    def label(self) -> str:
        """Get display label for boarding class."""
        return {"N": "Normal", "S": "Special"}[self.value]


class FareTypeCd(str, Enum):
    """運賃種別コード - Fare type code enumeration.
    
    Values:
        OW: One Way (片道運賃)
        RT: Round Trip (往復運賃)
        RD1: Reservation Discount 1 day (予約割1)
        RD7: Reservation Discount 7 days (予約割7)
        ED: Early Discount (早期割)
        LD: Ladies Discount (レディース割)
        GD: Group Discount (グループ割)
        SOW: Special One Way (特別片道運賃)
        SRT: Special Round Trip (特別往復運賃)
        SRD: Special Reservation Discount (特別予約割)
    """
    OW = "OW"
    RT = "RT"
    RD1 = "RD1"
    RD7 = "RD7"
    ED = "ED"
    LD = "LD"
    GD = "GD"
    SOW = "SOW"
    SRT = "SRT"
    SRD = "SRD"


class FlightType(str, Enum):
    """フライト種別 - Flight type enumeration.
    
    Values:
        RT: Round Trip (往復)
        OW: One Way (片道)
    """
    RT = "RT"
    OW = "OW"

    @property
    def label(self) -> str:
        """Get display label for flight type."""
        return {"RT": "Round Trip", "OW": "One Way"}[self.value]
