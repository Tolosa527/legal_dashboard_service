from dataclasses import dataclass

# Configurable constants for police data state

# State categories
IN_PROGRESS_STATES = ["NEW", "IN_PROGRESS", "PROGRESS"]
SUCCESS_STATES = ["SUCCESS", "CONFIRMED", "COMPLETE"]
ERROR_STATES = ["ERROR", "FAILED", "INVALID"]


@dataclass(frozen=True)
class SuccessRateThresholds:
    good: int = 90
    warning: int = 70


@dataclass(frozen=True)
class StatusLabel:
    good: str = "Good"
    warning: str = "Warning"
    error: str = "Error"


@dataclass(frozen=True)
class StatusColor:
    good: str = "green"
    warning: str = "orange"
    error: str = "red"


@dataclass(frozen=True)
class StatusIcon:
    good: str = "check"
    warning: str = "triangle-alert"
    error: str = "circle-x"


SUCCESS_RATE_THRESHOLDS = SuccessRateThresholds()
STATUS_LABELS = StatusLabel()
STATUS_COLORS = StatusColor()
STATUS_ICONS = StatusIcon()

# Cache timeout in seconds
CACHE_TIMEOUT = 300
