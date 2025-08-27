from typing import List, Optional, Dict, Any
from datetime import datetime, date
from uuid import UUID
from database_manager import DatabaseManager
from dataclasses import dataclass, asdict
from enum import Enum


class UnifiedPoliceState(Enum):
    """Unified police state enumeration"""
    NEW = "NEW"
    CONFIRMED = "CONFIRMED"
    SUCCESS = "SUCCESS"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"
    CANCELED = "CANCELED"
    EXPIRED = "EXPIRED"
    INVALID = "INVALID"
    IN_PROGRESS = "IN_PROGRESS"
    PROGRESS = "PROGRESS"
    NOT_APPLY = "NOT_APPLY"
    SCHEDULED = "SCHEDULED"
    SENT_TO_CANCEL = "SENT_TO_CANCEL"


class UnifiedPoliceAction(Enum):
    """Unified police action enumeration"""
    CHECK_IN = "CHECK_IN"
    PRE_CHECK_IN = "PRE_CHECK_IN"
    CHECK_OUT = "CHECK_OUT"
    CANCELED = "CANCELED"
    CANCELED_PRE_CHECK_IN = "CANCELED_PRE_CHECK_IN"
    GENERATE_RECIPT = "GENERATE_RECIPT"
    BOOKING = "BOOKING"
    REGISTRATION = "REGISTRATION"


class UnifiedPoliceType(Enum):
    """Unified police type enumeration"""
    # Movement vendor types
    SPAIN_HOS = "SPAIN_HOS"
    GERMANY = "GERMANY"
    CROATIAN_CEV = "CROATIAN_CEV"
    PORTUGAL_SEF = "PORTUGAL_SEF"
    ITALIA = "ITALIA"
    CZECH_CUP = "CZECH_CUP"

    # Police account types
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


class UnifiedMovementType(Enum):
    """Unified movement type enumeration"""
    NEW_BOOKING = "NEW_BOOKING"
    BOOKING_MODIFIED = "BOOKING_MODIFIED"
    NEW_GUEST = "NEW_GUEST"
    GUEST_MODIFIED = "GUEST_MODIFIED"
    REGISTRATION = "REGISTRATION"
    EMPTY = ""


@dataclass
class UnifiedPoliceData:
    """
    Unified police data model for MongoDB storage
    
    This combines data from both police_movements and police_registrations
    into a single consistent schema.
    """
    
    # Primary fields
    id: str
    created_at: datetime
    updated_at: datetime
    
    # Core information
    action: UnifiedPoliceAction
    state: UnifiedPoliceState
    movement_type: UnifiedMovementType
    police_type: UnifiedPoliceType
    
    # Data and details
    data: str = ""
    reason: str = ""
    
    # Source information
    source_type: str = ""  # "movement" or "registration"
    reservation_id: Optional[str] = None
    
    # Additional fields
    expiration_date: Optional[datetime] = None
    last_sent_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    vr_sheet_number: str = ""
    
    def to_mongo_dict(self) -> Dict[str, Any]:
        """Convert to MongoDB document format"""
        doc = asdict(self)
        
        # Convert enums to values
        doc['action'] = self.action.value
        doc['state'] = self.state.value
        doc['movement_type'] = self.movement_type.value
        doc['police_type'] = self.police_type.value
        
        # Handle datetime objects for MongoDB
        if isinstance(doc['created_at'], datetime):
            doc['created_at'] = doc['created_at'].isoformat()
        if isinstance(doc['updated_at'], datetime):
            doc['updated_at'] = doc['updated_at'].isoformat()
        if doc.get('expiration_date') and isinstance(doc['expiration_date'], date):
            doc['expiration_date'] = doc['expiration_date'].isoformat()
        if doc.get('last_sent_date') and isinstance(doc['last_sent_date'], datetime):
            doc['last_sent_date'] = doc['last_sent_date'].isoformat()
            
        return doc
    
    @classmethod
    def from_mongo_dict(cls, doc: Dict[str, Any]) -> "UnifiedPoliceData":
        """Create instance from MongoDB document"""
        return cls(
            id=doc["id"],
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
            action=UnifiedPoliceAction(doc["action"]),
            state=UnifiedPoliceState(doc["state"]),
            movement_type=UnifiedMovementType(doc["movement_type"]),
            police_type=UnifiedPoliceType(doc["police_type"]),
            data=doc.get("data", ""),
            reason=doc.get("reason", ""),
            source_type=doc.get("source_type", ""),
            reservation_id=doc.get("reservation_id"),
            expiration_date=doc.get("expiration_date"),
            last_sent_date=doc.get("last_sent_date"),
            start_date=doc.get("start_date"),
            end_date=doc.get("end_date"),
            vr_sheet_number=doc.get("vr_sheet_number", ""),
        )

