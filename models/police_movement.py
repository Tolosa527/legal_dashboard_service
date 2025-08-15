"""
Police Movement Models

This module contains the PoliceMovement model and related enums
based on the movements_policemovement database table.
"""

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime, date
from dataclasses import dataclass
from uuid import UUID
import json


class MovementState(Enum):
    """Police movement state enumeration"""
    NEW = "NEW"
    CONFIRMED = "CONFIRMED"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    CANCELED = "CANCELED"
    EXPIRED = "EXPIRED"
    INVALID = "INVALID"
    IN_PROGRESS = "IN_PROGRESS"
    NOT_APPLY = "NOT_APPLY"

    @classmethod
    def success_states(cls) -> list["MovementState"]:
        """Return states considered successful"""
        return [cls.SUCCESS, cls.CONFIRMED]
    
    @classmethod
    def failed_states(cls) -> list["MovementState"]:
        """Return states considered failed"""
        return [cls.ERROR, cls.EXPIRED, cls.INVALID]
    
    @classmethod
    def pending_states(cls) -> list["MovementState"]:
        """Return states considered pending/in progress"""
        return [cls.NEW, cls.IN_PROGRESS]
    
    def is_success(self) -> bool:
        """Check if this state represents success"""
        return self in self.success_states()
    
    def is_failed(self) -> bool:
        """Check if this state represents failure"""
        return self in self.failed_states()
    
    def is_pending(self) -> bool:
        """Check if this state represents pending/in progress"""
        return self in self.pending_states()


class MovementAction(Enum):
    """Police movement action enumeration"""
    CHECK_IN = "CHECK_IN"
    PRE_CHECK_IN = "PRE_CHECK_IN"
    CHECK_OUT = "CHECK_OUT"
    CANCELED = "CANCELED"
    CANCELED_PRE_CHECK_IN = "CANCELED_PRE_CHECK_IN"
    GENERATE_RECIPT = "GENERATE_RECIPT"  # Note: keeping original typo from DB


class MovementType(Enum):
    """Police movement type enumeration"""
    NEW_BOOKING = "NEW_BOOKING"
    BOOKING_MODIFIED = "BOOKING_MODIFIED"
    NEW_GUEST = "NEW_GUEST"
    GUEST_MODIFIED = "GUEST_MODIFIED"
    EMPTY = ""  # For empty string values in DB


class VendorType(Enum):
    """Police vendor/service type enumeration"""
    SPAIN_HOS = "SPAIN_HOS"
    GERMANY = "GERMANY"
    CROATIAN_CEV = "CROATIAN_CEV"
    PORTUGAL_SEF = "PORTUGAL_SEF"
    ITALIA = "ITALIA"
    CZECH_CUP = "CZECH_CUP"

    @classmethod
    def get_display_name(cls, vendor: str) -> str:
        """Get human-readable display name for vendor"""
        display_names = {
            cls.SPAIN_HOS.value: "Spain - Hospedajes Police",
            cls.GERMANY.value: "Germany Police",
            cls.CROATIAN_CEV.value: "Croatian CEV",
            cls.PORTUGAL_SEF.value: "Portugal SEF",
            cls.ITALIA.value: "Italy Police",
            cls.CZECH_CUP.value: "Czech Republic CUP",
        }
        return display_names.get(vendor, vendor)


