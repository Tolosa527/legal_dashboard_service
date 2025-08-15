"""
Models package for Legal Dashboard Service
"""

from .police_movement import PoliceMovement, MovementState, MovementAction, MovementType
from .police_registration import (
    PoliceRegistration, 
    RegistrationStatus, 
    BookingStatus, 
    CheckoutStatus, 
    RoomChangeStatus
)

__all__ = [
    "PoliceMovement",
    "MovementState", 
    "MovementAction",
    "MovementType",
    "PoliceRegistration",
    "RegistrationStatus",
    "BookingStatus", 
    "CheckoutStatus",
    "RoomChangeStatus",
]
