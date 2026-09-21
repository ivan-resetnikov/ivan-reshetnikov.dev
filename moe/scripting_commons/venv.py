import os
import venv

from pathlib import Path

from .log import *
from .filesystem import PathLike, ensure_path_as_pathlib_Path
from .process import assert_not_exists, assert_file, assert_shell_simple



__all__ = ["venv_ensure", "venv_ensure_requirements"]



def venv_ensure(p_path: PathLike) -> Path:
    p_path = ensure_path_as_pathlib_Path(p_path)


    log(ansi(f"[dim white]Ensuring a virtual environment exists @ {p_path}"))

    if not p_path.exists():
        venv.create(p_path, with_pip=True)


    if os.name == "nt":
        python: Path = assert_file(p_path / "Scripts" / "python.exe", False)
    else:
        python: Path = assert_file(p_path / "bin" / "python", False)

    return python


def venv_ensure_requirements(p_python: PathLike, p_requirements_file_path: PathLike) -> None:
    assert_file(p_python, False)
    assert_file(p_requirements_file_path, False)

    assert_shell_simple(
        ansi(f"[dim white]Pulling requirements with pip @ {p_requirements_file_path}"),
        [
            p_python, "-m", "pip", "install", "-r", p_requirements_file_path
        ],
        ""
    )
