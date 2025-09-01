# Fixed remaining long lines in `StatisticsDataState`
import reflex as rx
from services.stats.stats_data_mongo_service import StatDataMongoService
from database_manager import DatabaseManager
from typing import Dict, Any
from app.states.success_rate_utils import calculate_stat_success_rate
from settings import settings
from dataclasses import dataclass, field
from app.states.police.config import (
    IN_PROGRESS_STATES,
    SUCCESS_STATES,
    ERROR_STATES,
    SUCCESS_RATE_THRESHOLDS,
    STATUS_LABELS,
    STATUS_COLORS,
    STATUS_ICONS,
    CACHE_TIMEOUT,
)

from logging import Logger

logger = Logger(__name__)


@dataclass
class StatisticsTypeStatusResult:

    stat_type: str
    total_records: int
    success_rate: float
    status: str
    color: str
    icon: str
    success_records: int
    states: Dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StatisticsTypeStatusResult":
        return cls(
            stat_type=data["stat_type"],
            total_records=data["total_records"],
            success_rate=data["success_rate"],
            status=data["status"],
            color=data["color"],
            icon=data["icon"],
            success_records=data["success_records"],
            states=data.get("states", {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stat_type": self.stat_type,
            "total_records": self.total_records,
            "success_rate": self.success_rate,
            "status": self.status,
            "color": self.color,
            "icon": self.icon,
            "success_records": self.success_records,
            "states": self.states,
        }


class StatisticsDataState(rx.State):
    # Store aggregated statistics instead of all raw data
    stats_cache: Dict[str, Any] = {}
    statistics_type_data: Dict[str, Any] = {}
    loading: bool = True
    error_message: str = ""
    selected_statistics_type: str = ""
    cache_timestamp: float = 0

    # Cache timeout in seconds (from config)
    CACHE_TIMEOUT: float = CACHE_TIMEOUT

    @rx.event(background=True)
    async def fetch_dashboard_stats(self):
        """Fetch only dashboard statistics (much faster than full data)."""
        import time

        # Check if cache is still valid
        current_time = time.time()
        if (
            self.stats_cache
            and (current_time - self.cache_timestamp) < self.CACHE_TIMEOUT
        ):
            async with self:
                self.loading = False
            return

        # Use singleton database manager for connection pooling
        db_manager = DatabaseManager.get_instance()
        db_manager.connect_mongo(
            connection_string=settings.get_mongo_connection_string(),
            database=settings.get_mongo_database(),
        )
        stats_data_service = StatDataMongoService(db_manager=db_manager)
        # Use context manager to modify state in background task
        async with self:
            try:
                # Get aggregated statistics instead of all data
                stats = stats_data_service.get_statistics()
                self.stats_cache = stats
                self.cache_timestamp = current_time
                # Get statistics type status data
                self.statistics_type_data = await self._get_statistics_type_statistics(
                    stats_data_service
                )
                self.loading = False
            except Exception as e:
                self.error_message = f"Failed to load data: {str(e)}"
                self.loading = False

    async def _get_statistics_type_statistics(
        self, service: StatDataMongoService
    ) -> Dict[str, StatisticsTypeStatusResult]:
        """Get aggregated statistics by statistics type."""
        collection = service._get_collection()
        success_states = SUCCESS_STATES
        error_states = ERROR_STATES
        pipeline = [
            {
                "$project": {
                    "stat_type": 1,
                    "registrations": {
                        "$concatArrays": [
                            [{"state": "$status_check_in"}],
                            [{"state": "$status_check_out"}],
                        ]
                    },
                }
            },
            {"$unwind": "$registrations"},
            {
                "$group": {
                    "_id": {
                        "stat_type": "$stat_type",
                        "state": "$registrations.state",
                    },
                    "count": {"$sum": 1},
                }
            },
            {
                "$group": {
                    "_id": "$_id.stat_type",
                    "total": {"$sum": "$count"},
                    "states": {"$push": {"state": "$_id.state", "count": "$count"}},
                }
            },
            {"$sort": {"total": -1}},
        ]

        from collections import Counter

        result = list(collection.aggregate(pipeline))
        # Process the aggregated data into expected structures
        police_type_stats = {}
        for item in result:
            stat_type = item["_id"]
            total_records = item.get("total", 0)
            # item["states"] is already an array of {state, count}
            state_counter = Counter(
                {s["state"]: s["count"] for s in item.get("states", [])}
            )
            states = dict(state_counter)
            success_count = sum(
                count for state, count in states.items() if state in success_states
            )
            try:
                sample_docs = list(
                    collection.find(
                        {"stat_type": stat_type},
                        {
                            "status_check_in": 1,
                            "status_check_out": 1,
                            "status_check_in_details": 1,
                            "status_check_out_details": 1,
                        },
                    )
                )
            except Exception:
                # If fetching sample documents fails for any reason, fall
                # back to an empty list so we don't crash the dashboard.
                sample_docs = []

            success_rate = calculate_stat_success_rate(
                success_count=success_count,
                error_states=error_states,
                docs=sample_docs,
                stat_type=stat_type,
            )
            # Determine status
            if success_rate >= SUCCESS_RATE_THRESHOLDS.good:
                status = STATUS_LABELS.good
                color = STATUS_COLORS.good
                icon = STATUS_ICONS.good
            elif success_rate >= SUCCESS_RATE_THRESHOLDS.warning:
                status = STATUS_LABELS.warning
                color = STATUS_COLORS.warning
                icon = STATUS_ICONS.warning
            else:
                status = STATUS_LABELS.error
                color = STATUS_COLORS.error
                icon = STATUS_ICONS.error

            police_type_stats[stat_type] = StatisticsTypeStatusResult(
                stat_type=stat_type,
                total_records=total_records,
                success_rate=round(success_rate, 1),
                status=status,
                color=color,
                icon=icon,
                success_records=success_count,
                states=states,
            )

        return police_type_stats

    @rx.event(background=True)
    async def fetch_statistics_data(self):
        """
        Legacy method - now just calls fetch_dashboard_stats for compatibility.
        """
        yield StatisticsDataState.fetch_dashboard_stats

    @rx.event
    def set_selected_statistics_type(self, statistics_type: str):
        """Set the selected statistics type for detailed view."""
        self.selected_statistics_type = statistics_type

    @rx.event
    def load_statistics_type_from_url(self):
        """Load statistics type from URL and set it as selected."""
        try:
            path = self.router.url.path
            if "/statistics-type/" in path:
                statistics_type = path.split("/statistics-type/")[-1]
                self.selected_statistics_type = statistics_type
        except Exception:
            pass

    @rx.var
    def get_statistics_data(self) -> list[dict]:
        """Return empty list - use specific statistics methods instead."""
        return []

    @rx.var
    def get_statistics_state_chart_data(self) -> list[dict]:
        """Get statistics data aggregated by state for pie chart."""
        if not self.stats_cache or "state_distribution" not in self.stats_cache:
            return []

        # Convert state distribution to chart format
        state_dist = self.stats_cache["state_distribution"]
        return [{"name": state, "value": count} for state, count in state_dist.items()]

    @rx.var
    def get_statistics_type_chart_data(self) -> list[dict]:
        """Get statistics data aggregated by statistics type for pie chart."""
        if (
            not self.stats_cache
            or "statistics_type_distribution" not in self.stats_cache
        ):
            return []

        # Convert type distribution to chart format
        type_dist = self.stats_cache["statistics_type_distribution"]
        return [
            {"name": statistics_type, "value": count}
            for statistics_type, count in type_dist.items()
        ]

    @rx.var
    def get_total_records(self) -> int:
        """Get total number of statistics records."""
        return self.stats_cache.get("total_records", 0)

    @rx.var
    def get_success_rate(self) -> float:
        """Get success rate percentage."""
        if not self.stats_cache or "state_distribution" not in self.stats_cache:
            return 0.0

        state_dist = self.stats_cache["state_distribution"]

        # Define states that should be excluded from success rate calculation
        in_progress_states = IN_PROGRESS_STATES
        success_states = SUCCESS_STATES

        # Calculate totals
        completed_count = sum(
            count
            for state, count in state_dist.items()
            if state not in in_progress_states
        )
        success_count = sum(
            count for state, count in state_dist.items() if state in success_states
        )

        if completed_count == 0:
            return 0.0

        return round((success_count / completed_count) * 100, 1)

    @rx.var
    def get_error_count(self) -> int:
        """Get count of error records."""
        if not self.stats_cache or "state_distribution" not in self.stats_cache:
            return 0

        return self.stats_cache["state_distribution"].get("ERROR", 0)

    @rx.var
    def get_active_types(self) -> int:
        """Get number of different statistics types."""
        if (
            not self.stats_cache
            or "statistics_type_distribution" not in self.stats_cache
        ):
            return 0

        return len(self.stats_cache["statistics_type_distribution"])

    @rx.var
    def get_service_status(self) -> str:
        """Get service status based on success rate thresholds."""
        # Calculate success rate inline instead of calling another @rx.var method
        if not self.stats_cache or "state_distribution" not in self.stats_cache:
            return "Error"

        state_dist = self.stats_cache["state_distribution"]
        in_progress_states = ["NEW", "IN_PROGRESS", "PROGRESS"]
        success_states = ["SUCCESS", "CONFIRMED", "COMPLETE"]

        completed_count = sum(
            count
            for state, count in state_dist.items()
            if state not in in_progress_states
        )
        success_count = sum(
            count for state, count in state_dist.items() if state in success_states
        )

        if completed_count == 0:
            success_rate = 0.0
        else:
            success_rate = (success_count / completed_count) * 100

        if success_rate >= SUCCESS_RATE_THRESHOLDS.good:
            return STATUS_LABELS.good
        elif success_rate >= SUCCESS_RATE_THRESHOLDS.warning:
            return STATUS_LABELS.warning
        else:
            return STATUS_LABELS.error

    @rx.var
    def get_service_status_color(self) -> str:
        """Get service status color."""
        status = self.get_service_status
        if status == STATUS_LABELS.good:
            return STATUS_COLORS.good
        elif status == STATUS_LABELS.warning:
            return STATUS_COLORS.warning
        else:
            return STATUS_COLORS.error

    @rx.var
    def get_service_status_icon(self) -> str:
        """Get service status icon."""
        status = self.get_service_status
        if status == STATUS_LABELS.good:
            return STATUS_ICONS.good
        elif status == STATUS_LABELS.warning:
            return STATUS_ICONS.warning
        else:
            return STATUS_ICONS.error

    @rx.var
    def get_statistics_type_status(self) -> list[dict]:
        """Get service status for each statistics type."""
        if not self.statistics_type_data:
            return []

        # Convert statistics type data to list format expected by UI
        result = []
        for statistics_type, data in self.statistics_type_data.items():
            # Ensure data is a StatisticsTypeStatusResult instance
            if isinstance(data, dict):
                data = StatisticsTypeStatusResult.from_dict(data)
            result.append(
                {
                    "type": statistics_type,
                    "status": getattr(data, "status", "Unknown"),
                    "color": getattr(data, "color", "grey"),
                    "icon": getattr(data, "icon", ""),
                    "success_rate": getattr(data, "success_rate", 0.0),
                    "total_records": getattr(data, "total_records", 0),
                    "success_records": getattr(data, "success_records", 0),
                }
            )

        return sorted(result, key=lambda x: x["success_rate"], reverse=True)

    @rx.var
    def get_statistics_type_detail_data(self) -> dict:
        """Get detailed data for the selected statistics type."""
        # Get statistics type from URL if not set in selected_statistics_type
        statistics_type = self.selected_statistics_type
        if not statistics_type:
            try:
                path = self.router.url.path
                if "/statistics-type/" in path:
                    statistics_type = path.split("/statistics-type/")[-1]
                else:
                    statistics_type = ""
            except Exception:
                statistics_type = ""

        if not self.statistics_type_data or not statistics_type:
            return {
                "type": statistics_type or "Unknown",
                "total_records": 0,
                "success_records": 0,
                "success_rate": 0.0,
                "status": "Unknown",
                "checkin_success_rate": 0.0,
                "checkout_success_rate": 0.0,
            }

        if statistics_type not in self.statistics_type_data:
            return {
                "type": statistics_type,
                "total_records": 0,
                "success_records": 0,
                "success_rate": 0.0,
                "status": "Unknown",
                "checkin_success_rate": 0.0,
                "checkout_success_rate": 0.0,
            }

        data = self.statistics_type_data[statistics_type]
        # Handle both dict and StatisticsTypeStatusResult objects
        if isinstance(data, dict):
            return {
                "type": statistics_type,
                "total_records": data.get("total_records", 0),
                "success_records": data.get("success_records", 0),
                "success_rate": data.get("success_rate", 0.0),
                "status": data.get("status", "Unknown"),
                # For now, use the same success rate for both
                "checkin_success_rate": data.get("success_rate", 0.0),
                "checkout_success_rate": data.get("success_rate", 0.0),
            }
        else:
            return {
                "type": statistics_type,
                "total_records": getattr(data, "total_records", 0),
                "success_records": getattr(data, "success_records", 0),
                "success_rate": getattr(data, "success_rate", 0.0),
                "status": getattr(data, "status", "Unknown"),
                # For now, use the same success rate for both
                "checkin_success_rate": getattr(data, "success_rate", 0.0),
                "checkout_success_rate": getattr(data, "success_rate", 0.0),
            }

    # Recent records cache for the current statistics type
    statistics_type_recent_records: list[dict] = []
    recent_records_loading: bool = False

    @rx.var
    def get_statistics_type_recent_records(self) -> list[dict]:
        """Get recent records for the selected statistics type."""
        return self.statistics_type_recent_records

    @rx.event(background=True)
    async def fetch_recent_records_for_statistics_type(self):
        """Fetch recent records for the current statistics type."""
        # Get statistics type from URL if not set in selected_statistics_type
        statistics_type = self.selected_statistics_type
        if not statistics_type:
            try:
                path = self.router.url.path
                if "/statistics-type/" in path:
                    statistics_type = path.split("/statistics-type/")[-1]
                else:
                    statistics_type = ""
            except Exception:
                statistics_type = ""

        if not statistics_type:
            async with self:
                self.statistics_type_recent_records = []
                self.recent_records_loading = False
            return

        async with self:
            self.recent_records_loading = True

        try:
            # Use singleton database manager for connection pooling
            db_manager = DatabaseManager.get_instance()
            mongo_db = db_manager.connect_mongo(
                connection_string=settings.get_mongo_connection_string(),
                database=settings.get_mongo_database(),
            )
            collection = mongo_db["stat_data"]

            # Fetch recent records for this statistics type
            records = list(
                collection.find(
                    {"stat_type": statistics_type},
                    {
                        "status_check_in": 1,
                        "status_check_out": 1,
                        "status_check_in_details": 1,
                        "status_check_out_details": 1,
                        "created_at": 1,
                        "_id": 0,
                    },
                )
                .sort("created_at", -1)
                .limit(10)
            )

            # Process records into the format expected by the UI
            processed_records = []
            for record in records:
                checkin_state = record.get("status_check_in", "Unknown")
                checkout_state = record.get("status_check_out", "Unknown")
                checkin_reason = record.get("status_check_in_details", "")
                checkout_reason = record.get("status_check_out_details", "")

                # Combine reasons if both exist
                reason = ""
                if checkin_reason and checkout_reason:
                    reason = f"CI: {checkin_reason} | CO: {checkout_reason}"
                elif checkin_reason:
                    reason = f"CI: {checkin_reason}"
                elif checkout_reason:
                    reason = f"CO: {checkout_reason}"
                else:
                    reason = "No details available"

                processed_records.append(
                    {
                        "checkin_state": checkin_state,
                        "checkout_state": checkout_state,
                        "reason": reason,
                    }
                )

            async with self:
                self.statistics_type_recent_records = processed_records
                self.recent_records_loading = False

        except Exception as e:
            logger.error(f"Error fetching recent records: {str(e)}")
            async with self:
                self.statistics_type_recent_records = []
                self.recent_records_loading = False

    # URL handling
    @rx.var
    def get_current_statistics_type_from_url(self) -> str:
        """Get statistics type from URL path."""
        try:
            path = self.router.url.path
            if "/statistics-type/" in path:
                return path.split("/statistics-type/")[-1]
            return "Unknown"
        except Exception:
            return "Unknown"

    # State distribution methods for detailed view
    @rx.var
    def get_statistics_type_state_distribution(self) -> list[dict]:
        """Get combined state distribution for selected statistics type."""
        statistics_type = self.selected_statistics_type
        if not statistics_type:
            try:
                path = self.router.url.path
                if "/statistics-type/" in path:
                    statistics_type = path.split("/statistics-type/")[-1]
                else:
                    statistics_type = ""
            except Exception:
                statistics_type = ""

        if not statistics_type or not self.statistics_type_data:
            return []

        # Get the states data for this statistics type
        stats_data = self.statistics_type_data.get(statistics_type)
        if not stats_data or not hasattr(stats_data, "states"):
            return []

        states = stats_data.states
        # Convert to chart format
        cleaned_data = []
        for state, count in states.items():
            if count > 0:  # Only include states with actual data
                cleaned_data.append({"name": state, "value": count})

        return cleaned_data

    @rx.var
    def get_statistics_type_checkin_distribution(self) -> list[dict]:
        """Get check-in state distribution for selected statistics type."""
        statistics_type = self.selected_statistics_type
        if not statistics_type:
            try:
                path = self.router.url.path
                if "/statistics-type/" in path:
                    statistics_type = path.split("/statistics-type/")[-1]
                else:
                    statistics_type = ""
            except Exception:
                statistics_type = ""

        if not statistics_type:
            return []

        # Query MongoDB directly for check-in states only
        try:
            db_manager = DatabaseManager.get_instance()
            mongo_db = db_manager.connect_mongo(
                connection_string=settings.get_mongo_connection_string(),
                database=settings.get_mongo_database(),
            )
            collection = mongo_db["stat_data"]

            # Aggregate check-in states only
            pipeline = [
                {"$match": {"stat_type": statistics_type}},
                {"$group": {"_id": "$status_check_in", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
            ]

            result = list(collection.aggregate(pipeline))
            cleaned_data = []
            for item in result:
                state = item["_id"]
                count = item["count"]
                if count > 0:
                    cleaned_data.append({"name": state, "value": count})
            return cleaned_data
        except Exception:
            return []

    @rx.var
    def get_statistics_type_checkout_distribution(self) -> list[dict]:
        """Get check-out state distribution for selected statistics type."""
        statistics_type = self.selected_statistics_type
        if not statistics_type:
            try:
                path = self.router.url.path
                if "/statistics-type/" in path:
                    statistics_type = path.split("/statistics-type/")[-1]
                else:
                    statistics_type = ""
            except Exception:
                statistics_type = ""

        if not statistics_type:
            return []

        # Query MongoDB directly for check-out states only
        try:
            db_manager = DatabaseManager.get_instance()
            mongo_db = db_manager.connect_mongo(
                connection_string=settings.get_mongo_connection_string(),
                database=settings.get_mongo_database(),
            )
            collection = mongo_db["stat_data"]

            # Aggregate check-out states only
            pipeline = [
                {"$match": {"stat_type": statistics_type}},
                {"$group": {"_id": "$status_check_out", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
            ]

            result = list(collection.aggregate(pipeline))
            cleaned_data = []
            for item in result:
                state = item["_id"]
                count = item["count"]
                if count > 0:
                    cleaned_data.append({"name": state, "value": count})

            return cleaned_data
        except Exception:
            return []

    # Modal state management
    show_reasons_modal: bool = False
    selected_state: str = ""
    state_reasons: list[dict] = []
    total_reasons_count: int = 0
    reasons_current_page: int = 1
    reasons_per_page: int = 10

    @rx.event
    def close_reasons_modal(self):
        """Close the reasons modal."""
        self.show_reasons_modal = False
        self.selected_state = ""
        self.state_reasons = []
        self.total_reasons_count = 0
        self.reasons_current_page = 1

    # Pagination methods
    @rx.var
    def get_paginated_reasons(self) -> list[dict]:
        """Get paginated reasons for current page."""
        start_idx = (self.reasons_current_page - 1) * self.reasons_per_page
        end_idx = start_idx + self.reasons_per_page
        return self.state_reasons[start_idx:end_idx]

    @rx.var
    def get_total_pages(self) -> int:
        """Get total number of pages for reasons."""
        if not self.state_reasons:
            return 1
        return max(
            1,
            (len(self.state_reasons) + self.reasons_per_page - 1)
            // self.reasons_per_page,
        )

    @rx.var
    def has_previous_page(self) -> bool:
        """Check if there's a previous page."""
        return self.reasons_current_page > 1

    @rx.var
    def has_next_page(self) -> bool:
        """Check if there's a next page."""
        if not self.state_reasons:
            total_pages = 1
        else:
            total_pages = max(
                1,
                (len(self.state_reasons) + self.reasons_per_page - 1)
                // self.reasons_per_page,
            )
        return self.reasons_current_page < total_pages

    @rx.event
    def go_to_previous_page(self):
        """Go to previous page."""
        if self.has_previous_page:
            self.reasons_current_page -= 1

    @rx.event
    def go_to_next_page(self):
        """Go to next page."""
        if self.has_next_page:
            self.reasons_current_page += 1

    # Combined state reason handlers
    @rx.event
    def show_combined_success_reasons(self):
        self.selected_state = "SUCCESS"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_combined_error_reasons(self):
        self.selected_state = "ERROR"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_combined_complete_reasons(self):
        self.selected_state = "COMPLETE"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_combined_confirmed_reasons(self):
        self.selected_state = "CONFIRMED"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_combined_progress_reasons(self):
        self.selected_state = "PROGRESS"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_combined_in_progress_reasons(self):
        self.selected_state = "IN_PROGRESS"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_combined_new_reasons(self):
        self.selected_state = "NEW"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_combined_invalid_reasons(self):
        self.selected_state = "INVALID"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_combined_expired_reasons(self):
        self.selected_state = "EXPIRED"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_combined_canceled_reasons(self):
        self.selected_state = "CANCELED"
        yield StatisticsDataState.show_reasons_for_state

    # Check-in state reason handlers
    @rx.event
    def show_checkin_success_reasons(self):
        self.selected_state = "CHECKIN_SUCCESS"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_checkin_error_reasons(self):
        self.selected_state = "CHECKIN_ERROR"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_checkin_complete_reasons(self):
        self.selected_state = "CHECKIN_COMPLETE"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_checkin_confirmed_reasons(self):
        self.selected_state = "CHECKIN_CONFIRMED"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_checkin_progress_reasons(self):
        self.selected_state = "CHECKIN_PROGRESS"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_checkin_in_progress_reasons(self):
        self.selected_state = "CHECKIN_IN_PROGRESS"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_checkin_new_reasons(self):
        self.selected_state = "CHECKIN_NEW"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_checkin_invalid_reasons(self):
        self.selected_state = "CHECKIN_INVALID"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_checkin_expired_reasons(self):
        self.selected_state = "CHECKIN_EXPIRED"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_checkin_canceled_reasons(self):
        self.selected_state = "CHECKIN_CANCELED"
        yield StatisticsDataState.show_reasons_for_state

    # Check-out state reason handlers
    @rx.event
    def show_checkout_success_reasons(self):
        self.selected_state = "CHECKOUT_SUCCESS"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_checkout_error_reasons(self):
        self.selected_state = "CHECKOUT_ERROR"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_checkout_complete_reasons(self):
        self.selected_state = "CHECKOUT_COMPLETE"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_checkout_confirmed_reasons(self):
        self.selected_state = "CHECKOUT_CONFIRMED"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_checkout_progress_reasons(self):
        self.selected_state = "CHECKOUT_PROGRESS"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_checkout_in_progress_reasons(self):
        self.selected_state = "CHECKOUT_IN_PROGRESS"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_checkout_new_reasons(self):
        self.selected_state = "CHECKOUT_NEW"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_checkout_invalid_reasons(self):
        self.selected_state = "CHECKOUT_INVALID"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_checkout_expired_reasons(self):
        self.selected_state = "CHECKOUT_EXPIRED"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event
    def show_checkout_canceled_reasons(self):
        self.selected_state = "CHECKOUT_CANCELED"
        yield StatisticsDataState.show_reasons_for_state

    @rx.event(background=True)
    async def show_reasons_for_state(self):
        """Show modal with reasons for the selected state."""
        async with self:
            self.show_reasons_modal = True

        # Get statistics_type from URL params if selected_statistics_type is not set
        statistics_type = self.selected_statistics_type
        if not statistics_type:
            try:
                path = self.router.url.path
                if "/statistics-type/" in path:
                    statistics_type = path.split("/statistics-type/")[-1]
                else:
                    statistics_type = ""
            except Exception:
                statistics_type = ""

        if not statistics_type:
            async with self:
                self.state_reasons = []
            return

        # Fetch reasons for this state and statistics type
        try:
            db_manager = DatabaseManager.get_instance()
            mongo_db = db_manager.connect_mongo(
                connection_string=settings.get_mongo_connection_string(),
                database=settings.get_mongo_database(),
            )
            collection = mongo_db["stat_data"]

            state = self.selected_state
            operation = "COMBINED"

            # Determine if this is check-in, check-out, or combined
            if state.startswith("CHECKIN_"):
                operation = "CHECK_IN"
                actual_state = state.replace("CHECKIN_", "")
                field = "status_check_in"
                details_field = "status_check_in_details"
            elif state.startswith("CHECKOUT_"):
                operation = "CHECK_OUT"
                actual_state = state.replace("CHECKOUT_", "")
                field = "status_check_out"
                details_field = "status_check_out_details"
            else:
                # Combined query - check both check-in and check-out
                actual_state = state
                # For combined, we'll get reasons from both fields
                records_checkin = list(
                    collection.find(
                        {
                            "stat_type": statistics_type,
                            "status_check_in": actual_state,
                            "status_check_in_details": {
                                "$exists": True,
                                "$nin": [None, ""],
                            },
                        },
                        {"status_check_in_details": 1, "created_at": 1, "_id": 0},
                    )
                    .sort("created_at", -1)
                    .limit(50)
                )

                records_checkout = list(
                    collection.find(
                        {
                            "stat_type": statistics_type,
                            "status_check_out": actual_state,
                            "status_check_out_details": {
                                "$exists": True,
                                "$nin": [None, ""],
                            },
                        },
                        {"status_check_out_details": 1, "created_at": 1, "_id": 0},
                    )
                    .sort("created_at", -1)
                    .limit(50)
                )

                # Count reasons and prepare combined list
                reasons_count = {}
                for record in records_checkin:
                    reason = record.get("status_check_in_details", "")
                    if reason:
                        key = f"CHECK_IN: {reason}"
                        reasons_count[key] = reasons_count.get(key, 0) + 1

                for record in records_checkout:
                    reason = record.get("status_check_out_details", "")
                    if reason:
                        key = f"CHECK_OUT: {reason}"
                        reasons_count[key] = reasons_count.get(key, 0) + 1

                # Convert to list format
                reasons_list = [
                    {
                        "operation": op.split(":")[0],
                        "reason": op.split(":", 1)[1].strip(),
                        "count": count,
                    }
                    for op, count in sorted(
                        reasons_count.items(), key=lambda x: x[1], reverse=True
                    )
                ]

                async with self:
                    self.state_reasons = reasons_list
                    self.total_reasons_count = len(reasons_list)
                    self.reasons_current_page = 1
                return

            # Single operation query (check-in or check-out)
            records = list(
                collection.find(
                    {
                        "stat_type": statistics_type,
                        field: actual_state,
                        details_field: {"$exists": True, "$nin": [None, ""]},
                    },
                    {details_field: 1, "created_at": 1, "_id": 0},
                )
                .sort("created_at", -1)
                .limit(100)
            )

            # Count occurrences of each reason
            reasons_count = {}
            for record in records:
                reason = record.get(details_field, "")
                if reason:
                    reasons_count[reason] = reasons_count.get(reason, 0) + 1

            # Convert to list format sorted by count
            reasons_list = [
                {"operation": operation, "reason": reason, "count": count}
                for reason, count in sorted(
                    reasons_count.items(), key=lambda x: x[1], reverse=True
                )
            ]

            async with self:
                self.state_reasons = reasons_list
                self.total_reasons_count = len(reasons_list)
                self.reasons_current_page = 1

        except Exception as e:
            logger.error(f"Error fetching reasons for state {state}: {str(e)}")
            async with self:
                self.state_reasons = []
