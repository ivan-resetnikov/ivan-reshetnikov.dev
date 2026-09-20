from typing import Any



def str_to_bool(p_str: str) -> bool:
    """
    Converts generic user input when prompted for a truthy value,
    and converts it to a boolean type.
    """

    if p_str.lower() in ("true", "1", "on", "yes"):
        return True

    return False


def pop_front_safe(p_array: list) -> Any|None:
    """
    Remove and return the element at the beginning of the list,
    or `None` if the list is empty.
    """

    try:
        return p_array.pop(0)
    except IndexError:
        return None
