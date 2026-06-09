from typing import Union, Dict, List

TAGS_MAPPING: Dict[str, Dict[str, Union[str, List[str]]]] = {
    "title": {"mp3": "TIT2", "m4b": "©nam"},
    "artist": {"mp3": "TPE1", "m4b": "©ART"},
    "album": {"mp3": "TALB", "m4b": "©alb"},
    "date": {"mp3": "TDRC", "m4b": "©day"},
    "track": {"mp3": "TRCK", "m4b": "trkn"},
    "genre": {"mp3": "TCON", "m4b": "©gen"},
    "comment": {"mp3": "COMM::eng", "m4b": "©cmt"},
    "album_artist": {"mp3": "TPE2", "m4b": "aART"},
    "composer": {"mp3": "TCOM", "m4b": "©wrt"},
    "disc": {"mp3": "TPOS", "m4b": "disk"},
    "compilation": {"mp3": "TCMP", "m4b": "cpil"},
    "description": {"mp3": "TXXX:DESCRIPTION", "m4b": "desc"},
    "synopsis": {"mp3": "TDES", "m4b": "ldes"},
    "language": {"mp3": "TLAN", "m4b": "----:com.apple.iTunes:LANGUAGE"},
    "copyright": {"mp3": "TCOP", "m4b": "cprt"},
    "series": {
        "mp3": "TXXX:SERIES",
        "m4b": [
            "----:com.apple.iTunes:SERIES",
            "----:com.apple.iTunes:series",
        ],
    },
    "series-part": {
        "mp3": "TXXX:SERIES-PART",
        "m4b": [
            "----:com.apple.iTunes:SERIES-PART",
            "----:com.apple.iTunes:series-part",
        ],
    },
    "lyrics": {"mp3": "TXXX:LYRICS", "m4b": "©lyr"},
    "publisher": {
        "mp3": "TPUB",
        "m4b": [
            "----:com.apple.iTunes:PUBLISHER",
            "----:com.apple.iTunes:publisher",
            "----:com.apple.iTunes:label",
            "©pub",
            "©wrp",
            "©prd",
        ],
    },
    "subtitle": {
        "mp3": ["TIT3"],
        "m4b": ["----:com.apple.iTunes:SUBTITLE", "©st3"],
    },
    "isbn": {"mp3": "TXXX:ISBN", "m4b": "----:com.apple.iTunes:ISBN"},
    "asin": {"mp3": "TXXX:ASIN", "m4b": "----:com.apple.iTunes:ASIN"},
    "encoded_by": {"mp3": "TENC", "m4b": "©enc"},
    "encoder": {"mp3": "TSSE", "m4b": "----:com.apple.iTunes:ENCODERSETTINGS"},
    "release_date": {"mp3": "TDRL", "m4b": "----:com.apple.iTunes:RELEASETIME"},
}
