from typing import List, Optional
from datetime import date
from uuid import UUID
from database_manager import DatabaseManager
from models.police_movement import (
    PoliceMovement,
    MovementState,
    MovementAction,
    VendorType,
)


class PoliceMovementService:
    """Service for retrieving police movements from PostgreSQL database"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_all_movements(self, limit: Optional[int] = None) -> List[PoliceMovement]:
        """Get all police movements"""
        query = "SELECT * FROM movements_policemovement ORDER BY created_at DESC"
        if limit:
            query += f" LIMIT {limit}"

        conn = self.db_manager.postgres
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

        return [PoliceMovement.from_db_row(dict(zip(columns, row))) for row in rows]

    def get_movement_by_id(self, movement_id: UUID) -> Optional[PoliceMovement]:
        """Get police movement by ID"""
        query = "SELECT * FROM movements_policemovement WHERE id = %s"

        conn = self.db_manager.postgres
        with conn.cursor() as cur:
            cur.execute(query, (str(movement_id),))
            row = cur.fetchone()
            if not row:
                return None
            columns = [desc[0] for desc in cur.description]

        return PoliceMovement.from_db_row(dict(zip(columns, row)))

    def get_movements_by_state(self, state: MovementState) -> List[PoliceMovement]:
        """Get police movements by state"""
        query = "SELECT * FROM movements_policemovement WHERE state = %s ORDER BY created_at DESC"

        conn = self.db_manager.postgres
        with conn.cursor() as cur:
            cur.execute(query, (state.value,))
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

        return [PoliceMovement.from_db_row(dict(zip(columns, row))) for row in rows]

    def get_movements_by_vendor(self, vendor: VendorType) -> List[PoliceMovement]:
        """Get police movements by vendor"""
        query = "SELECT * FROM movements_policemovement WHERE vendor = %s ORDER BY created_at DESC"

        conn = self.db_manager.postgres
        with conn.cursor() as cur:
            cur.execute(query, (vendor.value,))
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

        return [PoliceMovement.from_db_row(dict(zip(columns, row))) for row in rows]

    def get_movements_by_reservation(
        self, reservation_id: UUID
    ) -> List[PoliceMovement]:
        """Get police movements by reservation ID"""
        query = "SELECT * FROM movements_policemovement WHERE reservation_id = %s ORDER BY created_at DESC"

        conn = self.db_manager.postgres
        with conn.cursor() as cur:
            cur.execute(query, (str(reservation_id),))
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

        return [PoliceMovement.from_db_row(dict(zip(columns, row))) for row in rows]

    def get_movements_by_date_range(
        self, start_date: date, end_date: date
    ) -> List[PoliceMovement]:
        """Get police movements within date range"""
        query = """
        SELECT * FROM movements_policemovement 
        WHERE DATE(created_at) BETWEEN %s AND %s 
        ORDER BY created_at DESC
        """

        conn = self.db_manager.postgres
        with conn.cursor() as cur:
            cur.execute(query, (start_date, end_date))
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

        return [PoliceMovement.from_db_row(dict(zip(columns, row))) for row in rows]
