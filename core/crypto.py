import os



def join_paths_safe(p_base_dir: str, p_path: str) -> str | None:
    p_base_dir = os.path.realpath(p_base_dir)
    resolved = os.path.realpath(os.path.join(p_base_dir, p_path.lstrip("/\\")))

    if os.path.commonpath((p_base_dir, resolved)) != p_base_dir:
        return None

    return resolved