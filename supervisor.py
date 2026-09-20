import time

from scripting_commons import *

import subprocess



UPDATE_INTERVAL: int = 1



def supervise_until_KeyboardInterrupt() -> None:
    log("Supervising until KeyboardInterrupt...")

    python3: str = assert_bin("python3")
    server: Path = assert_file("./server.py")

    server_process: subprocess.Popen|None = None

    def is_server_up() -> bool:
        return isinstance(server_process, subprocess.Popen) and process_is_up(server_process)

    def is_up_to_date

    try:
        while True:
            
            
            # NOTE(vanya): Server process respawning
            if not is_server_up():
                log("Server process down! (Re)starting...")
                server_process = process_spawn([
                    python3, server
                ])

            time.sleep(UPDATE_INTERVAL)
    except KeyboardInterrupt:
        log("Received KeyboardInterrupt, exiting supervisor.")

        if is_server_up():
            log("Killing server process")
            server_process.kill()
        
        return


if __name__ == "__main__":
    supervise_until_KeyboardInterrupt()