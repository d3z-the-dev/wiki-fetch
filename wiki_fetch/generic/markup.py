import re
from collections.abc import Container
from enum import StrEnum
from typing import Any, Final

from wiki_fetch.generic.network import Scheme
from wiki_fetch.generic.syntax import Tag
from wiki_fetch.utils.settings import Group, settings


class Label(StrEnum):
    nameless = 'No header'
    prologue = 'Prologue'
    contents = 'Contents'
    picture = 'Image'
    caption = 'Caption'
    missing = 'No caption'
    headers = 'Headers {order}'
    carried = '{value} [{order}]'
    numbered = '{value} {order}'
    line = 'Row {order}'


CONFIG: Any = settings.load(Group.markup)
SELECTORS: Any = CONFIG.selectors
CLASSES: Any = CONFIG.classes
LAYERS: Final[tuple[str, ...]] = (SELECTORS.content, SELECTORS.body, SELECTORS.parser)

CHROME_TAGS: Final[frozenset[str]] = frozenset(CONFIG.chrome.tags)
CHROME_CLASSES: Final[frozenset[str]] = frozenset(CONFIG.chrome.classes)
CHROME_IDENTIFIERS: Final[frozenset[str]] = frozenset(CONFIG.chrome.identifiers)

PAIR: Final = (Tag.HEAD, Tag.DATA)
HEADINGS: Final = (Tag.SECTION, Tag.SUBSECTION, Tag.TOPIC)
PROSE: Final[frozenset[str]] = frozenset({*HEADINGS, Tag.PARAGRAPH})
BARRIER: Final[frozenset[str]] = frozenset({Tag.TABLE, Tag.FIGURE, Tag.ASIDE})
HIDDEN: Final = re.compile(r'display\s*:\s*none', re.IGNORECASE)
COLON: Final = re.compile(r'\s*:\s*$')
PROTOCOL: Final = '//'
SEPARATOR: Final = '.'
SLASH: Final = '/'
NAMESPACE: Final = ':'
UNDERSCORE: Final = '_'
QUESTION: Final = '?'
AMPERSAND: Final = '&'
TRACKING: Final = 'utm_'
SCHEME: Final = f'{Scheme.secure}{NAMESPACE}'
SPAN: Final = 1


def unique(taken: Container[str], label: str) -> str:
    if label not in taken:
        return label
    order = 2
    while Label.numbered.format(value=label, order=order) in taken:
        order += 1
    return Label.numbered.format(value=label, order=order)
