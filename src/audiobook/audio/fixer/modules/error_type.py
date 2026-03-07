from enum import Enum


class ErrorType(Enum):
    """Fixer error type"""

    NONE = "No errors"
    REMUX = "Remux"
    TRANSCODE = "Transcode"
    NOT_FIXED = "Not fixed"
    UNKNOWN = "Unknown"
