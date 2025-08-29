from enum import Enum
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass

from models.base_classes import BookingStatus
from models.base_classes import CheckoutStatus


class StatType(Enum):
    AEEM = "AEEM"
    ATVIET = "ATVIET"
    COTRA = "COTRA"
    ITAB = "ITAB"
    ITCA = "ITCA"
    ITCB = "ITCB"
    ITCS = "ITCS"
    ITER = "ITER"
    ITLA = "ITLA"
    ITLI = "ITLI"
    ITLO = "ITLO"
    ITMA = "ITMA"
    ITPI = "ITPI"
    ITPU_DMS = "ITPU_DMS"
    ITPU_SE = "ITPU_SE"
    ITRA = "ITRA"
    ITSA = "ITSA"
    ITSA_V2 = "ITSA_V2"
    ITSI_V2 = "ITSI_V2"
    ITT3 = "ITT3"
    ITTO = "ITTO"
    ITTO_V2 = "ITTO_V2"
    ITTR = "ITTR"
    ITTR_V2 = "ITTR_V2"
    ITVE = "ITVE"


@dataclass
class StatRegistration:
    """
    Data class representing a statistical registration record.
    """
    # Primary fields
    id: UUID
    created_at: datetime
    updated_at: datetime

    # Core registration information (required fields first)
    status_check_in_details: str
    status_check_out_details: str
    status_check_in: BookingStatus
    status_check_out: CheckoutStatus

    reservation_id: UUID
    stat_type: StatType

    @classmethod
    def _safe_stat_type(cls, value: str) -> StatType | None:
        """Safely convert a string to a StatType enum member."""
        try:
            return StatType(value)
        except ValueError:
            return None

    @classmethod
    def from_db_row(cls, row: dict) -> "StatRegistration":
        """Create StatRegistration instance from database row dictionary"""
        return cls(
            id=UUID(row["id"]) if isinstance(row["id"], str) else row["id"],
            created_at=row.get("created_at", ""),
            updated_at=row.get("updated_at", ""),
            status_check_in_details=row.get("status_check_in_details", ""),
            status_check_out_details=row.get("status_check_out_details", ""),
            status_check_in=BookingStatus(row.get("status_check_in")),
            status_check_out=CheckoutStatus(row.get("status_check_out")),
            reservation_id=row.get("reservation_id", ""),
            stat_type=cls._safe_stat_type(row.get("stat_type"))
        )

    def to_dict(self) -> dict:
        """Convert StatRegistration instance to dictionary"""
        return {
            "id": str(self.id),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "status_check_in_details": self.status_check_in_details,
            "status_check_out_details": self.status_check_out_details,
            "status_check_in": self.status_check_in.value if self.status_check_in else None,
            "status_check_out": self.status_check_out.value if self.status_check_out else None,
            "reservation_id": str(self.reservation_id) if self.reservation_id else None,
            "stat_type": self.stat_type.value if self.stat_type else None,
        }
