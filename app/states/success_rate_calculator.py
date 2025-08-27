from dataclasses import dataclass


@dataclass
class PoliceErrorReasonAnalysis:
    reason: str
    count: int


def calculate_success_rate(
    states, reason, in_progress_states, success_states, error_states
) -> float:
    error_count = sum(count for state, count in states.items() if state in error_states)
    completed_count = sum(
        count for state, count in states.items() if state not in in_progress_states
    )
    success_count = sum(
        count for state, count in states.items() if state in success_states
    )

    success_rate = (success_count / completed_count * 100) if completed_count > 0 else 0

    return success_rate
