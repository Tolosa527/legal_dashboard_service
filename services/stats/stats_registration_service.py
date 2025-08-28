from database_manager import DatabaseManager  # Adjust the import path as needed
from typing import List
from datetime import date

from models.stat_registration import StatRegistration


class StatRegistrationService:
    """Service for retrieving stat registrations from PostgreSQL database"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_registrations_by_date_range(
        self, start_date: date, end_date: date
    ) -> List[StatRegistration]:
        """Get police registrations within date range based on created_at"""
        query = """
        SELECT
            sr.status_check_in as status_check_in,
            sr.status_check_out as status_check_out,
            srt.status_details,
            sr.updated_at,
            sr.created_at,
            sr.reservation_id,
            sr.id,
            COALESCE(srt.stat_report -> 'stat_account' ->> 'type', NULL) as police_type
        FROM stat_registrations sr
        JOIN stat_registration_tasks srt ON srt.id IN (sr.task_check_in_id, sr.task_check_out_id)
        WHERE srt.created_at >= %s AND srt.created_at <= %s
        ORDER BY srt.created_at desc
        """

        conn = self.db_manager.postgres
        with conn.cursor() as cur:
            cur.execute(query, (start_date, end_date))
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

        return [
            StatRegistration.from_db_row(dict(zip(columns, row)))
            for row in rows
        ]
