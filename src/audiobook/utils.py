from pathlib import Path
import shutil
import os


def get_files(directory_path: str, extension: str) -> list[str]:
    """
    Recherche les fichiers avec une extension spécifique dans un dossier
    et retourne leurs chemins absolus.
    """
    # Nettoyage de l'extension pour s'assurer qu'elle commence par un point
    ext = extension if extension.startswith(".") else f".{extension}"

    # Création de l'objet Path
    root = Path(directory_path)

    if not root.is_dir():
        print(f"Le chemin {directory_path} n'est pas un dossier valide.")
        return []

    # root.glob(pattern) cherche dans le dossier
    # file.resolve() transforme le chemin relatif en chemin absolu
    return [str(file.resolve()) for file in root.glob(f"*{ext}")]


def move_files(liste_chemins: list[str], dossier_destination: str) -> None:
    """
    Déplace une liste de fichiers vers un dossier cible.

    :param liste_chemins: Liste des chemins absolus ou relatifs des fichiers.
    :param dossier_destination: Chemin du dossier où déplacer les fichiers.
    """
    # 1. Créer le dossier de destination s'il n'existe pas
    dest_path = Path(dossier_destination)
    dest_path.mkdir(parents=True, exist_ok=True)

    for chemin_str in liste_chemins:
        fichier_source = Path(chemin_str)

        # Vérifier si le fichier existe avant de tenter le déplacement
        if not fichier_source.is_file():
            print(f"⚠️ Fichier introuvable, ignoré : {fichier_source.name}")
            continue

        # 2. Définir le chemin de destination final (dossier + nom du fichier)
        fichier_destination = dest_path / fichier_source.name

        try:
            # 3. Déplacement
            shutil.move(str(fichier_source), str(fichier_destination))
            print(f"✅ Déplacé : {fichier_source.name} -> {dossier_destination}")
        except Exception as e:
            print(f"❌ Erreur lors du déplacement de {fichier_source.name} : {e}")


def rename_file(absolute_path: str, new_name: str) -> str:
    """
    Renomme un fichier en gardant son dossier d'origine et son extension.
    """
    path = Path(absolute_path)
    new_path = path.with_name(new_name + path.suffix)

    if new_path.exists():
        new_path.unlink()

    path.rename(new_path)

    return str(new_path.resolve())


def rename_directory(absolute_path: str, new_name: str) -> str:
    """
    Renomme un répertoire en gardant son emplacement d'origine.
    """
    path = Path(absolute_path)

    # On remplace simplement le dernier composant du chemin par le nouveau nom
    new_path = path.with_name(new_name)

    if new_path.exists():
        shutil.rmtree(new_path)

    # Renommage effectif
    path.rename(new_path)

    return str(new_path.resolve())


def delete_directory(directory_path: str | Path):
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)
        print(f"Delete {directory_path}")
    else:
        print(f"Directory {directory_path}")


def make_directory(directory_path: str | Path) -> Path:
    if not isinstance(directory_path, Path):
        directory_path = Path(directory_path)

    directory_path.mkdir(parents=True, exist_ok=True)

    return directory_path
