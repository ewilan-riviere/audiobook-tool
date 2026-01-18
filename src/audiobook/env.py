"""Get variables from .env"""

import os
from dotenv import load_dotenv

load_dotenv()

PART_SIZE = int(os.environ.get("PART_SIZE", 500))
