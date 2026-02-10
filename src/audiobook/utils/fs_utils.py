from pathlib import Path
import os
import shutil


def path_join(base_path: str | Path, *add_paths: str | Path) -> Path:
    """Join paths"""
    return Path(base_path).joinpath(*add_paths)


def path_exists(path: str | Path | None) -> bool:
    """Check if path exists"""
    if not path:
        return False

    return Path(path).exists()


def file_exists(path: str | Path) -> bool:
    """Check if path exists and if it is file"""
    return Path(path).is_file()


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

    return f"{current_size:.2f}".rstrip("0").rstrip(".") + f" {units[i]}"


def get_file_size(path: str | Path) -> int:
    """Get file size as bytes from path of file"""
    if Path(path).is_file():
        return os.path.getsize(path)
    else:
        print(f"ERROR: file not found at {path}")

    return 0


def get_file(directory_path: str | Path, extension: str) -> Path | None:
    """Find first file with extension in directory_path"""
    listing = get_files(directory_path, extension)
    if listing and len(listing) > 0:
        return Path(listing[0])

    return None


def get_files(
    directory_path: str | Path, extension: str, recursive: bool = False
) -> list[Path]:
    """Find all files with specific extension into directory"""
    ext = extension if extension.startswith(".") else f".{extension}"
    root = Path(directory_path)

    if not root.is_dir():
        return []

    pattern = f"**/*{ext}" if recursive else f"*{ext}"

    return sorted(list(root.glob(pattern)), key=lambda p: p.name.lower())


def get_all_files(directory_path: str | Path) -> list[Path]:
    """Get all files into directory"""
    return [f for f in Path(directory_path).iterdir() if f.is_file()]


def move_files(paths: list[Path], destination_dir: str | Path) -> bool:
    """
    Moves a list of files to a target directory.

    :param paths: List of absolute or relative file paths.
    :param destination_dir: Path to the directory where files should be moved.
    """
    dest_path = Path(destination_dir)
    dest_path.mkdir(parents=True, exist_ok=True)

    for path in paths:
        source_file = Path(path)

        if not source_file.is_file():
            print(f"⚠️ File not found, ignored: {source_file.name}")
            continue

        destination_file = dest_path / source_file.name

        try:
            shutil.move(str(source_file), str(destination_file))
        except Exception as e:
            print(f"❌ Error while moving {source_file.name}: {e}")
            return False

    return True


def get_absolute_path(path: str | Path) -> Path:
    """Get absolute path of possible relative path"""
    return Path(path).resolve()


def rename_file(
    absolute_path: str | Path, new_name: str, overwrite: bool = False
) -> Path:
    """Renames a file while keeping its original folder and extension"""
    path = Path(absolute_path)
    new_path = path.with_name(new_name + path.suffix)

    if new_path.exists():
        if overwrite:
            new_path.unlink()
        else:
            raise FileExistsError(f"Path {new_path} already exists")

    path.rename(new_path)
    return new_path.resolve()


def copy_file(from_path: str | Path, to_path: str | Path) -> Path:
    """Copy file"""
    copy_path = shutil.copy(from_path, to_path)
    return Path(copy_path)


def copy_directory(from_path: str | Path, to_path: str | Path) -> Path:
    """Copy directory"""
    shutil.copytree(from_path, to_path, dirs_exist_ok=True)
    return Path(to_path)


def rename_directory(absolute_path: str | Path, new_name: str) -> Path:
    """Renames a directory while keeping its original location"""
    path = Path(absolute_path)
    new_path = path.with_name(new_name)

    if new_path.exists():
        shutil.rmtree(new_path)

    path.rename(new_path)

    return new_path.resolve()


def remove_directory(directory_path: str | Path | None) -> bool:
    """Delete directory"""
    if not directory_path:
        return False

    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)
        return True

    return False


def remove_file(file_path: str | Path) -> bool:
    """Delete file"""
    path = Path(file_path)
    if path.exists():
        path.unlink()
        return True

    return False


def make_directory(directory_path: str | Path) -> Path:
    """Make directory"""
    if not isinstance(directory_path, Path):
        directory_path = Path(directory_path)

    directory_path.mkdir(parents=True, exist_ok=True)

    return directory_path
