from pathlib import Path
import shutil
from typing import Optional, Union
import os
import platform
import subprocess
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3


def path_join(base_path: str, *add_paths: str):
    """Join paths to get valid OS path"""
    return os.path.join(base_path, *add_paths)


def path_exists(path: str | Path) -> bool:
    """Check if path exists"""
    if isinstance(path, str):
        path = Path(path)

    if path.exists():
        return True

    return False


def alert_sound():
    current_os = platform.system()

    if current_os == "Windows":
        try:
            import winsound  # pylint: disable=import-outside-toplevel

            # Note: winsound.Beep est bloquant par nature.
            # Pour Windows, on utilise PlaySound avec le flag SND_ASYNC
            winsound.PlaySound(  # type: ignore
                "SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC  # type: ignore
            )
        except ImportError:
            print("\a")

    elif current_os == "Darwin":  # macOS
        try:
            # Popen ne bloque pas le script
            subprocess.Popen(["afplay", "/System/Library/Sounds/Glass.aiff"])
        except FileNotFoundError:
            print("\a")

    elif current_os == "Linux":
        try:
            # Utilisation de Popen ici aussi
            subprocess.Popen(["canberra-gtk-play", "--id", "message-new-instant"])
        except FileNotFoundError:
            print("\x07", end="", flush=True)

    else:
        print("\a")


def get_mp3_title(filepath: str) -> str:
    """
    Extracts the title from an MP3 file's metadata.
    Returns the filename (without extension) if no title tag is found.
    """
    if not Path(filepath).exists():
        print(f"MP3 file not exists at {filepath}")
        return filepath

    try:
        # EasyID3 handles standard tags like 'title', 'artist', etc., very simply
        audio = EasyID3(filepath)

        if "title" in audio and audio["title"][0]:
            return audio["title"][0]  # type: ignore

    except Exception:
        # Fallback if EasyID3 fails (e.g., no ID3 tags present)
        try:
            audio = MP3(filepath)
            # Some files might have different tag structures
            if audio.tags and "TIT2" in audio.tags:  # type: ignore
                return str(audio.tags["TIT2"])  # type: ignore
        except Exception:
            pass

    # Final fallback: return the filename without extension
    return os.path.splitext(os.path.basename(filepath))[0]


def size_human_readable(size_bytes: int) -> str:
    """Return size as `str` human readable from bytes"""
    if size_bytes == 0:
        return "0 B"
    units = ("B", "KB", "MB", "GB", "TB")
    i = 0
    current_size = float(size_bytes)
    while current_size >= 1024 and i < len(units) - 1:
        current_size /= 1024
        i += 1
    return f"{current_size:.2f} {units[i]}".replace(".00", "")


def format_duration(seconds: float, short: bool = False) -> str:
    """Convert seconds to human readable duration"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        d = f"{h}h {m:02}m {s:02}s"
        if short:
            return _format_duration_short(d)
        return d

    d = f"{m:02}m {s:02}s"
    if short:
        return _format_duration_short(d)
    return d


def _format_duration_short(duration: str) -> str:
    return duration.replace(" ", ":").replace("h", "").replace("m", "").replace("s", "")


def get_file_size(path: str) -> int:
    """Get file size as bytes from path of file"""
    if Path(path).is_file():
        return os.path.getsize(path)
    else:
        print(f"ERROR: file not found at {path}")

    return 0


def get_file(directory_path: str, extension: str) -> Optional[str]:
    """Find first file with extension in directory_path"""
    listing = get_files(directory_path, extension)
    if len(listing) > 0:
        return listing[0]

    return None


def get_files(directory_path: str, extension: str, printing: bool = False) -> list[str]:
    """
    Recherche les fichiers avec une extension spécifique dans un dossier,
    les trie alphanumériquement et retourne leurs chemins absolus.
    """
    ext = extension if extension.startswith(".") else f".{extension}"
    root = Path(directory_path)

    if not root.is_dir():
        if printing:
            print(f"Le chemin {directory_path} n'est pas un dossier valide.")
        return []

    # On récupère les chemins absolus dans une liste
    files = [str(file.resolve()) for file in root.glob(f"*{ext}")]

    # On retourne la liste triée alphanumériquement
    return sorted(files)


def move_files(paths: list[str], path_to_move: str) -> None:
    """
    Déplace une liste de fichiers vers un dossier cible.

    :param paths: Liste des chemins absolus ou relatifs des fichiers.
    :param path_to_move: Chemin du dossier où déplacer les fichiers.
    """
    # 1. Créer le dossier de destination s'il n'existe pas
    dest_path = Path(path_to_move)
    dest_path.mkdir(parents=True, exist_ok=True)
    print(dest_path)

    for path in paths:
        fichier_source = Path(path)

        # Vérifier si le fichier existe avant de tenter le déplacement
        if not fichier_source.is_file():
            print(f"⚠️ File not found, ignored: {fichier_source.name}")
            continue

        # 2. Définir le chemin de destination final (dossier + nom du fichier)
        fichier_destination = dest_path / fichier_source.name

        try:
            # 3. Déplacement
            shutil.move(str(fichier_source), str(fichier_destination))
            # print(f"✅ Moved: {fichier_source.name} -> {path_to_move}")
            print(f"✅ Moved: {fichier_source.name}")
        except Exception as e:
            print(f"❌ Error while moving {fichier_source.name} : {e}")


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


def copy_file(from_path: str, to_path: str) -> str:
    """Copy file"""
    return shutil.copy(from_path, to_path)


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


def delete_directory(directory_path: str | Path, printing: bool = False):
    """Delete directory"""
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)
        if printing:
            print(f"Delete {directory_path}")
    else:
        if printing:
            print(f"Directory {directory_path} not exists")


def file_exists(path: Union[str, Path]) -> bool:
    """
    Vérifie si un fichier existe à l'emplacement donné.

    Args:
        path: Le chemin du fichier (string ou objet Path).

    Returns:
        True si le chemin existe ET qu'il s'agit d'un fichier.
    """
    path_obj = Path(path)
    return path_obj.is_file()


def delete_file(file_path: str | Path, printing: bool = False):
    """Delete file"""
    if os.path.exists(file_path):
        os.remove(file_path)
        if printing:
            print(f"Delete {file_path}")
    else:
        if printing:
            print(f"File {file_path} not exists")


def make_directory(directory_path: str | Path) -> Path:
    """Make directory"""
    if not isinstance(directory_path, Path):
        directory_path = Path(directory_path)

    directory_path.mkdir(parents=True, exist_ok=True)

    return directory_path
