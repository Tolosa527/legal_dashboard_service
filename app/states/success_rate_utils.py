from typing import List, Dict, Any
from app.states.statistics.analyzer import filter_expected_errors


def calculate_police_success_rate(
    success_count: int,
    error_states: List[str],
    docs: List[Dict[str, Any]] = None,
    police_type: str = None
) -> float:
    # Lazy import to avoid circular imports when modules that import this
    # utility also import police state modules.
    if docs is not None and police_type is not None:
        from app.states.police.analyzer import analyze_police_errors

        filtered_errors = analyze_police_errors(
            docs=docs,
            police_type=police_type,
            error_states=error_states,
        )
        error_count = len(filtered_errors)
        denominator = success_count + error_count
        return (success_count / denominator * 100) if denominator > 0 else 0
    return 0.0


def calculate_stat_success_rate(
    success_count: int,
    error_states: List[str],
    docs: List[Dict[str, Any]] = None,
    stat_type: str = None
) -> float:
    if docs is not None and stat_type is not None:
        errors = filter_expected_errors(
            docs=docs,
            stat_type=stat_type,
            error_states=error_states
        )
        error_count = len(errors)
        denominator = success_count + error_count
        return (success_count / denominator * 100) if denominator > 0 else 0
    return 0.0
