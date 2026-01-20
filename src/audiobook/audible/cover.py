import requests
from pathlib import Path


class AudibleCover:
    def __init__(self, url: str):
        self.url = url
        # Détermine dynamiquement le dossier "Downloads" de l'utilisateur
        self.download_path = Path.home() / "Downloads"

    def download(self, filename: str | None = None):
        """Télécharge l'image de la couverture dans le dossier Téléchargements."""
        try:
            # Si aucun nom n'est fourni, on extrait le nom du fichier depuis l'URL
            if not filename:
                filename = self.url.split("/")[-1].split("?")[0]
                if not filename:
                    filename = "audible_cover.jpg"

            target_path = self.download_path / filename

            # Requête pour récupérer l'image
            response = requests.get(self.url, stream=True, timeout=30)
            response.raise_for_status()  # Vérifie si le téléchargement a réussi

            # Écriture du fichier sur le disque
            with open(target_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Succès ! Image enregistrée sous : {target_path}")
            return target_path

        except requests.exceptions.RequestException as e:
            print(f"Erreur lors du téléchargement : {e}")
            return None
