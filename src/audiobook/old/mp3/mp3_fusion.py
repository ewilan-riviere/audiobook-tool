import os
from collections import defaultdict
import subprocess
from pathlib import Path
from audiobook.metadata import MetadataFile
import audiobook.utils as utils
import json
import mutagen
from typing import Dict, Any
from mutagen.mp4 import MP4, MP4FreeForm
from mutagen.id3 import ID3, TXXX, CHAP, CTOC, Encoding
import mutagen.id3

MetadataDict = Dict[str, Dict[str, Any]]


class Mp3Fusion:
    def __init__(self, mp3_list: list[str]):
        self._mp3_list = mp3_list

        items: dict[str, str] = {}
        for path in self._mp3_list:
            file = MetadataFile(path)
            items.update({path: str(file.title)})

        grouped_data: dict[str, list[str]] = defaultdict(list)

        for filename, title in items.items():
            grouped_data[title].append(filename)

        for title, files in grouped_data.items():
            if len(files) > 1:
                self._fusion(files)

    def _fusion(self, files: list[str]):
        """
        Fusionne une liste de fichiers MP3 dans l'ordre de la liste.
        Conserve les métadonnées du premier fichier.
        """
        first_file = Path(files[0])
        first_file_no_ext = first_file.with_suffix("")
        output_file = f"{first_file_no_ext}_fusion.mp3"

        metadata = self._extract_metadata(str(first_file))
        print(metadata)

        if not files:
            print("La liste de fichiers est vide.")
            return

        # Nom du fichier temporaire pour la liste
        temp_list_file = "concat_list.txt"

        try:
            # 1. Création du fichier de configuration pour ffmpeg
            # On utilise l'encodage utf-8 pour gérer les accents dans les noms de fichiers
            with open(temp_list_file, "w", encoding="utf-8") as f:
                for file in files:
                    # On échappe les apostrophes si présentes dans le nom du fichier
                    path = file.replace("'", "'\\''")
                    f.write(f"file '{path}'\n")

            # 2. Commande FFmpeg
            command = [
                "ffmpeg",
                "-y",  # Ecrase le fichier de sortie s'il existe déjà
                "-f",
                "concat",  # Mode concaténation
                "-safe",
                "0",  # Autorise les chemins absolus ou complexes
                "-i",
                temp_list_file,
                "-c",
                "copy",  # Pas de ré-encodage (vitesse max, qualité préservée)
                "-map_metadata",
                "0",  # Copie les métadonnées (et atoms) du PREMIER fichier
                output_file,
            ]

            # Exécution (capture_output permet de voir les erreurs ffmpeg en cas de crash)
            subprocess.run(command, check=True, capture_output=True)
            print(f"✅ Fusion terminée avec succès : {output_file}")

        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur FFmpeg : {e.stderr.decode()}")
        finally:
            # 3. Nettoyage
            if os.path.exists(temp_list_file):
                os.remove(temp_list_file)

            for path in files:
                utils.delete_file(path)

            new_file = utils.copy_file(output_file, str(first_file))
            self._inject_metadata(new_file, metadata)
            utils.delete_file(output_file)

    def _extract_metadata(self, path: str) -> Dict[str, Dict[str, Any]]:
        # 1. Analyse structurelle (Atoms pour M4B / Frames pour MP3)
        # On demande à FFprobe de lister les 'entries' de métadonnées
        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-show_format",
            "-show_streams",
            "-show_chapters",
            "-print_format",
            "json",
            path,
        ]
        ff_data = json.loads(subprocess.check_output(cmd).decode("utf-8"))

        # 2. Analyse des Tags via Mutagen
        audio = mutagen.File(path)
        tags_extracted = {}

        if audio:
            # On convertit tout en string pour éviter les types 'Unknown'
            # Pour les M4B, Mutagen renverra les clés sous forme d'Atoms (ex: '©nam')
            # Pour les MP3, ce sera les clés ID3 (ex: 'TIT2')
            for key in audio.keys():
                val = audio[key]
                # Gestion des listes (souvent les tags sont des listes dans Mutagen)
                tags_extracted[str(key)] = (
                    val[0] if isinstance(val, list) and len(val) > 0 else str(val)
                )

        return {
            "structure": ff_data,  # Contient les chapitres du M4B et les flux
            "tags": tags_extracted,
        }

    def _inject_metadata(self, path: str, full_metadata_dict: Dict[str, Any]) -> bool:
        try:
            # On extrait la partie tags du dictionnaire
            tags_to_inject = full_metadata_dict.get("tags", {})
            audio = mutagen.File(path)

            if audio is None:
                return False

            # --- CAS MP4 / M4B (Atoms) ---
            if isinstance(audio, MP4):
                # Le format MP4 est plus souple sur les noms de clés
                for key, value in tags_to_inject.items():
                    try:
                        audio[key] = [value] if not isinstance(value, list) else value
                    except:
                        continue
                audio.save()

            # --- CAS MP3 (ID3) ---
            else:
                # On force la création/chargement du header ID3
                try:
                    tags = ID3(path)
                except mutagen.id3.ID3NoHeaderError:
                    tags = ID3()

                for key, value in tags_to_inject.items():
                    try:
                        # 1. Nettoyage de la clé (ex: 'TIT2:titre' -> 'TIT2')
                        base_key = key.split(":")[0]

                        # 2. Gestion des Tags Personnalisés (TXXX)
                        if base_key == "TXXX":
                            description = key.split(":", 1)[1] if ":" in key else ""
                            tags.add(
                                TXXX(
                                    encoding=Encoding.UTF8,
                                    desc=description,
                                    text=[str(value)],
                                )
                            )

                        # 3. Gestion des Frames Standards (TIT2, TPE1, etc.)
                        elif hasattr(mutagen.id3, base_key):
                            frame_class = getattr(mutagen.id3, base_key)
                            # On vérifie que c'est bien une classe de frame (et pas Encoding par ex)
                            if isinstance(frame_class, type):
                                tags.add(
                                    frame_class(
                                        encoding=Encoding.UTF8, text=[str(value)]
                                    )
                                )

                        # 4. On ignore CHAP et CTOC ici car ils nécessitent un parsing complexe
                        # de la structure temporelle extraite précédemment.

                    except Exception as e:
                        print(f"Erreur sur la clé {key}: {e}")

                tags.save(path, v2_version=3)  # v2.3 est souvent plus compatible

            print(f"Injection terminée pour : {path}")
            return True

        except Exception as e:
            print(f"Erreur critique lors de l'injection : {e}")
            return False
