from typing import List, Dict, Any
from app.states.police.police_error_rules import (
    PoliceErrorRules,
    SpainHosErrorRules,
    SpainMosErrorRules,
    ItalyIspErrorRules
)


def get_error_rules_for_police_type(police_type: str) -> PoliceErrorRules:
    if police_type == "SPAIN_HOS":
        return SpainHosErrorRules()
    elif police_type == "MOS":
        return SpainMosErrorRules()
    # Add more police types here
    elif police_type == "ISP":
        return ItalyIspErrorRules()
    return PoliceErrorRules()


def analyze_police_errors(
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
                error_reason=reason, state=state)
        ):
            filtered.append(doc)
    return filtered
