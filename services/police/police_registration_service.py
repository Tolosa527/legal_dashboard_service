from typing import List
from datetime import date
from database_manager import DatabaseManager
from models.police_registration import (
    PoliceRegistration,
)


class PoliceRegistrationService:
    """Service for retrieving police registrations from PostgreSQL database"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

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
