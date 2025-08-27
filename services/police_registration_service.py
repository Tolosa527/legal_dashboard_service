from typing import List, Optional
from datetime import date
from uuid import UUID
from database_manager import DatabaseManager
from models.police_registration import (
    PoliceRegistration,
    RegistrationStatus,
    PoliceType,
)


class PoliceRegistrationService:
    """Service for retrieving police registrations from PostgreSQL database"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_all_registrations(
        self, limit: Optional[int] = None
    ) -> List[PoliceRegistration]:
        """Get all police registrations (from police_guest_registrations)"""
        query = """
        SELECT pgr.*, 
               COALESCE(prt.task_data->'housing'->'police_account'->>'type', NULL) as police_type,
               pr.reservation_id
        FROM police_guest_registrations pgr
        JOIN police_registrations pr ON pr.id = pgr.police_registration_id
        LEFT JOIN police_registration_tasks prt ON pr.id = prt.police_registration_id
        ORDER BY prt.created_at DESC
        """
        if limit:
            query += f" LIMIT {limit}"

        conn = self.db_manager.postgres
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

        return [PoliceRegistration.from_db_row(dict(zip(columns, row))) for row in rows]

    def get_registration_by_id(
        self, registration_id: UUID
    ) -> Optional[PoliceRegistration]:
        """Get police registration by ID (from police_guest_registrations)"""
        query = """
        SELECT pgr.*, 
               COALESCE(prt.task_data->'housing'->'police_account'->>'type', NULL) as police_type,
               pr.reservation_id
        FROM police_guest_registrations pgr
        JOIN police_registrations pr ON pr.id = pgr.police_registration_id
        LEFT JOIN police_registration_tasks prt ON pr.id = prt.police_registration_id
        WHERE pr.id = %s
        """

        conn = self.db_manager.postgres
        with conn.cursor() as cur:
            cur.execute(query, (str(registration_id),))
            row = cur.fetchone()
            if not row:
                return None
            columns = [desc[0] for desc in cur.description]

        return PoliceRegistration.from_db_row(dict(zip(columns, row)))

    def get_registrations_by_status(
        self, status: RegistrationStatus
    ) -> List[PoliceRegistration]:
        """Get police registrations by status (from police_guest_registrations)"""
        query = """
        SELECT pgr.*, 
               COALESCE(prt.task_data->'housing'->'police_account'->>'type', NULL) as police_type,
               pr.reservation_id
        FROM police_guest_registrations pgr
        JOIN police_registrations pr ON pr.id = pgr.police_registration_id
        LEFT JOIN police_registration_tasks prt ON pr.id = prt.police_registration_id
        WHERE pr.status = %s 
        ORDER BY prt.created_at DESC
        """

        conn = self.db_manager.postgres
        with conn.cursor() as cur:
            cur.execute(query, (status.value,))
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

        return [PoliceRegistration.from_db_row(dict(zip(columns, row))) for row in rows]

    def get_registrations_by_reservation(
        self, reservation_id: UUID
    ) -> List[PoliceRegistration]:
        """Get police registrations by reservation ID (from police_guest_registrations)"""
        query = """
        SELECT pgr.*, 
               COALESCE(prt.task_data->'housing'->'police_account'->>'type', NULL) as police_type,
               pr.reservation_id
        FROM police_guest_registrations pgr
        JOIN police_registrations pr ON pr.id = pgr.police_registration_id
        LEFT JOIN police_registration_tasks prt ON pr.id = prt.police_registration_id
        WHERE pr.reservation_id = %s 
        ORDER BY prt.created_at DESC
        """

        conn = self.db_manager.postgres
        with conn.cursor() as cur:
            cur.execute(query, (str(reservation_id),))
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

        return [PoliceRegistration.from_db_row(dict(zip(columns, row))) for row in rows]

    def get_current_registrations(self) -> List[PoliceRegistration]:
        """Get current/active police registrations (from police_guest_registrations)"""
        query = """
        SELECT pgr.*, 
               COALESCE(prt.task_data->'housing'->'police_account'->>'type', NULL) as police_type,
               pr.reservation_id
        FROM police_guest_registrations pgr
        JOIN police_registrations pr ON pr.id = pgr.police_registration_id
        LEFT JOIN police_registration_tasks prt ON pr.id = prt.police_registration_id
        WHERE pr.start_date <= CURRENT_DATE AND pr.end_date >= CURRENT_DATE
        ORDER BY prt.created_at DESC
        """

        conn = self.db_manager.postgres
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

        return [PoliceRegistration.from_db_row(dict(zip(columns, row))) for row in rows]

    def get_registrations_by_date_range(
        self, start_date: date, end_date: date
    ) -> List[PoliceRegistration]:
        """Get police registrations within date range based on created_at"""
        query = """
        SELECT pgr.*,
               COALESCE(prt.task_data->'housing'->'police_account'->>'type', NULL) as police_type,
               pr.reservation_id
        FROM police_registrations pr
        JOIN police_guest_registrations pgr ON pr.id = pgr.police_registration_id 
        LEFT JOIN police_registration_tasks prt ON pr.id = prt.police_registration_id
        WHERE prt.created_at >= %s AND prt.created_at <= %s
        ORDER BY prt.created_at desc
        """

        conn = self.db_manager.postgres
        with conn.cursor() as cur:
            cur.execute(query, (start_date, end_date))
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

        return [PoliceRegistration.from_db_row(dict(zip(columns, row))) for row in rows]

    def get_registrations_by_police_type(
        self, police_type: PoliceType
    ) -> List[PoliceRegistration]:
        """Get police registrations by police type (from police_guest_registrations)"""
        query = """
        SELECT pgr.*, 
               COALESCE(prt.task_data->'housing'->'police_account'->>'type', NULL) as police_type,
               pr.reservation_id
        FROM police_guest_registrations pgr
        JOIN police_registrations pr ON pr.id = pgr.police_registration_id
        LEFT JOIN police_registration_tasks prt ON pr.id = prt.police_registration_id
        WHERE prt.task_data->'housing'->'police_account'->>'type' = %s
        ORDER BY prt.created_at DESC
        """

        conn = self.db_manager.postgres
        with conn.cursor() as cur:
            cur.execute(query, (police_type.value,))
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

        return [PoliceRegistration.from_db_row(dict(zip(columns, row))) for row in rows]
