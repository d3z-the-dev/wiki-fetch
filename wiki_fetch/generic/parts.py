from collections.abc import Mapping
from enum import StrEnum, auto
from typing import Final


class Part(StrEnum):
    infobox = auto()
    paragraph = auto()
    table = auto()
    list = auto()
    thumb = auto()
    toc = auto()
    all = auto()


class Format(StrEnum):
    text = auto()
    json = auto()
    dict = auto()
    toml = auto()


class Selection(StrEnum):
    first = auto()
    last = auto()
    all = auto()


LABELS: Final[Mapping[Part, str]] = {part: part.value.capitalize() for part in Part}
