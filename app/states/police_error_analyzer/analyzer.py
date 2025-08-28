from typing import List, Dict, Any


# --- Error Rules Mechanism ---
class PoliceErrorRules:
    def is_expected_error(self, error_reason: str, state: str, doc: Dict[str, Any]) -> bool:
        """Override in subclasses to define expected errors for each police type."""
        return False


class SpainHosErrorRules(PoliceErrorRules):
    # Example: treat INVALID with specific reason as expected
    EXPECTED_INVALID_REASONS = [
        (
            "Fields 'leader guest phone' and 'invite email': one of these is "
            "required for booking registration."
        ),
        "Field 'leader guest name' is required for booking registration.",
        "Invalid name format. Name and first surname are required.",
        "El nombre contiene caracteres no permitidos.",
        # Add more as needed from new validation errors
    ]

    def is_expected_error(
        self, error_reason: str, state: str, doc: Dict[str, Any]
    ) -> bool:
        if (
            state == "INVALID"
            and any(
                msg in error_reason
                for msg in self.EXPECTED_INVALID_REASONS
            )
        ):
            return True
        return False


class SpainMosErrorRules(PoliceErrorRules):
    EXPECTED_INVALID_REASONS = [
        "Validation error",
        "Postal code does not match expected format",
        "Contains non-printable characters",
        "Field length incorrect",
        "Conté caracters no imprimibles",
        # Add more as needed from new validation errors
    ]

    def is_expected_error(
        self, error_reason: str, state: str, doc: Dict[str, Any]
    ) -> bool:
        if (
            state in ["ERROR", "INVALID"]
            and any(
                msg in error_reason
                for msg in self.EXPECTED_INVALID_REASONS
            )
        ):
            return True
        return False


def get_error_rules_for_police_type(police_type: str) -> PoliceErrorRules:
    if police_type == "SPAIN_HOS":
        return SpainHosErrorRules()
    elif police_type == "MOS":
        return SpainMosErrorRules()
    # Add more police types here
    return PoliceErrorRules()


def analyze_errors(
    docs: List[Dict[str, Any]],
    police_type: str,
    error_states: List[str],
) -> List[Dict[str, Any]]:
    rules = get_error_rules_for_police_type(police_type)
    filtered = []
    for doc in docs:
        state = doc.get("state")
        reason = doc.get("reason", "")
        if (
            state in error_states
            and not rules.is_expected_error(
                error_reason=reason, state=state, doc=doc)
        ):
            filtered.append(doc)
    return filtered
