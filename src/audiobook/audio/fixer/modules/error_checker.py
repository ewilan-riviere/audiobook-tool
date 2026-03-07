"""Check errors if any in audio stream"""

from pathlib import Path
import subprocess

from audiobook.common import AutoRepr


class ErrorChecker(AutoRepr):
    """Check errors if any in audio stream"""

    # List of fatal errors that actually impact audio
    CRITICAL_PATTERNS = [
        "corrupt",
        "invalid data",
        "frame sync",
        "decoding error",
        "overread",
        "bitstream",
        "header missing",
        "checksum mismatch",
        "error submitting packet",
        "invalid data found",
        "misdetection possible",
        "conversion failed",
        "invalid audio stream",
    ]

    def __init__(self, original_path: Path, strict: bool, seconds_to_parse: int = 60):
        self.original_path: Path = original_path
        self.strict: bool = strict
        self.seconds_to_parse = seconds_to_parse
        self.errors: list[str] = []
        self.has_errors: bool = False

    def run(self):
        """Decode to null and analyze the stderr output"""

        # -v info to filter error
        # cmd = ["ffmpeg", "-v", "error", "-i", str(self.original_path), "-f", "null", "-"]
        cmd = [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(self.original_path),
            "-t",
            str(self.seconds_to_parse),
            "-f",
            "null",
            "-",
        ]

        try:
            # NOT set `check=True` here to analyze stderr even fails
            # pylint: disable=subprocess-run-check
            result = subprocess.run(
                cmd,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
            )
            raw_errors = result.stderr.strip()

            if not raw_errors:
                self.has_errors = False
                self.errors = []

                return self

            if self.strict:
                # Strict mode: if there is text in stderr with -v error, it is an error
                self.has_errors = True
                self.errors = raw_errors.split("\n")
            else:
                # Relaxed mode: check patterns without requiring the “[error]” tag
                critical_lines: list[str] = []
                for line in raw_errors.splitlines():
                    line_lower = line.lower()
                    if any(p in line_lower for p in self.CRITICAL_PATTERNS):
                        critical_lines.append(line)

                self.has_errors = len(critical_lines) > 0
                self.errors = critical_lines

        except Exception as e:  # pylint: disable=broad-exception-caught
            self.has_errors = True
            self.errors = [f"FFmpeg execution failed: {e}"]

        return self
