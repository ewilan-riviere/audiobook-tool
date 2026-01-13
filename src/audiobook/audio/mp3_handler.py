from mutagen.mp3 import MP3
from mutagen.id3 import (
    ID3,
    TIT2,
    TIT3,
    TPE1,
    TPE2,
    TALB,
    TCOM,
    TCON,
    TDRC,
    TYER,
    TRCK,
    TPOS,
    COMM,
    TPUB,
    TCOP,
    TXXX,
    TLAN,
    TCMP,
    APIC,
)


class MP3Handler:
    def __init__(self, path):
        self.path = path

    def extract(self, data):
        audio = MP3(self.path, ID3=ID3)
        tags = audio.tags
        if not tags:
            return

        def safe_tag(key):
            return str(tags.get(key, "")) or None

        data.update(
            {
                "title": safe_tag("TIT2"),
                "subtitle": safe_tag("TIT3"),
                "artist": safe_tag("TPE1"),
                "album_artist": safe_tag("TPE2"),
                "album": safe_tag("TALB"),
                "composer": safe_tag("TCOM"),
                "genre": safe_tag("TCON"),
                "year": safe_tag("TDRC") or safe_tag("TYER"),
                "track": safe_tag("TRCK"),
                "disc": safe_tag("TPOS"),
                "language": safe_tag("TLAN"),
                "publisher": safe_tag("TPUB"),
                "copyright": safe_tag("TCOP"),
                "compilation": (
                    True if tags.get("TCMP") and "1" in str(tags.get("TCMP")) else False
                ),
            }
        )
        for c in tags.getall("COMM"):
            desc = c.desc.lower()
            if not desc:
                data["comment"] = str(c.text[0])
            elif "description" in desc:
                data["description"] = str(c.text[0])
            elif "synopsis" in desc:
                data["synopsis"] = str(c.text[0])
        for txxx in tags.getall("TXXX"):
            k = txxx.desc.lower().replace("-", "_")
            if k in data:
                data[k] = str(txxx.text[0])

    def inject(self, d):
        audio = MP3(self.path, ID3=ID3)
        if not audio.tags:
            audio.add_tags()
        t = audio.tags
        mapping = {
            TIT2: d["title"],
            TIT3: d["subtitle"],
            TPE1: d["artist"],
            TPE2: d["album_artist"],
            TALB: d["album"],
            TCOM: d["composer"],
            TCON: d["genre"],
            TDRC: d["year"],
            TRCK: d["track"],
            TPOS: d["disc"],
            TLAN: d["language"],
            TPUB: d["publisher"],
            TCOP: d["copyright"],
        }
        for cls, val in mapping.items():
            if val:
                t.add(cls(encoding=3, text=[str(val)]))
        if d["compilation"]:
            t.add(TCMP(encoding=3, text=["1"]))
        else:
            t.delall("TCMP")
        t.delall("COMM")
        if d["comment"]:
            t.add(COMM(encoding=3, lang="eng", desc="", text=[d["comment"]]))
        if d["description"]:
            t.add(
                COMM(
                    encoding=3, lang="eng", desc="description", text=[d["description"]]
                )
            )
        if d["synopsis"]:
            t.add(COMM(encoding=3, lang="eng", desc="synopsis", text=[d["synopsis"]]))
        for key in ["series", "series_part", "isbn", "asin"]:
            if d.get(key):
                t.add(TXXX(encoding=3, desc=key.replace("_", "-"), text=[str(d[key])]))
        audio.save()

    def extract_cover(self) -> Optional[bytes]:
        audio = MP3(self.path, ID3=ID3)
        if not audio.tags:
            return None
        covers = audio.tags.getall("APIC")
        if not covers:
            return None

        # Priorité à la Front Cover (type 3)
        cover = next((c for c in covers if c.type == 3), covers[0])
        return cover.data

    def inject_cover(self, img_data: bytes) -> bool:
        audio = MP3(self.path, ID3=ID3)
        if not audio.tags:
            audio.add_tags()

        # Détection du type mime via signature binaire magique
        mime = "image/jpeg"
        if img_data.startswith(b"\x89PNG\r\n\x1a\n"):
            mime = "image/png"

        audio.tags.add(
            APIC(encoding=3, mime=mime, type=3, desc="Front Cover", data=img_data)
        )
        audio.save()
        return True
