"""Forge audiobook from MP3 to M4B"""

from pathlib import Path
import audiobook.utils as utils
from audiobook.common import AutoRepr
from .blacksmith import AudiobookBlacksmith


class AudiobookForge(AutoRepr):
    """Forge audiobook from MP3 to M4B"""

    _source_path: Path
    _working_directory: Path
    _bytes: int = 0
    _clear: bool = False
    _output_path: Path | None = None

    def __init__(self, source_path: Path, working_directory: Path, clear: bool = False):
        self._source_path = source_path.resolve()
        self._working_directory = working_directory.resolve()

        self._clear = clear

    @property
    def output_path(self) -> Path | None:
        """Get M4B file path"""
        if self._output_path:
            return self._output_path.resolve()

        return None

    @property
    def size_human(self) -> str:
        """Get M4B file size"""
        return utils.size_human_readable(self._bytes)

    def _calculate_size(self):
        if self._output_path and Path(self._output_path).is_file():
            self._bytes = utils.get_file_size(self._output_path)

    def run(self, output_path: Path | str | None = None):
        """Execute build command"""

        blacksmith = AudiobookBlacksmith(
            self._source_path,
            self._working_directory,
        ).run()
        self._output_path = blacksmith.output_path
        if output_path and self._output_path:
            self._output_path = Path(output_path).resolve() / self._output_path.name
            utils.make_directory(self._output_path.parent)
            utils.copy_file(str(blacksmith.output_path), self._output_path)

        self._calculate_size()

        return self
