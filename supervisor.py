import time
import subprocess

from moe.scripting_commons import *



UPDATE_INTERVAL: int = 5



git: str = ""
server = Path()
python3 = Path()

out_of_date_file = Path(".out_of_date")
server_process: subprocess.Popen|None = None



def set_up_environment() -> None:
    global git, server, python3


    log("Setting up environment")
    log_push_indent()


    git = assert_bin("git")
    server = assert_file("server.py")

    python3 = venv_ensure(".venv")
    venv_ensure_requirements(python3, "requirements.txt")


    log_pop_indent()


def is_server_up() -> bool:
    global server_process

    return isinstance(server_process, subprocess.Popen) and process_is_up(server_process)


def is_up_to_date() -> bool:
    global out_of_date_file

    return not out_of_date_file.exists()


def mark_up_to_date() -> None:
    global out_of_date_file

    log("Marking source as up-to-date")

    if out_of_date_file.exists():
        out_of_date_file.unlink()


def ensure_server_killed() -> None:
    global server_process

    log("Killing server process")
    if isinstance(server_process, subprocess.Popen) and process_is_up(server_process):
        server_process.kill()
        server_process = None



def supervise_until_KeyboardInterrupt() -> None:
    global server_process
    
    set_up_environment()


    log("Supervising until KeyboardInterrupt")
    log_push_indent()

    try:
        while True:
            # NOTE(vanya): Ensure that the project is up-to-date
            if not is_up_to_date():
                log("Server source out-of-date! Killing, (Re-)pulling, and restarting...")
                ensure_server_killed()
                shell_simple([
                    git, "pull"
                ])
                mark_up_to_date()
            
            # NOTE(vanya): Ensure that the server process is up
            if not is_server_up():
                log("Server process down! (Re-)starting...")
                server_process = process_spawn(
                    [
                        python3, server
                    ]
                )

            time.sleep(UPDATE_INTERVAL)
    
    except KeyboardInterrupt:
        log("Received KeyboardInterrupt, exiting supervisor.")
        ensure_server_killed()

    finally:
        log_pop_indent()


if __name__ == "__main__":
    log_set_prefix("[supervisor.py]")
    supervise_until_KeyboardInterrupt()