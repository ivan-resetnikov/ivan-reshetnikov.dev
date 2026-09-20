import shutil

from pathlib import Path
from typing import TypeAlias

from .log import *


PathLike: TypeAlias = str | Path


def ensure_path_as_string(p_path: PathLike) -> str:
    return (
        str(p_path.resolve())
        if isinstance(p_path, Path) else
        str(p_path)
    )


def ensure_path_as_pathlib_Path(p_path: PathLike) -> Path:
    return Path(p_path)


def ensure_dir(p_path: PathLike, p_message: bool=True) -> Path:
    p_path = ensure_path_as_pathlib_Path(p_path)

    if p_message:
        log(ansi(f"[dim white]Ensuring dir exists @ {p_path}"))

    p_path.mkdir(parents=True, exist_ok=True)
    return p_path


def assert_dir(p_path: PathLike) -> Path:
    p_path = ensure_path_as_pathlib_Path(p_path)

    log(ansi(f"[dim white]Asserting dir exists @ {p_path}"))
    assert p_path.exists() and p_path.is_dir(), ansi("[red fg]A directory does not exist at the path above!")
    return p_path


def assert_file(p_path: PathLike) -> Path:
    p_path = ensure_path_as_pathlib_Path(p_path)

    log(ansi(f"[dim white]Asserting file exists @ {p_path}"))
    assert p_path.exists() and p_path.is_file(), ansi("[red fg]A file does not exist at the path above!")
    return p_path


def copy(p_source_path: PathLike, p_dest_path: PathLike) -> Path:
    p_source_path = ensure_path_as_pathlib_Path(p_source_path)
    p_dest_path = ensure_path_as_pathlib_Path(p_dest_path)

    log(f"Ensuring a copy of {p_source_path.name} @ {p_dest_path.parent}")

    p_dest_path.write_bytes(p_source_path.read_bytes())
    return p_dest_path


def assert_bin(p_binary_file_name: str) -> str:
    log(ansi(f"[dim white]Asserting binary dependency \"{p_binary_file_name}\""))
    found_path: str|None = shutil.which(p_binary_file_name)
    assert found_path, ansi(f"[red fg]`{p_binary_file_name}` is a mandatory dependency!")
    return found_path


def size_as_human_readable(p_size: int) -> str:
    units = ["B", "KiB", "MiB", "GiB"]
    
    value = float(p_size)
    for unit in units:
        if value < 1024:
            return f"{value:.2f} {unit}"
        value /= 1024

    return f"{value:.2f} TiB"
