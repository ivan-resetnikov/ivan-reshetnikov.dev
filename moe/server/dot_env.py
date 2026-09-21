import os



def dot_env_load(p_path: str) -> None:
    with open(p_path) as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip()
