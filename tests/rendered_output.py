import re

BOX_CHARACTERS = "─│╭╮╰╯"
CELL_SEPARATOR = re.compile(r"\s{2,}")


def cells(text: str) -> list[list[str]]:
    return [CELL_SEPARATOR.split(line) for line in lines(text)]


def flat_text(text: str) -> str:
    return CELL_SEPARATOR.sub(" ", " ".join(lines(text)))


def lines(text: str) -> list[str]:
    stripped_lines = []

    for raw_line in text.splitlines():
        line = raw_line.strip().strip(BOX_CHARACTERS).strip()

        if line:
            stripped_lines.append(line)

    return stripped_lines
