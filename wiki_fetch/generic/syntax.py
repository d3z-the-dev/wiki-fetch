import re
from collections.abc import Mapping
from enum import StrEnum, auto
from typing import Final


class Tag(StrEnum):
    ROOT = 'html'
    ROW = 'tr'
    HEAD = 'th'
    DATA = 'td'
    ITEM = 'li'
    LIST = 'ul'
    BREAK = 'br'
    IMAGE = 'img'
    CAPTION = 'caption'
    ANCHOR = 'a'
    PARAGRAPH = 'p'
    SECTION = 'h2'
    SUBSECTION = 'h3'
    TOPIC = 'h4'
    TABLE = 'table'
    FIGURE = 'figure'
    ASIDE = 'aside'
    SCRIPT = 'script'
    STYLE = 'style'
    OPTION = 'option'
    TERM = 'dt'
    DETAIL = 'dd'
    HEADER = 'thead'
    BODY = 'tbody'
    FOOTER = 'tfoot'
    AREA = 'area'
    BASE = 'base'
    COLUMN = 'col'
    EMBED = 'embed'
    RULE = 'hr'
    INPUT = 'input'
    LINK = 'link'
    META = 'meta'
    PARAMETER = 'param'
    SOURCE = 'source'
    TRACK = 'track'
    OPPORTUNITY = 'wbr'


class Attribute(StrEnum):
    ID = 'id'
    CLASS = 'class'
    HREF = 'href'
    SRC = 'src'
    STYLE = 'style'
    COLSPAN = 'colspan'
    ROWSPAN = 'rowspan'


class Capture(StrEnum):
    combinator = auto()
    tag = auto()
    identifier = auto()
    label = auto()
    attribute = auto()
    operator = auto()
    content = auto()


VOID: Final[frozenset[str]] = frozenset(
    {
        Tag.AREA,
        Tag.BASE,
        Tag.BREAK,
        Tag.COLUMN,
        Tag.EMBED,
        Tag.RULE,
        Tag.IMAGE,
        Tag.INPUT,
        Tag.LINK,
        Tag.META,
        Tag.PARAMETER,
        Tag.SOURCE,
        Tag.TRACK,
        Tag.OPPORTUNITY,
    }
)
CELLS: Final[frozenset[str]] = frozenset({Tag.DATA, Tag.HEAD})
GROUPS: Final[frozenset[str]] = frozenset({Tag.HEADER, Tag.BODY, Tag.FOOTER})
DESCRIPTIONS: Final[frozenset[str]] = frozenset({Tag.TERM, Tag.DETAIL})
IMPLICIT: Final[Mapping[str, frozenset[str]]] = {
    Tag.ITEM: frozenset({Tag.ITEM}),
    Tag.PARAGRAPH: frozenset({Tag.PARAGRAPH}),
    Tag.DATA: CELLS,
    Tag.HEAD: CELLS,
    Tag.ROW: CELLS | {Tag.ROW},
    Tag.OPTION: frozenset({Tag.OPTION}),
    Tag.TERM: DESCRIPTIONS,
    Tag.DETAIL: DESCRIPTIONS,
    Tag.HEADER: GROUPS,
    Tag.BODY: GROUPS,
    Tag.FOOTER: GROUPS,
}
SILENT: Final[frozenset[str]] = frozenset({Tag.SCRIPT, Tag.STYLE})
TOKEN: Final = re.compile(
    r"""
      (?P<combinator>\s*>\s*|\s+)
    | (?P<tag>[A-Za-z][\w-]*)
    | \#(?P<identifier>[-\w]+)
    | \.(?P<label>[-\w]+)
    | \[\s*(?P<attribute>[-\w:]+)\s*
        (?:(?P<operator>\^?=)\s*(?P<content>"[^"]*"|'[^']*'|[^\]\s]*)\s*)?
      \]
    """,
    re.VERBOSE,
)
CACHE: Final = 256
GROUP: Final = ','
CHILD: Final = '>'
QUOTES: Final = '"\''
PREFIXED: Final = '^='
