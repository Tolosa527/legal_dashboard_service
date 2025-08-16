import os
import reflex as rx
from services.police_data_mongo_service import PoliceDataMongoService
from database_manager import DatabaseManager


class PoliceDataState(rx.State):
    """State to manage police data."""
    police_data: list[dict] = []
    loading: bool = True
    error_message: str = ""

    @rx.event(background=True)
    async def fetch_police_data(self):
        """Fetch police data from the service."""
        mongo_host = os.getenv('MONGO_HOST', 'localhost')
        mongo_port = int(os.getenv('MONGO_PORT', '27017'))
        mongo_db = os.getenv('MONGO_DB', 'legal_dashboard')
        mongo_username = os.getenv('MONGO_USERNAME')
        mongo_password = os.getenv('MONGO_PASSWORD')

        # Create database connection
        db_manager = DatabaseManager()
        db_manager.connect_mongo(
            host=mongo_host,
            port=mongo_port,
            database=mongo_db,
            username=mongo_username,
            password=mongo_password
        )
        
        # Create service locally (not as state variable to avoid serialization issues)
        police_data_service = PoliceDataMongoService(db_manager=db_manager)
        
        # Use context manager to modify state in background task
        async with self:
            if police_data_service:
                police_data = police_data_service.get_all_police_data()
                # Convert UnifiedPoliceData objects to dictionaries for state storage
                self.police_data = [data.to_mongo_dict() for data in police_data]
            self.loading = False

    @rx.var
    def get_police_data(self) -> list[dict]:
        """Return the police data."""
        return self.police_data
    
    @rx.var
    def get_police_state_chart_data(self) -> list[dict]:
        """Get police data aggregated by state for pie chart."""
        if not self.police_data:
            return []
        
        # Count occurrences of each state
        state_counts = {}
        for data in self.police_data:
            state = data.get("state", "Unknown")
            state_counts[state] = state_counts.get(state, 0) + 1
        
        # Convert to chart format
        return [{"name": state, "value": count} for state, count in state_counts.items()]
    
    @rx.var
    def get_police_type_chart_data(self) -> list[dict]:
        """Get police data aggregated by police type for pie chart."""
        if not self.police_data:
            return []
        
        # Count occurrences of each police type
        type_counts = {}
        for data in self.police_data:
            police_type = data.get("police_type", "Unknown")
            type_counts[police_type] = type_counts.get(police_type, 0) + 1
        
        # Convert to chart format
        return [{"name": police_type, "value": count} for police_type, count in type_counts.items()]
    
    @rx.var
    def get_total_records(self) -> int:
        """Get total number of police records."""
        return len(self.police_data)
    
    @rx.var
    def get_success_rate(self) -> float:
        """Get success rate percentage."""
        if not self.police_data:
            return 0.0
        
        # Define states that should be excluded from success rate calculation (in-progress states)
        in_progress_states = ["NEW", "IN_PROGRESS", "PROGRESS"]
        
        # Count only completed entries (exclude in-progress states)
        completed_entries = [data for data in self.police_data if data.get("state") not in in_progress_states]
        
        if not completed_entries:
            return 0.0
        
        # Consider both SUCCESS, CONFIRMED, and COMPLETE as successful states
        success_states = ["SUCCESS", "CONFIRMED", "COMPLETE"]
        success_count = sum(1 for data in completed_entries if data.get("state") in success_states)
        
        return round((success_count / len(completed_entries)) * 100, 1)
    
    @rx.var
    def get_error_count(self) -> int:
        """Get count of error records."""
        return sum(1 for data in self.police_data if data.get("state") == "ERROR")
    
    @rx.var
    def get_active_types(self) -> int:
        """Get number of different police types."""
        if not self.police_data:
            return 0
        
        unique_types = set(data.get("police_type", "Unknown") for data in self.police_data)
        return len(unique_types)
    
    @rx.var
    def get_service_status(self) -> str:
        """Get service status based on success rate thresholds."""
        success_rate = self.get_success_rate
        
        if success_rate >= 90:
            return "Good"
        elif success_rate >= 70:
            return "Warning"
        else:
            return "Error"
    
    @rx.var
    def get_service_status_color(self) -> str:
        """Get service status color."""
        status = self.get_service_status
        if status == "Good":
            return "green"
        elif status == "Warning":
            return "orange"
        else:
            return "red"
    
    @rx.var
    def get_service_status_icon(self) -> str:
        """Get service status icon."""
        status = self.get_service_status
        if status == "Good":
            return "circle-check"
        elif status == "Warning":
            return "triangle-alert"
        else:
            return "circle-x"
    
    @rx.var
    def get_police_type_status(self) -> list[dict]:
        """Get service status for each police type."""
        if not self.police_data:
            return []
        
        # Define states that should be excluded from success rate calculation (in-progress states)
        in_progress_states = ["NEW", "IN_PROGRESS", "PROGRESS"]
        
        # Group data by police type and calculate success rates
        type_stats = {}
        for data in self.police_data:
            police_type = data.get("police_type", "Unknown")
            state = data.get("state", "Unknown")
            
            # Skip in-progress states for success rate calculation
            if state in in_progress_states:
                continue
            
            if police_type not in type_stats:
                type_stats[police_type] = {"total": 0, "success": 0}
            
            type_stats[police_type]["total"] += 1
            # Consider both SUCCESS, CONFIRMED, and COMPLETE as successful states
            if state in ["SUCCESS", "CONFIRMED", "COMPLETE"]:
                type_stats[police_type]["success"] += 1
        
        # Calculate status for each type
        result = []
        for police_type, stats in type_stats.items():
            if stats["total"] > 0:
                success_rate = (stats["success"] / stats["total"]) * 100
                
                if success_rate >= 90:
                    status = "Good"
                    color = "green"
                    icon = "circle-check"
                elif success_rate >= 70:
                    status = "Warning"
                    color = "orange"
                    icon = "triangle-alert"
                else:
                    status = "Error"
                    color = "red"
                    icon = "circle-x"
                
                result.append({
                    "type": police_type,
                    "status": status,
                    "color": color,
                    "icon": icon,
                    "success_rate": round(success_rate, 1),
                    "total_records": stats["total"],
                    "success_records": stats["success"]
                })
        
        return sorted(result, key=lambda x: x["success_rate"], reverse=True)