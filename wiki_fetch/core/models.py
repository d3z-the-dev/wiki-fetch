from dataclasses import dataclass, field

from wiki_fetch.base.render.json import EMPTY
from wiki_fetch.generic import parts, types


@dataclass(frozen=True, slots=True)
class Cell:
    data: types.Data


@dataclass(frozen=True, slots=True)
class Row:
    label: str = str()
    cells: tuple[Cell, ...] = tuple()


@dataclass(frozen=True, slots=True)
class Block:
    label: str = str()
    rows: tuple[Row, ...] = tuple()


@dataclass(frozen=True, slots=True)
class Piece:
    part: parts.Part
    blocks: tuple[Block, ...] = tuple()

    @property
    def label(self) -> str:
        return parts.LABELS[self.part]


@dataclass(frozen=True, slots=True)
class Output:
    dict: types.Payload = field(default_factory=dict)
    json: str = EMPTY
    text: str = str()
    toml: str = str()
