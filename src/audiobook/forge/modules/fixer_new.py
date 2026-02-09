import subprocess
import logging
from pathlib import Path
from typing import List, Optional

# Imports spécifiques pour éviter les warnings de typage
from mutagen import MutagenError
from mutagen.mp4 import MP4, error as MP4Error

# On suppose que cet utilitaire existe dans ton projet
import audiobook.utils as utils

# Configuration pro du logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


class BlacksmithFixer:
    """
    Répare et normalise les fichiers M4B via FFmpeg et valide avec Mutagen.
    """

    def __init__(self, input_path: str | Path):
        self.input_path = Path(input_path).resolve()
        # On définit le chemin de sortie dès le début
        self.output_path = self.input_path.with_name(
            f"{self.input_path.stem}_fixed.m4b"
        )
        self.success = False

        if not self.input_path.exists():
            raise FileNotFoundError(f"Fichier source introuvable : {self.input_path}")

    def _get_ffmpeg_cmd(self, strip_metadata: bool = False) -> List[str]:
        """Génère la commande FFmpeg sans duplication de code."""
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(self.input_path),
            "-map",
            "0:a",  # Sélectionne l'audio
            "-map_chapters",
            "0",  # Préserve les chapitres
            "-c",
            "copy",  # Copie directe sans ré-encodage
            "-f",
            "mp4",
            "-movflags",
            "+faststart",  # Optimise l'index (moov atom)
            "-metadata",
            f"title={self.input_path.stem}",
            "-loglevel",
            "error",
        ]

        if strip_metadata:
            # Mode survie : on supprime les métadonnées globales corrompues
            cmd.extend(["-map_metadata", "-1"])

        cmd.append(str(self.output_path))
        return cmd

    def _try_repair(self, fallback: bool = False) -> bool:
        """Exécute l'appel système FFmpeg avec gestion d'erreurs."""
        mode = "STRIPPED" if fallback else "STANDARD"
        logger.info("Tentative de réparation (%s) : %s", mode, self.input_path.name)

        try:
            # Ajout d'un timeout de 5min pour éviter les processus fantômes
            subprocess.run(self._get_ffmpeg_cmd(fallback), check=True, timeout=300)
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logger.warning("Échec de la réparation %s : %s", mode, e)
            return False

    def _validate_with_mutagen(self) -> bool:
        """Vérifie si le fichier final est lisible par Mutagen."""
        if not self.output_path.exists():
            return False

        try:
            audio = MP4(self.output_path)
            # On force la lecture d'une info technique pour valider le header
            _ = audio.info.length
            logger.info("Validation Mutagen réussie.")
            return True
        except (MP4Error, MutagenError, IOError) as e:
            logger.error("Le fichier généré reste invalide : %s", e)
            return False

    def run(self) -> bool:
        """Point d'entrée principal du workflow."""
        # 1. Tentative standard
        if not self._try_repair(fallback=False):
            # 2. Tentative de secours
            if not self._try_repair(fallback=True):
                logger.critical("Réparation impossible pour : %s", self.input_path.name)
                return False

        # 3. Validation et finalisation
        if self._validate_with_mutagen():
            try:
                utils.rename_file(str(self.output_path), self.input_path.stem)
                self.success = True
                logger.info("🚀 Réparation terminée avec succès.")
            except Exception as e:
                logger.error("Erreur lors du renommage final : %s", e)
        else:
            # Nettoyage en cas d'échec de validation
            if self.output_path.exists():
                self.output_path.unlink()

        return self.success
