import re
import inspect

from pathlib import Path



ANSI_RESET: str = "\033[0m"
ANSI_TAG_REGEX: re.Pattern = re.compile(r"\[(.*?)\]")



log_indent: int = 0



def ansi_parse_tag(p_tag: str) -> str:
    FG: dict[str, int] = {
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "magenta": 35,
        "cyan": 36,
        "white": 37,
        "default": 39,
    }

    BG: dict[str, int] = {k: v + 10 for k, v in FG.items()}

    STYLES: dict[str, int] = {
        "bold": 1,
        "dim": 2,
        "italic": 3,
        "underline": 4,
        "blink": 5,
        "reverse": 7,
        "hidden": 8,
        "strikethrough": 9,
    }
    
    tokens: list[str] = p_tag.lower().split()
    ansi_codes: list[int] = []

    i: int = 0
    while i < len(tokens):
        bright = False

        if tokens[i] in ("bright", "light"):
            bright = True
            i += 1

        if i >= len(tokens):
            break

        token: str = tokens[i]

        if token in STYLES:
            ansi_codes.append(STYLES[token])
            i += 1
            continue

        if token in FG:
            if i + 1 < len(tokens) and tokens[i + 1] == "bg":
                ansi_codes.append(BG[token] + (60 if bright and token != "default" else 0))
                i += 2
            else:
                ansi_codes.append(FG[token] + (60 if bright and token != "default" else 0))
                if i + 1 < len(tokens) and tokens[i + 1] == "fg":
                    i += 2
                else:
                    i += 1
            continue

        i += 1

    return f"\033[{';'.join(map(str, ansi_codes))}m" if ansi_codes else ""


def ansi(p_text: str) -> str:
    text: str = ANSI_TAG_REGEX.sub(lambda m: ansi_parse_tag(m.group(1)), p_text)
    return text + "\033[0m"


def log(*p_args, **p_var_args) -> None:
    global log_indent
    
    print(Path(inspect.stack()[1].filename).name.rjust(20, " "), "|", "    " * log_indent, end="")
    print(*p_args, **p_var_args)


def log_no_indent(*p_args, **p_var_args) -> None:
    print(*p_args, **p_var_args)


def log_push_indent() -> None:
    global log_indent
    log_indent += 1


def log_pop_indent() -> None:
    global log_indent
    log_indent -= 1
