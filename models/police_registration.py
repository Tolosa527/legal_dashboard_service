"""
Police Registration Models

This module contains the PoliceRegistration model and related enums
based on the police_registrations database table.
"""

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime, date
from dataclasses import dataclass
from uuid import UUID


class RegistrationStatus(Enum):
    """Police registration status enumeration"""

    NEW = "NEW"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"
    PROGRESS = "PROGRESS"
    SCHEDULED = "SCHEDULED"
    CANCELED = "CANCELED"
    SENT_TO_CANCEL = "SENT_TO_CANCEL"

    @classmethod
    def success_states(cls) -> list["RegistrationStatus"]:
        """Return states considered successful"""
        return [cls.COMPLETE]

    @classmethod
    def failed_states(cls) -> list["RegistrationStatus"]:
        """Return states considered failed"""
        return [cls.ERROR]

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


class BookingStatus(Enum):
    """Booking status enumeration"""

    NEW = "NEW"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"

    def is_success(self) -> bool:
        """Check if this booking status represents success"""
        return self == self.COMPLETE

    def is_failed(self) -> bool:
        """Check if this booking status represents failure"""
        return self == self.ERROR

    def is_pending(self) -> bool:
        """Check if this booking status represents pending"""
        return self == self.NEW


class CheckoutStatus(Enum):
    """Check-out status enumeration"""

    NEW = "NEW"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"
    SENT_TO_CANCEL = "SENT_TO_CANCEL"

    def is_success(self) -> bool:
        """Check if this checkout status represents success"""
        return self == self.COMPLETE

    def is_failed(self) -> bool:
        """Check if this checkout status represents failure"""
        return self in [self.ERROR]

    def is_pending(self) -> bool:
        """Check if this checkout status represents pending"""
        return self == self.NEW


class RoomChangeStatus(Enum):
    """Room change status enumeration"""

    NEW = "NEW"
    ERROR = "ERROR"

    def is_success(self) -> bool:
        """Check if this room change status represents success"""
        # No explicit success state, NEW might indicate no room change needed
        return False

    def is_failed(self) -> bool:
        """Check if this room change status represents failure"""
        return self == self.ERROR

    def is_pending(self) -> bool:
        """Check if this room change status represents pending"""
        return self == self.NEW


class PoliceType(Enum):
    """Police type enumeration"""

    AVS = "AVS"
    CEV = "CEV"
    CHE = "CHE"
    COL = "COL"
    CUP = "CUP"
    CUP2 = "CUP2"
    ERT = "ERT"
    FAKE = "FAKE"
    FER = "FER"
    HREV = "HREV"
    ISP = "ISP"
    MOS = "MOS"
    NAT = "NAT"
    POL = "POL"
    SEF = "SEF"
    SEF2 = "SEF2"
    THAI = "THAI"
    UHH = "UHH"
    UHH2 = "UHH2"


