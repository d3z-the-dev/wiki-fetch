from collections.abc import Mapping
from dataclasses import dataclass
from typing import Optional

from wiki_fetch.generic import layout, types


@dataclass(frozen=True, slots=True)
class Entry:
    label: Optional[str]
    value: types.Data
    depth: int


def unfold(value: types.Data, depth: int) -> list[Entry]:
    if isinstance(value, dict):
        return [Entry(label=key, value=child, depth=depth) for key, child in value.items()]
    if isinstance(value, tuple):
        return [Entry(label=None, value=child, depth=depth) for child in value]
    return list()


def build(data: Mapping[str, types.Data]) -> str:
    lines: list[str] = list()
    stack: list[Entry] = [
        Entry(label=key, value=child, depth=0) for key, child in reversed(list(data.items()))
    ]
    while stack:
        entry = stack.pop()
        if isinstance(entry.value, dict | tuple):
            if entry.label is not None:
                lines.append(f'{layout.STEP * entry.depth}{entry.label}{layout.MARK}')
            stack.extend(reversed(unfold(entry.value, entry.depth + 1)))
            continue
        head = str() if entry.label is None else f'{entry.label}{layout.MARK}'
        shown = layout.MISSING if entry.value is None else entry.value
        lines.append(f'{layout.STEP * entry.depth}{head}{shown}')
    return layout.NEWLINE.join(lines)
