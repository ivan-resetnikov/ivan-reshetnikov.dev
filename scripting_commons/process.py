import subprocess

from typing import TypeAlias

from .log import *
from .filesystem import *



ShellCommand: TypeAlias = list[PathLike | bool | int | float]



def resolve_shell_command(p_command: ShellCommand) -> list[str]:
    """
    NOTE(vanya):
    Resolves every element of the path of arbitrary type into a string.

    Or another way to describe it:

    Ensures a list of elements of variable-types like str, pathlib.Path, bool, int are strings.
    While some types are resolved with particular methods. e.g:
    - pathlib.Path will be resolved into a string with `.resolve()`

    NOTE(vanya):
    The benefit of representing commands with these lists is not having to handle string-ification manually.
    """
    return [
        str(token.resolve()) if isinstance(token, Path) else
        str(token)
        for token in p_command
    ]


def shell_simple(p_command: ShellCommand, p_cwd: Path | None = None) -> tuple[int, str]:
    """

    """

    ensured_string_tokens: list[str] = resolve_shell_command(p_command)

    log("")

    # NOTE(vanya): Print the working directory hint
    if p_cwd:
        log(ansi(f"[italic]@ {str(p_cwd.resolve()) if isinstance(p_cwd, Path) else str(p_cwd)}"))

    # NOTE(vanya): Run command

    log(ansi(f"[italic]$ {" ".join(ensured_string_tokens)}"))
    log_push_indent()

    process = subprocess.Popen(
        ensured_string_tokens,
        cwd=p_cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    assert process.stdout is not None
    assert process.stderr is not None

    stdout: str = ""

    for line in process.stdout:
        stripped_line: str = line.rstrip()
        stdout += stripped_line
        log(f"| {stripped_line}")

    for line in process.stderr:
        stripped_line: str = line.rstrip()
        log(f"| {stripped_line}")

    return_code: int = process.wait()

    log("")
    log_pop_indent()

    return return_code, stdout


def assert_shell_simple(p_intent_message: str, p_command: ShellCommand, p_error_message: str="", **p_var_args) -> str:
    log(p_intent_message)

    exit_code, stdout = shell_simple(p_command, **p_var_args)
    assert exit_code == 0, p_error_message

    return stdout


def process_spawn(p_command: ShellCommand) -> subprocess.Popen:
    print("Spawning process")

    ensured_string_tokens: list[str] = resolve_shell_command(p_command)

    log(ansi(f"[italic]$ {" ".join(ensured_string_tokens)}"))

    process = subprocess.Popen(ensured_string_tokens)

    print(process.pid)

    return process


def process_is_up(p_process: subprocess.Popen) -> bool:
    return p_process.poll() is None