@dataclass
class PoliceMovement:
    """
    Police Movement model representing a police registration movement
    
    This model corresponds to the movements_policemovement database table
    and contains all the information about a police registration transaction.
    """
    
    # Primary fields
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    # Core movement information
    action: MovementAction
    state: MovementState
    movement_type: MovementType
    vendor: VendorType
    
    # Dates and timing
    expiration_date: Optional[date] = None
    last_sent_date: Optional[datetime] = None
    
    # Data and details
    data: str = ""
    reason: str = ""
    
    # Relationships
    reservation_id: Optional[UUID] = None
    
    # Additional fields
    tax_data: Dict[str, Any] = None
    is_sent_manually: bool = False
    
    def __post_init__(self):
        """Post-initialization processing"""
        if self.tax_data is None:
            self.tax_data = {}
        
        # Convert string enums to proper enum instances if needed
        if isinstance(self.action, str):
            self.action = MovementAction(self.action)
        if isinstance(self.state, str):
            self.state = MovementState(self.state)
        if isinstance(self.movement_type, str):
            self.movement_type = MovementType(self.movement_type)
        if isinstance(self.vendor, str):
            self.vendor = VendorType(self.vendor)
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "PoliceMovement":
        """
        Create PoliceMovement instance from database row
        
        Args:
            row: Dictionary representing a database row
            
        Returns:
            PoliceMovement instance
        """
        # Parse tax_data if it's a string
        tax_data = row.get("tax_data", {})
        if isinstance(tax_data, str):
            try:
                tax_data = json.loads(tax_data)
            except (json.JSONDecodeError, TypeError):
                tax_data = {}
        
        return cls(
            id=UUID(row["id"]) if isinstance(row["id"], str) else row["id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            action=MovementAction(row["action"]),
            state=MovementState(row["state"]),
            movement_type=MovementType(row["movement_type"]),
            vendor=VendorType(row["vendor"]),
            expiration_date=row.get("expiration_date"),
            last_sent_date=row.get("last_sent_date"),
            data=row.get("data", ""),
            reason=row.get("reason", ""),
            reservation_id=UUID(row["reservation_id"]) if row.get("reservation_id") else None,
            tax_data=tax_data,
            is_sent_manually=row.get("is_sent_manually", False),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert PoliceMovement to dictionary
        
        Returns:
            Dictionary representation of the movement
        """
        return {
            "id": str(self.id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "action": self.action.value,
            "state": self.state.value,
            "movement_type": self.movement_type.value,
            "vendor": self.vendor.value,
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "last_sent_date": self.last_sent_date.isoformat() if self.last_sent_date else None,
            "data": self.data,
            "reason": self.reason,
            "reservation_id": str(self.reservation_id) if self.reservation_id else None,
            "tax_data": self.tax_data,
            "is_sent_manually": self.is_sent_manually,
        }
    
    def is_successful(self) -> bool:
        """Check if this movement is considered successful"""
        return self.state.is_success()
    
    def is_failed(self) -> bool:
        """Check if this movement has failed"""
        return self.state.is_failed()
    
    def is_pending(self) -> bool:
        """Check if this movement is still pending"""
        return self.state.is_pending()
    
    def get_vendor_display_name(self) -> str:
        """Get human-readable vendor name"""
        return VendorType.get_display_name(self.vendor.value)
    
    def is_expired(self) -> bool:
        """Check if the movement has expired"""
        if not self.expiration_date:
            return False
        
        from datetime import date
        return date.today() > self.expiration_date
    
    def days_until_expiration(self) -> Optional[int]:
        """Get number of days until expiration"""
        if not self.expiration_date:
            return None
        
        from datetime import date
        delta = self.expiration_date - date.today()
        return delta.days
    
    def __str__(self) -> str:
        """String representation of PoliceMovement"""
        return (f"PoliceMovement(id={self.id}, action={self.action.value}, "
                f"state={self.state.value}, vendor={self.vendor.value})")
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"PoliceMovement(id={self.id}, created_at={self.created_at}, "
                f"action={self.action.value}, state={self.state.value}, "
                f"movement_type={self.movement_type.value}, vendor={self.vendor.value})")


# Utility functions for metrics and analysis

def calculate_success_rate(movements: list[PoliceMovement]) -> float:
    """
    Calculate success rate for a list of movements
    
    Args:
        movements: List of PoliceMovement instances
        
    Returns:
        Success rate as percentage (0-100)
    """
    if not movements:
        return 0.0
    
    successful_count = sum(1 for movement in movements if movement.is_successful())
    return (successful_count / len(movements)) * 100


def group_by_vendor(movements: list[PoliceMovement]) -> Dict[VendorType, list[PoliceMovement]]:
    """
    Group movements by vendor
    
    Args:
        movements: List of PoliceMovement instances
        
    Returns:
        Dictionary mapping vendor to list of movements
    """
    groups = {}
    for movement in movements:
        if movement.vendor not in groups:
            groups[movement.vendor] = []
        groups[movement.vendor].append(movement)
    return groups


def group_by_action(movements: list[PoliceMovement]) -> Dict[MovementAction, list[PoliceMovement]]:
    """
    Group movements by action
    
    Args:
        movements: List of PoliceMovement instances
        
    Returns:
        Dictionary mapping action to list of movements
    """
    groups = {}
    for movement in movements:
        if movement.action not in groups:
            groups[movement.action] = []
        groups[movement.action].append(movement)
    return groups


def group_by_state(movements: list[PoliceMovement]) -> Dict[MovementState, list[PoliceMovement]]:
    """
    Group movements by state
    
    Args:
        movements: List of PoliceMovement instances
        
    Returns:
        Dictionary mapping state to list of movements
    """
    groups = {}
    for movement in movements:
        if movement.state not in groups:
            groups[movement.state] = []
        groups[movement.state].append(movement)
    return groups


def get_vendor_success_rates(movements: list[PoliceMovement]) -> Dict[VendorType, float]:
    """
    Calculate success rates by vendor
    
    Args:
        movements: List of PoliceMovement instances
        
    Returns:
        Dictionary mapping vendor to success rate percentage
    """
    vendor_groups = group_by_vendor(movements)
    return {
        vendor: calculate_success_rate(vendor_movements)
        for vendor, vendor_movements in vendor_groups.items()
    }


def get_action_success_rates(movements: list[PoliceMovement]) -> Dict[MovementAction, float]:
    """
    Calculate success rates by action
    
    Args:
        movements: List of PoliceMovement instances
        
    Returns:
        Dictionary mapping action to success rate percentage
    """
    action_groups = group_by_action(movements)
    return {
        action: calculate_success_rate(action_movements)
        for action, action_movements in action_groups.items()
    }
