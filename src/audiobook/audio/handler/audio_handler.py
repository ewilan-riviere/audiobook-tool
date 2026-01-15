"""Base media file handler"""

from typing import Optional
from abc import ABC, abstractmethod
from audiobook.audio.types import AudioTags


class AudioHandler(ABC):
    """Base media file handler"""

    @abstractmethod
    def extract(self, data: AudioTags) -> None:
        """Extract metadata as `AudioTags`"""

    @abstractmethod
    def inject(self, d: AudioTags) -> None:
        """Inject `AudioTags` to media file"""

    @abstractmethod
    def extract_cover(self) -> Optional[bytes]:
        """Extract cover as bytes"""

    @abstractmethod
    def inject_cover(self, img_data: bytes) -> bool:
        """Inject cover from bytes to media file"""

    @abstractmethod
    def has_cover(self) -> bool:
        """Check if media file has cover"""
