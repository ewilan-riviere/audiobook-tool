from typing import Optional, List, Any, Union, cast
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, ID3FileType
from mutagen.id3._frames import (
    TIT2,
    TIT3,
    TPE1,
    TPE2,
    TALB,
    TCOM,
    TCON,
    TDRC,
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
from audiobook.audio.types import AudioTags
from .audio_handler import AudioHandler


class MP3Handler(AudioHandler):
    def __init__(self, path: Union[str, Path]):
        self.path = str(path)

    def extract(self, data: AudioTags) -> None:
        audio = MP3(self.path, ID3=ID3)
        tags = audio.tags  # type: ignore

        if tags is None:
            return

        def safe_tag(key: str) -> Optional[str]:
            # tags.get(key) retourne un objet Frame, on prend son premier élément textuel
            # frame = tags.get(key)
            frame = cast(Optional[Any], tags.get(key))  # type: ignore
            return (
                str(frame.text[0])
                if frame and hasattr(frame, "text") and frame.text
                else None
            )

        # Mise à jour des champs simples
        data["title"] = safe_tag("TIT2")
        data["subtitle"] = safe_tag("TIT3")
        data["artist"] = safe_tag("TPE1")
        data["album_artist"] = safe_tag("TPE2")
        data["album"] = safe_tag("TALB")
        data["composer"] = safe_tag("TCOM")
        data["genre"] = safe_tag("TCON")
        data["year"] = safe_tag("TDRC") or safe_tag("TYER")
        data["track"] = safe_tag("TRCK")
        data["disc"] = safe_tag("TPOS")
        data["language"] = safe_tag("TLAN")
        data["publisher"] = safe_tag("TPUB")
        data["copyright"] = safe_tag("TCOP")

        # Compilation (booléen)
        tcmp_frame = tags.get("TCMP")  # type: ignore
        data["compilation"] = (
            True if tcmp_frame and "1" in str(tcmp_frame) else False  # type: ignore
        )

        # Commentaires (COMM)
        for c in tags.getall("COMM"):  # type: ignore
            if not isinstance(c, COMM):
                continue
            desc: str | None = c.desc.lower()  # type: ignore
            text_val = str(c.text[0]) if c.text else ""  # type: ignore

            if not desc:
                data["comment"] = text_val
            elif "description" in desc:
                data["description"] = text_val
            elif "synopsis" in desc:
                data["synopsis"] = text_val

        # Tags personnalisés (TXXX)
        for txxx in tags.getall("TXXX"):  # type: ignore
            if not isinstance(txxx, TXXX):
                continue
            k = txxx.desc.lower().replace("-", "_")  # type: ignore
            if k in data:
                # On utilise cast pour rassurer le type checker sur la clé
                data[k] = str(txxx.text[0]) if txxx.text else None  # type: ignore

    def inject(self, d: AudioTags) -> None:
        audio = MP3(self.path, ID3=ID3)
        if audio.tags is None:  # type: ignore
            audio.add_tags()  # type: ignore

        # On utilise ID3 comme type pour le cast
        t = cast(ID3, audio.tags)  # type: ignore

        mapping: dict[Any, str | int | None] = {
            TIT2: d.get("title"),
            TIT3: d.get("subtitle"),
            TPE1: d.get("artist"),
            TPE2: d.get("album_artist"),
            TALB: d.get("album"),
            TCOM: d.get("composer"),
            TCON: d.get("genre"),
            TDRC: d.get("year"),
            TRCK: d.get("track"),
            TPOS: d.get("disc"),
            TLAN: d.get("language"),
            TPUB: d.get("publisher"),
            TCOP: d.get("copyright"),
        }

        for cls, val in mapping.items():
            if val:
                # On force en str pour éviter les problèmes si val est un int
                t.add(cls(encoding=3, text=[str(val)]))  # type: ignore

        # Logique spécifique
        if d.get("compilation"):
            t.add(TCMP(encoding=3, text=["1"]))  # type: ignore
        else:
            t.delall("TCMP")  # type: ignore

        t.delall("COMM")  # type: ignore
        if d.get("comment"):
            t.add(COMM(encoding=3, lang="eng", desc="", text=[str(d["comment"])]))  # type: ignore
        if d.get("description"):
            t.add(  # type: ignore
                COMM(
                    encoding=3,
                    lang="eng",
                    desc="description",
                    text=[str(d["description"])],
                )
            )
        if d.get("synopsis"):
            t.add(  # type: ignore
                COMM(encoding=3, lang="eng", desc="synopsis", text=[str(d["synopsis"])])
            )

        # Séries et identifiants (TXXX)
        for key in ["series", "series_part", "isbn", "asin"]:
            val = d.get(key)  # type: ignore
            if val:
                t.add(TXXX(encoding=3, desc=key.replace("_", "-"), text=[str(val)]))  # type: ignore

        audio.save()  # type: ignore

    def extract_cover(self) -> Optional[bytes]:
        audio = MP3(self.path, ID3=ID3)
        if not audio.tags:  # type: ignore
            return None

        covers = cast(List[APIC], audio.tags.getall("APIC"))  # type: ignore
        if not covers:
            return None

        # Priorité à la Front Cover (type 3)
        cover = next((c for c in covers if c.type == 3), covers[0])  # type: ignore
        return cast(bytes, cover.data)  # type: ignore

    def inject_cover(self, img_data: bytes) -> bool:
        audio = MP3(self.path, ID3=ID3)
        if audio.tags is None:  # type: ignore
            audio.add_tags()  # type: ignore

        t = cast(ID3FileType, audio.tags)  # type: ignore
        mime = (
            "image/png" if img_data.startswith(b"\x89PNG\r\n\x1a\n") else "image/jpeg"
        )

        t.add(  # type: ignore
            APIC(
                encoding=3,
                mime=mime,
                type=3,
                desc="Front Cover",
                data=img_data,
            )
        )
        audio.save()  # type: ignore
        return True

    def has_cover(self) -> bool:
        try:
            audio = MP3(self.path, ID3=ID3)
            return (
                audio.tags is not None  # type: ignore
                and "APIC:" in audio.tags  # type: ignore
                or any(k.startswith("APIC") for k in audio.tags.keys())  # type: ignore
            )
        except Exception:
            return False
