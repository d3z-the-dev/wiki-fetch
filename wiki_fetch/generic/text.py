import re
from collections.abc import Mapping
from enum import StrEnum, auto
from typing import Final


class Capture(StrEnum):
    charset = auto()


class Encoding(StrEnum):
    fallback = 'utf-8'
    ascii = 'ascii'
    idna = 'idna'
    gzip = 'gzip'
    deflate = 'deflate'
    form = 'NFKC'


CHARSET: Final = re.compile(rb'charset=["\']?(?P<charset>[\w-]+)', re.IGNORECASE)
FOOTNOTE: Final = re.compile(r'\[\d+\]|\[\.\.\.\]|\[edit\]')
SPACES: Final = re.compile(r'\s+')
FOLD: Final[Mapping[int, str]] = {
    ord('\N{ZERO WIDTH SPACE}'): str(),
    ord('\N{EN DASH}'): '-',
}
LENIENT: Final = 'ignore'
SPACE: Final = ' '
