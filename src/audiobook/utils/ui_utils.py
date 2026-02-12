from typing import Any
from rich import print as rprint


def confirm_action(msg: str = "Do you want to continue?"):
    """Ask to user before continue"""
    while True:
        # .lower() makes it case-insensitive
        choice = input(f"{msg} (Y/n): ").lower().strip()

        # If user presses Enter without typing, default to 'yes'
        if choice in ["y", "yes", ""]:
            return True
        elif choice in ["n", "no"]:
            return False
        else:
            print("Please enter 'y' or 'n'.")


def rprint_(*objects: Any):
    """Print as rich format"""
    rprint(*objects)


def format_duration(seconds: float, short: bool = False) -> str:
    """Convert seconds to human readable duration"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        d = f"{h}h {m:02}m {s:02}s"
        if short:
            return _format_duration_short(d)
        return d

    d = f"{m:02}m {s:02}s"
    if short:
        return _format_duration_short(d)
    return d


def _format_duration_short(duration: str) -> str:
    return duration.replace(" ", ":").replace("h", "").replace("m", "").replace("s", "")
