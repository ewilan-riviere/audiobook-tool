"""Mixin to add an automatic `__repr__` to classes"""

from typing import Any
from datetime import datetime


class AutoRepr:
    """Mixin to add an automatic `__repr__` to classes"""

    def __repr__(self):
        def format_val(v: Any):
            # If the value is a datetime, format it as a string.
            if isinstance(v, datetime):
                return f"'{v.strftime('%Y-%m-%d %H:%M:%S')}'"
            # Otherwise, use the standard format (!r adds quotation marks if necessary).
            return repr(v)

        # We generate the list of attributes
        attributes = [f"{k}={format_val(v)}" for k, v in self.__dict__.items()]

        # Returns the class name with formatted attributes
        return f"{self.__class__.__name__}(\n  " + ",\n  ".join(attributes) + "\n)"
