from typing import List, Dict, Any

from app.states.statistics.stat_error_rules import StatErrorRules


def get_error_rules_for_stat_type(stat_type: str) -> StatErrorRules:
    # This function should return the error rules for the given stat type
    return StatErrorRules()  # Placeholder implementation


def filter_expected_errors(
    docs: List[Dict[str, Any]],
    stat_type: str,
    error_states: List[str],
) -> List[Dict[str, Any]]:
    rules = get_error_rules_for_stat_type(stat_type)
    filtered = []
    for doc in docs:
        check_in_status = doc.get("status_check_in")
        check_out_status = doc.get("status_check_out")
        reason_check_in = doc.get("status_check_in_details", "")
        reason_check_out = doc.get("status_check_out_details", "")
        if (
            check_in_status in error_states
            and not rules.is_expected_error(
                error_reason=reason_check_in, state=check_in_status)
        ):
            filtered.append(doc)
        if (
            check_out_status in error_states
            and not rules.is_expected_error(
                error_reason=reason_check_out, state=check_out_status)
        ):
            filtered.append(doc)
    return filtered
