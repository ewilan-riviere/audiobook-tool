"""Properties of audio file"""

from datetime import timedelta
from audiobook.utils import AutoRepr
from .mutagen import MutagenReader


class AudioProperties(AutoRepr):
    """Properties of audio file"""

    def __init__(self, path: str):
        reader = MutagenReader(path)

        length = reader.properties["length"]
        bitrate = reader.properties["bitrate"]
        sample_rate = reader.properties["sample_rate"]
        channels = reader.properties["channels"]
        codec = reader.properties["codec"]
        format_type = reader.properties["format_type"]
        format_label = reader.properties["format_label"]
        channels = reader.properties["channels"]
        channel_layout = reader.properties["channel_layout"]

        self.duration: float | None = None  # 10.0
        self.bit_rate: int | None = None  # 128000
        self.codec: str | None = codec  # mp3
        self.sample_rate: int | None = None  # 48000
        self.channels: int | None = None  # 2
        self.channel_layout: str | None = channel_layout  # stereo
        self.format_type: str | None = format_type  # mov,mp4,m4a,3gp,3g2,mj2
        self.format_label: str | None = format_label  # QuickTime / MOV

        if length:
            self.duration = float(length)
        if bitrate:
            self.bit_rate = int(bitrate)
        if sample_rate:
            self.sample_rate = int(sample_rate)
        if channels:
            self.channels = int(channels)

    @property
    def duration_human(self) -> str | None:
        """Get human readable duration"""
        if self.duration:
            return str(timedelta(seconds=int(self.duration)))

        return None
