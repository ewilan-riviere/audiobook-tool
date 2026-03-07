from enum import Enum


class AudioType(Enum):
    """Audio file type"""

    MP3 = "mp3"
    M4A = "m4a"
    M4B = "m4b"
    UNKNOWN = "unknown"

    @classmethod
    def from_extension(cls, extension: str) -> "AudioType":
        """
        Maps a string extension to an AudioType.
        Handles leading dots and case sensitivity.
        """
        normalized_ext = extension.lower().lstrip(".")

        try:
            return cls(normalized_ext)
        except ValueError:
            return cls.UNKNOWN
