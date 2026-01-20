"""Get variables from .env"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

PART_SIZE = int(os.environ.get("PART_SIZE", 500))


def python_check() -> None:
    """Check Python version"""
    version_min = (3, 12)
    if sys.version_info < version_min:
        sys.stderr.write(
            f"Error: Python {version_min[0]}.{version_min[1]} or later required.\n"
        )
        sys.exit(1)
