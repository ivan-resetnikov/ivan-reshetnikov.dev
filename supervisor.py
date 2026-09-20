import time

from scripting_commons import *

import subprocess



UPDATE_INTERVAL: int = 1



def supervise_until_KeyboardInterrupt() -> None:
    python3: str = assert_bin("python3")
    git: str = assert_bin("git")
    server: Path = assert_file("./server.py")
    out_of_date_file = Path("./.out_of_date")

    server_process: subprocess.Popen|None = None


    # NOTE(vanya): Helper functions
    def is_server_up() -> bool:
        return isinstance(server_process, subprocess.Popen) and process_is_up(server_process)

    def is_up_to_date() -> bool:
        return not out_of_date_file.exists()

    def mark_up_to_date() -> None:
        log("Marking source as up-to-date")

        if out_of_date_file.exists():
            out_of_date_file.unlink()

    def ensure_server_killed() -> None:
        log("Killing server process")
        if isinstance(server_process, subprocess.Popen) and process_is_up(server_process):
            server_process.kill()


    log("Supervising until KeyboardInterrupt...")

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
                server_process = process_spawn([
                    python3, server
                ])

            time.sleep(UPDATE_INTERVAL)
    except KeyboardInterrupt:
        log("Received KeyboardInterrupt, exiting supervisor.")

        ensure_server_killed()
        
        return


if __name__ == "__main__":
    supervise_until_KeyboardInterrupt()