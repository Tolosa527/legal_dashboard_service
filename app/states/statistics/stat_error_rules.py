from typing import Dict, Any


# --- Error Rules Mechanism ---
class StatErrorRules:
    def is_expected_error(self, error_reason: str, state: str, doc: Dict[str, Any]) -> bool:
        """Override in subclasses to define expected errors for each stat type."""
        return False