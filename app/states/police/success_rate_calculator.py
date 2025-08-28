from typing import List, Dict, Any
from app.states.police.police_error_analyzer.analyzer import analyze_errors


def calculate_success_rate(
    states,
    success_states,
    error_states,
    docs: List[Dict[str, Any]] = None,
    police_type: str = None
) -> float:
    if docs is not None and police_type is not None:
        filtered_errors = analyze_errors(
            docs=docs,
            police_type=police_type,
            error_states=error_states
        )
        error_count = len(filtered_errors)
        success_count = sum(
            count for state, count in states.items() if state in success_states
        )
        denominator = success_count + error_count
        return (success_count / denominator * 100) if denominator > 0 else 0
    return 0.0