@dataclass
class PoliceDataMongoService:
    """Service for storing unified police data in MongoDB"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.collection_name = "police_data"
    
    def _get_collection(self):
        """Get MongoDB collection"""
        mongo_db = self.db_manager.mongo
        return mongo_db[self.collection_name]
    
    def store_police_movement(self, movement) -> str:
        """
        Store police movement data in unified format
        
        Args:
            movement: PoliceMovement instance
            
        Returns:
            MongoDB document ID
        """
        # Map movement fields to unified schema
        unified_data = UnifiedPoliceData(
            id=str(movement.id),
            created_at=movement.created_at,
            updated_at=movement.updated_at,
            action=self._map_movement_action(movement.action.value),
            state=self._map_movement_state(movement.state.value),
            movement_type=self._map_movement_type(movement.movement_type.value),
            police_type=self._map_vendor_to_police_type(movement.vendor.value),
            data=movement.data,
            reason=movement.reason,
            source_type="movement",
            reservation_id=str(movement.reservation_id) if movement.reservation_id else None,
            expiration_date=movement.expiration_date,
            last_sent_date=movement.last_sent_date,
        )
        
        collection = self._get_collection()
        doc = unified_data.to_mongo_dict()
        result = collection.replace_one(
            {"id": doc["id"]}, 
            doc, 
            upsert=True
        )
        return str(result.upserted_id if result.upserted_id else doc["id"])
    
    def store_police_registration(self, registration) -> str:
        """
        Store police registration data in unified format
        
        Args:
            registration: PoliceRegistration instance

        Returns:
            MongoDB document ID
        """
        # Map registration fields to unified schema
        unified_data = UnifiedPoliceData(
            id=str(registration.id),
            created_at=registration.created_at,
            updated_at=registration.updated_at,
            action=UnifiedPoliceAction.REGISTRATION,
            state=self._map_registration_state(registration.status.value),
            movement_type=UnifiedMovementType.REGISTRATION,
            police_type=self._map_police_type(registration.police_type.value) if registration.police_type else UnifiedPoliceType.POL,
            data="",
            reason=registration.status_details,
            source_type="registration",
            reservation_id=str(registration.reservation_id),
            start_date=registration.start_date,
            end_date=registration.end_date,
            vr_sheet_number=registration.vr_sheet_number,
        )

        collection = self._get_collection()
        doc = unified_data.to_mongo_dict()
        result = collection.replace_one(
            {"id": doc["id"]},
            doc,
            upsert=True
        )
        return str(result.upserted_id if result.upserted_id else doc["id"])
    
    def get_all_police_data(self, limit: Optional[int] = None) -> List[UnifiedPoliceData]:
        """Get all police data"""
        collection = self._get_collection()
        cursor = collection.find().sort("created_at", -1)
        if limit:
            cursor = cursor.limit(limit)
        
        return [UnifiedPoliceData.from_mongo_dict(doc) for doc in cursor]
    
    def get_police_data_by_id(self, data_id: str) -> Optional[UnifiedPoliceData]:
        """Get police data by ID"""
        collection = self._get_collection()
        doc = collection.find_one({"id": data_id})
        return UnifiedPoliceData.from_mongo_dict(doc) if doc else None
    
    def get_police_data_by_state(self, state: UnifiedPoliceState) -> List[UnifiedPoliceData]:
        """Get police data by state"""
        collection = self._get_collection()
        cursor = collection.find({"state": state.value}).sort("created_at", -1)
        return [UnifiedPoliceData.from_mongo_dict(doc) for doc in cursor]
    
    def get_police_data_by_police_type(self, police_type: UnifiedPoliceType) -> List[UnifiedPoliceData]:
        """Get police data by police type"""
        collection = self._get_collection()
        cursor = collection.find({"police_type": police_type.value}).sort("created_at", -1)
        return [UnifiedPoliceData.from_mongo_dict(doc) for doc in cursor]
    
    def get_police_data_by_source(self, source_type: str) -> List[UnifiedPoliceData]:
        """Get police data by source type (movement/registration)"""
        collection = self._get_collection()
        cursor = collection.find({"source_type": source_type}).sort("created_at", -1)
        return [UnifiedPoliceData.from_mongo_dict(doc) for doc in cursor]
    
    def get_police_data_by_reservation(self, reservation_id: str) -> List[UnifiedPoliceData]:
        """Get police data by reservation ID"""
        collection = self._get_collection()
        cursor = collection.find({"reservation_id": reservation_id}).sort("created_at", -1)
        return [UnifiedPoliceData.from_mongo_dict(doc) for doc in cursor]
    
    def update_police_data(self, data_id: str, updates: Dict[str, Any]) -> bool:
        """Update police data"""
        collection = self._get_collection()
        result = collection.update_one({"id": data_id}, {"$set": updates})
        return result.modified_count > 0
    
    def delete_police_data(self, data_id: str) -> bool:
        """Delete police data"""
        collection = self._get_collection()
        result = collection.delete_one({"id": data_id})
        return result.deleted_count > 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get optimized statistics about police data using aggregation."""
        collection = self._get_collection()
        
        # Basic counts
        total_count = collection.count_documents({})
        movement_count = collection.count_documents({"source_type": "movement"})
        registration_count = collection.count_documents({"source_type": "registration"})
        
        # Optimized aggregation for state distribution
        state_pipeline = [
            {"$group": {"_id": "$state", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        state_results = list(collection.aggregate(state_pipeline))
        state_distribution = {item["_id"]: item["count"] for item in state_results}

        # Optimized aggregation for police type distribution
        type_pipeline = [
            {"$group": {"_id": "$police_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        type_results = list(collection.aggregate(type_pipeline))
        police_type_distribution = {item["_id"]: item["count"] for item in type_results}

        return {
            "total_records": total_count,
            "movements": movement_count,
            "registrations": registration_count,
            "state_distribution": state_distribution,
            "police_type_distribution": police_type_distribution,
        }

    # Mapping methods
    def _map_movement_action(self, action: str) -> UnifiedPoliceAction:
        """Map movement action to unified action"""
        return UnifiedPoliceAction(action)
    
    def _map_movement_state(self, state: str) -> UnifiedPoliceState:
        """Map movement state to unified state"""
        return UnifiedPoliceState(state)
    
    def _map_movement_type(self, movement_type: str) -> UnifiedMovementType:
        """Map movement type to unified movement type"""
        return UnifiedMovementType(movement_type)
    
    def _map_vendor_to_police_type(self, vendor: str) -> UnifiedPoliceType:
        """Map vendor to unified police type"""
        return UnifiedPoliceType(vendor)
    
    def _map_registration_state(self, status: str) -> UnifiedPoliceState:
        """Map registration status to unified state"""
        return UnifiedPoliceState(status)
    
    def _map_police_type(self, police_type: str) -> UnifiedPoliceType:
        """Map police type to unified police type"""
        # Handle special cases where movement vendor types appear in registration data
        if police_type == "HOS":
            # "HOS" is part of "SPAIN_HOS" movement vendor, map to appropriate type
            return UnifiedPoliceType.SPAIN_HOS
        
        return UnifiedPoliceType(police_type)
