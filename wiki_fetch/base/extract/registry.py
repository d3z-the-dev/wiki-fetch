from typing import Final, Protocol

from wiki_fetch.base.extract.parts import Contents, Infobox, List, Paragraph, Table, Thumb
from wiki_fetch.base.html.tree import Element
from wiki_fetch.core.models import Block, Piece
from wiki_fetch.generic import parts


class Extractor(Protocol):
    @property
    def part(self) -> parts.Part: ...

    def read(self, root: Element) -> tuple[Block, ...]: ...


EXTRACTORS: Final[tuple[Extractor, ...]] = (Infobox, Paragraph, Table, List, Thumb, Contents)


def extract(part: parts.Part, root: Element) -> tuple[Piece, ...]:
    chosen = (
        EXTRACTORS
        if part is parts.Part.all
        else tuple(one for one in EXTRACTORS if one.part is part)
    )
    return tuple(Piece(part=one.part, blocks=one.read(root)) for one in chosen)
