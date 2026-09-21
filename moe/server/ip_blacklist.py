from pathlib import Path

import datetime



BLACKLIST_PATH: Path|None = Path()
BLACKLISTED_IPS: list[str] = []



def ip_blacklist_load(p_path: str) -> None:
    global BLACKLIST_PATH
    global BLACKLISTED_IPS


    BLACKLIST_PATH = Path(p_path)
    assert BLACKLIST_PATH.exists()


    print("Loading IP blacklist...")

    with open(BLACKLIST_PATH) as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            BLACKLISTED_IPS.append(line)

    print(f"{len(BLACKLISTED_IPS)} IPs blacklisted!")


def ip_blacklist_add(p_ip: str, p_offence: str="None specified") -> None:
    global BLACKLIST_PATH
    global BLACKLISTED_IPS


    assert BLACKLIST_PATH
    assert BLACKLIST_PATH.exists()


    if p_ip in BLACKLISTED_IPS:
        return


    BLACKLISTED_IPS.append(p_ip)


    # NOTE(vanya): Append the IP to the blacklist
    with open("./ip_blacklist.txt", "a") as f:
        f.write(
            f"\n"
            f"{p_ip}\n"
            f"# On: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n"
            f"# Offence: {p_offence}\n"
            f"# (Automatic entry)"
        )


def ip_blacklist_contains(p_ip: str) -> bool:
    return p_ip in BLACKLISTED_IPS
