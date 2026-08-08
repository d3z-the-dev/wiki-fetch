from enum import Enum, IntEnum, StrEnum
from typing import Final, NamedTuple


class Code(IntEnum):
    done = 0
    failure = 1
    misuse = 2


class Pair(NamedTuple):
    short: str
    long: str


class Flag(Enum):
    _value_: Pair

    url = Pair('-u', '--url')
    query = Pair('-q', '--query')
    lang = Pair('-l', '--lang')
    part = Pair('-p', '--part')
    item = Pair('-i', '--item')
    output = Pair('-o', '--output')

    @property
    def short(self) -> str:
        return self.value.short

    @property
    def long(self) -> str:
        return self.value.long


class Help(StrEnum):
    url = 'URL of the article to read'
    query = 'what to look up when no URL is given'
    lang = 'language edition to read'
    part = 'part of the article to take'
    item = 'which matching blocks to keep'
    output = 'output format'


PROGRAM: Final = 'wiki-fetch'
SUMMARY: Final = 'Read Wikipedia articles from the command line.'
