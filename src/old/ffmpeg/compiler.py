from pathlib import Path
import ffmpeg  # type: ignore


class M4bCompiler:
    def __init__(self, files: list[str], output_file: str | None = None):
        """
        files: liste des chemins vers les fichiers M4B à fusionner
        output_file: chemin du fichier M4B final
                     si None, sera créé dans le parent du dossier 'm4b' du premier fichier
                     avec le nom 'final_book.m4b'
        """
        # Filtrer uniquement les fichiers M4B valides
        self.files = [Path(f) for f in files if Path(f).suffix.lower() == ".m4b"]
        if not self.files:
            raise ValueError("Aucun fichier M4B valide fourni.")

        # Déterminer le dossier m4b du premier fichier
        m4b_folder = self.files[0].parent

        # Si output_file non fourni, créer dans le parent du folder m4b
        if output_file is None:
            self.output_file = m4b_folder.parent / "final_book.m4b"
        else:
            self.output_file = Path(output_file)

    def compile(self):
        """
        Compile tous les fichiers M4B en un seul M4B final.
        """
        # Créer un fichier temporaire list.txt pour ffmpeg concat
        list_file = self.output_file.parent / "m4b_list.txt"
        with open(list_file, "w", encoding="utf-8") as f:
            for m4b in self.files:
                # ffmpeg concat nécessite des paths entourés de quotes
                f.write(f"file '{m4b.resolve()}'\n")

        # Supprimer le fichier final s'il existe déjà
        if self.output_file.exists():
            print(f"Suppression de l'ancien fichier : {self.output_file}")
            self.output_file.unlink()

        try:
            print(
                f"Compilation de {len(self.files)} fichiers en {self.output_file.name} ..."
            )
            stream = ffmpeg.input(str(list_file), format="concat", safe=0)  # type: ignore
            stream = ffmpeg.output(stream, str(self.output_file), c="copy")  # type: ignore
            ffmpeg.run(stream, overwrite_output=True, quiet=True)  # type: ignore

            print(f"Compilation terminée : {self.output_file}")

        except ffmpeg.Error as e:
            error_msg = e.stderr.decode(errors="ignore") if e.stderr else str(e)  # type: ignore
            print(f"FFmpeg error : {error_msg}")

        finally:
            # Nettoyage du fichier temporaire
            if list_file.exists():
                list_file.unlink()
