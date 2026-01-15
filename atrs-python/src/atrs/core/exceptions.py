"""Custom exceptions for ATRS"""

from enum import Enum


class ErrorCode(str, Enum):
    """Error codes for business exceptions"""
    # Search errors
    E_AR_B1_2001 = "E_AR_B1_2001"  # Departure date out of range
    E_AR_B1_2002 = "E_AR_B1_2002"  # Route not found

    # Reserve errors
    E_AR_B2_2001 = "E_AR_B2_2001"  # Return flight outside boarding range
    E_AR_B2_2002 = "E_AR_B2_2002"  # Representative member not found
    E_AR_B2_2003 = "E_AR_B2_2003"  # Representative info mismatch
    E_AR_B2_2004 = "E_AR_B2_2004"  # Representative age too young
    E_AR_B2_2005 = "E_AR_B2_2005"  # Passenger member not found
    E_AR_B2_2006 = "E_AR_B2_2006"  # Passenger info mismatch
    E_AR_B2_2007 = "E_AR_B2_2007"  # Ladies discount with male passenger
    E_AR_B2_2008 = "E_AR_B2_2008"  # Fare type not available
    E_AR_B2_2009 = "E_AR_B2_2009"  # Insufficient vacant seats
    E_AR_B2_2010 = "E_AR_B2_2010"  # Group discount passenger minimum not met

    # Member errors
    E_AR_C1_2001 = "E_AR_C1_2001"  # Member registration failed


ERROR_MESSAGES = {
    ErrorCode.E_AR_B1_2001: "Departure date must be between today and {limit_days} days ahead",
    ErrorCode.E_AR_B1_2002: "No route found for the specified airports",
    ErrorCode.E_AR_B2_2001: "Return flight departure must be at least {interval} minutes after outward arrival",
    ErrorCode.E_AR_B2_2002: "Representative member not found",
    ErrorCode.E_AR_B2_2003: "Representative information does not match member records",
    ErrorCode.E_AR_B2_2004: "Representative must be at least {min_age} years old",
    ErrorCode.E_AR_B2_2005: "Passenger {position} member not found",
    ErrorCode.E_AR_B2_2006: "Passenger {position} information does not match member records",
    ErrorCode.E_AR_B2_2007: "Ladies discount fare requires all female passengers",
    ErrorCode.E_AR_B2_2008: "Selected fare type is not available for this booking period",
    ErrorCode.E_AR_B2_2009: "Insufficient vacant seats for this flight",
    ErrorCode.E_AR_B2_2010: "{fare_type} requires at least {min_passengers} passengers",
}


class AtrsException(Exception):
    """Base exception for ATRS"""
    pass


class AtrsBusinessException(AtrsException):
    """Business logic exception with error code"""

    def __init__(self, error_code: ErrorCode, **kwargs):
        self.error_code = error_code
        self.details = kwargs
        message = ERROR_MESSAGES.get(error_code, str(error_code))
        if kwargs:
            message = message.format(**kwargs)
        super().__init__(message)


class FlightNotFoundException(AtrsException):
    """No flights found matching search criteria"""

    def __init__(self, message: str = "No flights found matching the search criteria"):
        super().__init__(message)


class InvalidFlightException(AtrsException):
    """Flight data is invalid or inconsistent"""

    def __init__(self, message: str = "Invalid flight data"):
        super().__init__(message)
