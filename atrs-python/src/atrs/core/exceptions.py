"""Custom exceptions for ATRS application.

Ported from Java exception classes.
"""


class AtrsException(Exception):
    """Base exception for ATRS application.
    
    All business exceptions should inherit from this class.
    
    Attributes:
        code: Error code for identification
        message: Human-readable error message
    """

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


# Authentication Exceptions (a1)

class AuthLoginException(AtrsException):
    """Base exception for authentication errors."""
    pass


class MemberNotFoundException(AuthLoginException):
    """Member not found during login."""

    def __init__(self):
        super().__init__("E_AR_A1_2001", "Member not found")


class InvalidPasswordException(AuthLoginException):
    """Invalid password during login."""

    def __init__(self):
        super().__init__("E_AR_A1_2002", "Invalid password")


class AccountLockedException(AuthLoginException):
    """Account is locked due to too many failed attempts."""

    def __init__(self):
        super().__init__("E_AR_A1_2003", "Account is locked")


# Ticket Search Exceptions (b1)

class TicketSearchException(AtrsException):
    """Base exception for ticket search errors."""
    pass


class FlightNotFoundException(TicketSearchException):
    """No flights found matching search criteria."""

    def __init__(self):
        super().__init__("E_AR_B1_2001", "No flights found")


class InvalidSearchCriteriaException(TicketSearchException):
    """Invalid search criteria provided."""

    def __init__(self, detail: str = "Invalid search criteria"):
        super().__init__("E_AR_B1_2002", detail)


# Ticket Reservation Exceptions (b2)

class TicketReserveException(AtrsException):
    """Base exception for ticket reservation errors."""
    pass


class InsufficientSeatsException(TicketReserveException):
    """Not enough vacant seats for reservation."""

    def __init__(self):
        super().__init__("E_AR_B2_2001", "Insufficient seats available")


class InvalidFlightException(TicketReserveException):
    """Flight is invalid for reservation."""

    def __init__(self, detail: str = "Invalid flight"):
        super().__init__("E_AR_B2_2002", detail)


class InvalidPassengerException(TicketReserveException):
    """Passenger information is invalid."""

    def __init__(self, detail: str = "Invalid passenger information"):
        super().__init__("E_AR_B2_2003", detail)


class FareTypeNotAvailableException(TicketReserveException):
    """Fare type is not available for the selected date."""

    def __init__(self):
        super().__init__("E_AR_B2_2004", "Fare type not available for this date")


# Member Exceptions (c1, c2)

class MemberException(AtrsException):
    """Base exception for member-related errors."""
    pass


class MemberAlreadyExistsException(MemberException):
    """Member with same email already exists."""

    def __init__(self):
        super().__init__("E_AR_C1_2001", "Member already exists")


class PasswordMismatchException(MemberException):
    """Password and confirmation do not match."""

    def __init__(self):
        super().__init__("E_AR_C1_2002", "Passwords do not match")


class SamePasswordException(MemberException):
    """New password is same as current password."""

    def __init__(self):
        super().__init__("E_AR_C2_2001", "New password must be different from current")


# System Exceptions

class SystemException(AtrsException):
    """System-level exception for unexpected errors."""

    def __init__(self, detail: str = "System error"):
        super().__init__("E_AR_SYS_001", detail)


class DatabaseException(SystemException):
    """Database operation failed."""

    def __init__(self, detail: str = "Database error"):
        super().__init__(f"Database error: {detail}")
