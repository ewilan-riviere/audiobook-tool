import os
import subprocess
from mutagen.mp4 import MP4, MP4FreeForm, MP4Cover


class M4BHandler:
    def __init__(self, path):
        self.path = path

    def extract(self, data):
        audio = MP4(self.path)
        t = audio.tags
        if not t:
            return

        def get_m4b_str(keys):
            for k in keys:
                if k in t:
                    val = t[k][0] if isinstance(t[k], list) and len(t[k]) > 0 else t[k]
                    if isinstance(val, (bytes, bytearray, MP4FreeForm)):
                        return val.decode("utf-8", errors="ignore")
                    return str(val)
            return None

        # Fallbacks Description/Synopsis
        d_val = get_m4b_str(["\xa9des"])
        s_val = get_m4b_str(["lp83", "desc", "----:com.apple.iTunes:SYNOPSIS"])
        c_val = get_m4b_str(["\xa9cmt"])
        if not s_val:
            s_val = d_val
        if not d_val:
            d_val = s_val[:250] + "..." if s_val else None

        data.update(
            {
                "title": get_m4b_str(["\xa9nam"]),
                "subtitle": get_m4b_str(["\xa9st3", "----:com.apple.iTunes:SUBTITLE"]),
                "artist": get_m4b_str(["\xa9ART"]),
                "album_artist": get_m4b_str(["aART"]),
                "album": get_m4b_str(["\xa9alb"]),
                "composer": get_m4b_str(["\xa9wrt"]),
                "genre": get_m4b_str(["\xa9gen"]),
                "year": get_m4b_str(["\xa9day"]),
                "comment": c_val,
                "description": d_val,
                "synopsis": s_val,
                "language": get_m4b_str(["\xa9lan", "----:com.apple.iTunes:LANGUAGE"]),
                "copyright": get_m4b_str(["cprt"]),
                "publisher": get_m4b_str(["\xa9pub"]),
                "compilation": self._get_cpil_safe(t),
            }
        )

        # Deep Scan & Track/Disc
        for field, tag in [("track", "trkn"), ("disc", "disk")]:
            if tag in t:
                v = t[tag][0]
                if isinstance(v, tuple) and v[0] > 0:
                    data[field] = f"{v[0]}/{v[1]}"

        for k in t.keys():
            if k.startswith("----:com.apple.iTunes:"):
                atom = k.split(":")[-1].upper()
                val = get_m4b_str([k])
                if atom in ["SERIES", "WORK"]:
                    data["series"] = val
                elif atom in ["SERIES-PART", "MOVEMENT-NUMBER"]:
                    data["series_part"] = val
                elif atom == "ISBN":
                    data["isbn"] = val
                elif atom == "ASIN":
                    data["asin"] = val

    def _get_cpil_safe(self, t):
        if "cpil" in t:
            v = t["cpil"]
            return bool(v[0]) if isinstance(v, list) else bool(v)
        return False

    def inject(self, d):
        meta_file = f"{self.path}.ffmeta"
        temp_file = f"{self.path}.tmp.m4b"
        try:
            # 1. FFmpeg (Chapitres)
            with open(meta_file, "w", encoding="utf-8") as f:
                f.write(";FFMETADATA1\n")
                for ch in d.get("chapters", []):
                    f.write(
                        f"\n[CHAPTER]\nTIMEBASE={ch['time_base']}\nSTART={ch['start']}\nEND={ch['end']}\ntitle={ch['title']}\n"
                    )

            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    self.path,
                    "-i",
                    meta_file,
                    "-map_metadata",
                    "1",
                    "-map_chapters",
                    "1",
                    "-c",
                    "copy",
                    temp_file,
                    "-y",
                ],
                capture_output=True,
                check=True,
            )
            os.replace(temp_file, self.path)

            # 2. Mutagen (Tous les Tags)
            audio = MP4(self.path)
            t = audio.tags

            # Tags standards
            t["\xa9nam"] = [str(d.get("title") or "")]
            t["\xa9ART"] = [str(d.get("artist") or "")]
            t["aART"] = [str(d.get("album_artist") or "")]
            t["\xa9alb"] = [str(d.get("album") or "")]
            t["\xa9wrt"] = [str(d.get("composer") or "")]
            t["\xa9gen"] = [str(d.get("genre") or "")]
            t["\xa9day"] = [str(d.get("year") or "")]
            t["\xa9cmt"] = [str(d.get("comment") or "")]
            t["cprt"] = [str(d.get("copyright") or "")]
            t["\xa9pub"] = [str(d.get("publisher") or "")]
            t["\xa9lan"] = [str(d.get("language") or "")]
            t["cpil"] = [bool(d.get("compilation"))]

            # Track / Disc (CORRECTION ICI)
            for field, tag in [("track", "trkn"), ("disc", "disk")]:
                val = d.get(field)
                if val:
                    try:
                        if "/" in str(val):
                            curr, tot = str(val).split("/")
                            t[tag] = [(int(curr), int(tot))]
                        else:
                            t[tag] = [(int(val), 0)]
                    except:
                        pass

            if d.get("subtitle"):
                t["\xa9st3"] = [str(d["subtitle"])]
                t["----:com.apple.iTunes:SUBTITLE"] = [str(d["subtitle"]).encode()]

            if d.get("synopsis"):
                s = d["synopsis"]
                t["lp83"] = [s]
                t["desc"] = [s]
                t["\xa9des"] = [s[:250] + "..." if len(s) > 250 else s]

            for key in ["series", "series_part", "isbn", "asin"]:
                if d.get(key):
                    t[f"----:com.apple.iTunes:{key.upper().replace('_', '-')}"] = [
                        str(d[key]).encode()
                    ]

            audio.save()
        finally:
            for f in [meta_file, temp_file]:
                if os.path.exists(f):
                    os.remove(f)

    def extract_cover(self) -> Optional[bytes]:
        audio = MP4(self.path)
        if not audio.tags or "covr" not in audio.tags:
            return None
        # Retourne le binaire brut de la première image trouvée
        return bytes(audio.tags["covr"][0])

    def inject_cover(self, img_data: bytes) -> bool:
        audio = MP4(self.path)
        if not audio.tags:
            audio.add_tags()

        # Détection du format pour l'énumération MP4
        fmt = MP4Cover.FORMAT_JPEG
        if img_data.startswith(b"\x89PNG\r\n\x1a\n"):
            fmt = MP4Cover.FORMAT_PNG

        audio.tags["covr"] = [MP4Cover(img_data, imageformat=fmt)]
        audio.save()
        return True