@dataclass
class PoliceRegistration:
    """
    Police Registration model representing a police registration record

    This model corresponds to the police_registrations database table
    and contains all the information about a police registration transaction.
    """

    # Primary fields
    id: UUID
    created_at: datetime
    updated_at: datetime

    # Core registration information (required fields first)
    status: RegistrationStatus
    status_booking: BookingStatus
    status_check_out: CheckoutStatus
    status_room_change: RoomChangeStatus
    reservation_id: UUID

    # Optional fields with defaults
    status_details: str = ""
    vr_sheet_number: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    police_type: Optional[PoliceType] = None

    def __post_init__(self):
        """Post-initialization processing"""
        # Convert string enums to proper enum instances if needed
        if isinstance(self.status, str):
            self.status = RegistrationStatus(self.status)
        if isinstance(self.status_booking, str):
            self.status_booking = BookingStatus(self.status_booking)
        if isinstance(self.status_check_out, str):
            self.status_check_out = CheckoutStatus(self.status_check_out)
        if isinstance(self.status_room_change, str):
            self.status_room_change = RoomChangeStatus(self.status_room_change)
        if isinstance(self.police_type, str):
            try:
                self.police_type = PoliceType(self.police_type)
            except ValueError:
                # Handle invalid police types gracefully - set to None
                # This can happen when movement vendor types like "HOS" appear in registration data
                self.police_type = None

    @classmethod
    def _safe_police_type(
        cls, police_type_value: Optional[str]
    ) -> Optional[PoliceType]:
        """
        Safely convert string to PoliceType enum, handling invalid values

        Args:
            police_type_value: String police type value

        Returns:
            PoliceType enum or None if invalid/missing
        """
        if not police_type_value:
            return None

        try:
            return PoliceType(police_type_value)
        except ValueError:
            # Handle invalid police types gracefully -
            # This can happen when movement vendor types like "HOS" appear
            return None

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "PoliceRegistration":
        """
        Create PoliceRegistration instance from database row

        Args:
            row: Dictionary representing a database row

        Returns:
            PoliceRegistration instance
        """
        return cls(
            id=UUID(row["id"]) if isinstance(row["id"], str) else row["id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            status=RegistrationStatus(row["status"]),
            status_details=row.get("status_details", ""),
            status_booking=BookingStatus(row["status_booking"]),
            status_check_out=CheckoutStatus(row["status_check_out"]),
            status_room_change=RoomChangeStatus(row["status_room_change"]),
            reservation_id=(
                UUID(row["reservation_id"])
                if isinstance(row["reservation_id"], str)
                else row["reservation_id"]
            ),
            vr_sheet_number=row.get("vr_sheet_number", ""),
            start_date=row.get("start_date"),
            end_date=row.get("end_date"),
            police_type=cls._safe_police_type(row.get("police_type")),
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert PoliceRegistration to dictionary

        Returns:
            Dictionary representation of the registration
        """
        return {
            "id": str(self.id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status.value,
            "status_details": self.status_details,
            "status_booking": self.status_booking.value,
            "status_check_out": self.status_check_out.value,
            "status_room_change": self.status_room_change.value,
            "reservation_id": str(self.reservation_id),
            "vr_sheet_number": self.vr_sheet_number,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "police_type": self.police_type.value if self.police_type else None,
        }

    def is_successful(self) -> bool:
        """Check if this registration is considered successful"""
        return self.status.is_success()

    def is_failed(self) -> bool:
        """Check if this registration has failed"""
        return self.status.is_failed()

    def is_pending(self) -> bool:
        """Check if this registration is still pending"""
        return self.status.is_pending()

    def get_overall_status(self) -> str:
        """
        Get overall status considering all sub-statuses

        Returns:
            Overall status string
        """
        if self.is_successful():
            return "Success"
        elif self.is_failed():
            return "Failed"
        elif self.is_pending():
            return "Pending"
        else:
            return "Unknown"

    def has_booking_issues(self) -> bool:
        """Check if there are booking-related issues"""
        return self.status_booking.is_failed()

    def has_checkout_issues(self) -> bool:
        """Check if there are checkout-related issues"""
        return self.status_check_out.is_failed()

    def has_room_change_issues(self) -> bool:
        """Check if there are room change-related issues"""
        return self.status_room_change.is_failed()

    def get_duration_days(self) -> Optional[int]:
        """Get registration duration in days"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return None

    def is_current_registration(self) -> bool:
        """Check if this is a current/active registration"""
        if not self.start_date or not self.end_date:
            return False

        today = date.today()
        return self.start_date <= today <= self.end_date

    def is_past_registration(self) -> bool:
        """Check if this is a past registration"""
        if not self.end_date:
            return False

        return self.end_date < date.today()

    def is_future_registration(self) -> bool:
        """Check if this is a future registration"""
        if not self.start_date:
            return False

        return self.start_date > date.today()

    def get_phase_summary(self) -> Dict[str, str]:
        """
        Get summary of all phase statuses

        Returns:
            Dictionary with phase status summary
        """
        return {
            "overall": self.status.value,
            "booking": self.status_booking.value,
            "checkout": self.status_check_out.value,
            "room_change": self.status_room_change.value,
        }

    def get_issues_summary(self) -> list[str]:
        """
        Get list of current issues

        Returns:
            List of issue descriptions
        """
        issues = []

        if self.has_booking_issues():
            issues.append("Booking issues")

        if self.has_checkout_issues():
            issues.append("Checkout issues")

        if self.has_room_change_issues():
            issues.append("Room change issues")

        if self.is_failed():
            issues.append("Overall registration failed")

        return issues

    def __str__(self) -> str:
        """String representation of PoliceRegistration"""
        return (
            f"PoliceRegistration(id={self.id}, status={self.status.value}, "
            f"reservation_id={self.reservation_id})"
        )

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (
            f"PoliceRegistration(id={self.id}, created_at={self.created_at}, "
            f"status={self.status.value}, booking={self.status_booking.value}, "
            f"checkout={self.status_check_out.value})"
        )
