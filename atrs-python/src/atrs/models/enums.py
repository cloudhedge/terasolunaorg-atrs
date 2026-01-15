"""Enumeration types for ATRS domain"""

from enum import Enum


class Gender(str, Enum):
    """Gender enumeration (M=Male, F=Female)"""
    M = "M"
    F = "F"


class FareTypeCd(str, Enum):
    """Fare type codes"""
    OW = "OW"    # One-way
    RT = "RT"    # Round-trip
    RD1 = "RD1"  # Advance discount 1 day
    RD7 = "RD7"  # Advance discount 7 days
    ED = "ED"    # Early bird discount
    LD = "LD"    # Ladies discount
    GD = "GD"    # Group discount
    SOW = "SOW"  # Special one-way
    SRT = "SRT"  # Special round-trip
    SRD = "SRD"  # Special advance discount


class BoardingClassCd(str, Enum):
    """Boarding class codes"""
    N = "N"  # Normal/Economy
    S = "S"  # Special/Business


class FlightType(str, Enum):
    """Flight type (one-way or round-trip)"""
    OW = "OW"  # One-way
    RT = "RT"  # Round-trip
