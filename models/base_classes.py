from enum import Enum


class RegistrationStatus(Enum):
    """Police registration status enumeration"""

    NEW = "NEW"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"
    PROGRESS = "PROGRESS"
    SCHEDULED = "SCHEDULED"
    CANCELED = "CANCELED"
    SENT_TO_CANCEL = "SENT_TO_CANCEL"
    NO_LOGIN_CRED = "NO_LOGIN_CRED"
    NOT_USED = "NOT_USED"
    RESTART = "RESTART"

    @classmethod
    def success_states(cls) -> list["RegistrationStatus"]:
        """Return states considered successful"""
        return [cls.COMPLETE, cls.NOT_USED]

    @classmethod
    def failed_states(cls) -> list["RegistrationStatus"]:
        """Return states considered failed"""
        return [cls.ERROR, cls.NO_LOGIN_CRED]

    @classmethod
    def pending_states(cls) -> list["RegistrationStatus"]:
        """Return states considered pending/in progress"""
        return [cls.NEW, cls.PROGRESS, cls.SCHEDULED]

    def is_success(self) -> bool:
        """Check if this status represents success"""
        return self in self.success_states()

    def is_failed(self) -> bool:
        """Check if this status represents failure"""
        return self in self.failed_states()

    def is_pending(self) -> bool:
        """Check if this status represents pending/in progress"""
        return self in self.pending_states()

    def is_no_login_cred(self) -> bool:
        """Check if this status represents no login credential"""
        return self == self.NO_LOGIN_CRED

    def is_not_used(self) -> bool:
        """Check if this status represents not used"""
        return self == self.NOT_USED

    def is_restart(self) -> bool:
        """Check if this status represents restart"""
        return self == self.RESTART


class BookingStatus(Enum):
    """Booking status enumeration"""

    NEW = "NEW"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"
    PROGRESS = "PROGRESS"

    def is_success(self) -> bool:
        """Check if this booking status represents success"""
        return self == self.COMPLETE

    def is_failed(self) -> bool:
        """Check if this booking status represents failure"""
        return self == self.ERROR

    def is_pending(self) -> bool:
        """Check if this booking status represents pending"""
        return self == self.NEW

    def is_in_progress(self) -> bool:
        """Check if this booking status represents in progress"""
        return self == self.PROGRESS


class CheckoutStatus(Enum):
    """Check-out status enumeration"""

    NEW = "NEW"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"
    SENT_TO_CANCEL = "SENT_TO_CANCEL"
    NOT_USED = "NOT_USED"
    SCHEDULED = "SCHEDULED"
    PROGRESS = "PROGRESS"

    def is_success(self) -> bool:
        """Check if this checkout status represents success"""
        return self == self.COMPLETE

    def is_failed(self) -> bool:
        """Check if this checkout status represents failure"""
        return self in [self.ERROR]

    def is_pending(self) -> bool:
        """Check if this checkout status represents pending"""
        return self == self.NEW

    def is_not_used(self) -> bool:
        """Check if this checkout status represents not used"""
        return self == self.NOT_USED

    def is_in_progress(self) -> bool:
        """Check if this checkout status represents in progress"""
        return self == self.PROGRESS
