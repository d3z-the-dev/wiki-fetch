from collections.abc import Iterator
from dataclasses import dataclass
from typing import Final, Optional
from urllib.parse import unquote

from wiki_fetch.base.extract.clean import (
    address,
    content,
    heading,
    label,
    marked,
    sentence,
    stream,
)
from wiki_fetch.base.html.query import find, find_all, select, select_one
from wiki_fetch.base.html.tree import Element, ancestors, classes
from wiki_fetch.core.models import Block, Cell, Row
from wiki_fetch.generic import markup, parts, syntax, text, types


class Infobox:
    part: Final = parts.Part.infobox

    @staticmethod
    def place(section: dict[str, types.Data], key: str, value: types.Data) -> None:
        section[markup.unique(section, key)] = value

    @staticmethod
    def picture(cell: Element) -> dict[str, types.Data]:
        image = find(cell, syntax.Tag.IMAGE)
        if image is None:
            return dict()
        caption = find(cell, classes=markup.CLASSES.caption) or find(
            cell, markup.SELECTORS.figcaption
        )
        found: dict[str, types.Data] = {
            str(markup.Label.picture): address(image.attrs.get(syntax.Attribute.SRC, str()))
        }
        legend = sentence(caption) or sentence(cell)
        if legend:
            found[str(markup.Label.caption)] = legend
        return found

    @staticmethod
    def heading(box: Element) -> str:
        above = find(box, classes=markup.CLASSES.above)
        if above is not None:
            return label(above)
        caption = find(box, syntax.Tag.CAPTION)
        if caption is not None:
            return label(caption)
        first = find(box, syntax.Tag.ROW)
        return label(find(first, syntax.Tag.HEAD)) if first is not None else str()

    @classmethod
    def sections(cls, box: Element, barrier: set[Element], title: str) -> Iterator[Row]:
        header = title
        section: dict[str, types.Data] = dict()
        for line in find_all(box, syntax.Tag.ROW):
            if not barrier.isdisjoint(ancestors(line)):
                continue
            cells = find_all(line, markup.PAIR, recursive=False)
            heads = tuple(cell for cell in cells if cell.tag == syntax.Tag.HEAD)
            bodies = tuple(cell for cell in cells if cell.tag == syntax.Tag.DATA)
            if heads and not bodies:
                opener = label(heads[0])
                if marked(heads[0], markup.CLASSES.label) or not opener:
                    continue
                if section:
                    yield Row(label=header, cells=(Cell(data=dict(section)),))
                    section = dict()
                header = opener
            elif len(bodies) > 1 and not heads:
                cls.place(section, label(bodies[0]), content(bodies[1]))
            elif bodies and not heads:
                shot = cls.picture(bodies[0])
                for key, value in shot.items():
                    cls.place(section, key, value)
                if not shot:
                    spare = content(bodies[0])
                    if spare is not None:
                        cls.place(section, str(len(section) + 1), spare)
            elif heads and bodies:
                cls.place(section, label(heads[0]), content(bodies[0]))
        if section:
            yield Row(label=header, cells=(Cell(data=dict(section)),))

    @classmethod
    def fold(cls, table: Block) -> dict[str, types.Data]:
        merged: dict[str, types.Data] = dict()
        for row in table.rows:
            for cell in row.cells:
                if isinstance(cell.data, dict):
                    for key, value in cell.data.items():
                        cls.place(merged, key, value)
        return merged

    @classmethod
    def compose(cls, box: Element) -> Block:
        inner = select(box, markup.SELECTORS.infobox)
        title = cls.heading(box)
        rows = list(cls.sections(box, set(inner), title))
        for part in cls.outermost(inner):
            child = cls.compose(part)
            name = markup.unique({row.label for row in rows}, child.label)
            rows.append(Row(label=name, cells=(Cell(data=cls.fold(child)),)))
        return Block(label=title, rows=tuple(rows))

    @staticmethod
    def outermost(boxes: tuple[Element, ...]) -> list[Element]:
        known = set(boxes)
        return [box for box in boxes if known.isdisjoint(ancestors(box))]

    @classmethod
    def read(cls, root: Element) -> tuple[Block, ...]:
        return tuple(
            cls.compose(box) for box in cls.outermost(select(root, markup.SELECTORS.infobox))
        )


class Paragraph:
    part: Final = parts.Part.paragraph

    @staticmethod
    def read(root: Element) -> tuple[Block, ...]:
        tables: list[Block] = list()
        rows: list[Row] = list()
        lines: list[str] = list()
        title: str = markup.Label.prologue
        heading: str = markup.Label.prologue
        for node in stream(root, markup.PROSE):
            if node.tag == syntax.Tag.PARAGRAPH:
                line = sentence(node)
                if line:
                    lines.append(line)
                continue
            if lines:
                rows.append(Row(label=heading, cells=(Cell(data=tuple(lines)),)))
                lines = list()
            if node.tag == syntax.Tag.SECTION:
                if rows:
                    tables.append(Block(label=title, rows=tuple(rows)))
                    rows = list()
                title = sentence(node)
            heading = sentence(node)
        if lines:
            rows.append(Row(label=heading, cells=(Cell(data=tuple(lines)),)))
        if rows:
            tables.append(Block(label=title, rows=tuple(rows)))
        return tuple(tables)


@dataclass(slots=True)
class Carry:
    data: types.Data
    left: int
    seen: int = 1


class Table:
    part: Final = parts.Part.table

    @staticmethod
    def span(cell: Element, name: str) -> int:
        value = cell.attrs.get(name, str())
        return int(value) if value.isdigit() and int(value) >= markup.SPAN else markup.SPAN

    @staticmethod
    def repeat(held: Carry) -> types.Data:
        if not isinstance(held.data, str):
            return held.data
        return markup.Label.carried.format(value=held.data, order=held.seen)

    @classmethod
    def sweep(cls, line: Element, carry: dict[int, Carry]) -> tuple[Cell, ...]:
        cells: list[Cell] = list()
        column = 0
        source = iter(find_all(line, markup.PAIR, recursive=False))
        while True:
            held = carry.get(column)
            if held is not None:
                held.seen += 1
                held.left -= 1
                cells.append(Cell(data=cls.repeat(held)))
                if held.left == 0:
                    del carry[column]
                column += 1
                continue
            cell = next(source, None)
            if cell is None:
                return tuple(cells)
            data = content(cell)
            width = cls.span(cell, syntax.Attribute.COLSPAN)
            height = cls.span(cell, syntax.Attribute.ROWSPAN)
            if height > markup.SPAN:
                carry[column] = Carry(data=data, left=height - markup.SPAN)
            cells.append(Cell(data=data))
            cells.extend(Cell(data=None) for _ in range(markup.SPAN, width))
            column += width

    @staticmethod
    def headed(line: Element) -> bool:
        cells = find_all(line, markup.PAIR, recursive=False)
        return bool(cells) and all(cell.tag == syntax.Tag.HEAD for cell in cells)

    @classmethod
    def rows(cls, grid: Element) -> tuple[Row, ...]:
        carry: dict[int, Carry] = dict()
        built: list[Row] = list()
        headers = 0
        for line in find_all(grid, syntax.Tag.ROW):
            cells = cls.sweep(line, carry)
            if not cells:
                continue
            if cls.headed(line) and not carry:
                headers += 1
                built.append(Row(label=markup.Label.headers.format(order=headers), cells=cells))
                continue
            label = cells[0].data
            if isinstance(label, str):
                built.append(Row(label=label, cells=cells[1:]))
                continue
            built.append(Row(label=markup.Label.line.format(order=len(built) + 1), cells=cells))
        return tuple(built)

    @classmethod
    def read(cls, root: Element) -> tuple[Block, ...]:
        return tuple(
            Block(label=heading(grid), rows=cls.rows(grid))
            for grid in select(root, markup.SELECTORS.wikitable)
        )


class List:
    part: Final = parts.Part.list

    @staticmethod
    def entries(block: Element) -> tuple[Row, ...]:
        found = (sentence(bullet) for bullet in find_all(block, syntax.Tag.ITEM, recursive=False))
        return tuple(
            Row(label=str(order), cells=(Cell(data=value),))
            for order, value in enumerate((line for line in found if line), start=1)
        )

    @staticmethod
    def chromed(block: Element) -> bool:
        return any(
            parent.tag in markup.CHROME_TAGS
            or not markup.CHROME_CLASSES.isdisjoint(classes(parent))
            or parent.attrs.get(syntax.Attribute.ID) in markup.CHROME_IDENTIFIERS
            for parent in ancestors(block)
        )

    @classmethod
    def read(cls, root: Element) -> tuple[Block, ...]:
        tables: list[Block] = list()
        for block in find_all(root, syntax.Tag.LIST):
            if cls.chromed(block):
                continue
            rows = cls.entries(block)
            if rows:
                tables.append(Block(label=heading(block), rows=rows))
        return tuple(tables)


class Thumb:
    part: Final = parts.Part.thumb

    @staticmethod
    def name(anchor: Optional[Element]) -> str:
        if anchor is None:
            return markup.Label.nameless
        tail = unquote(anchor.attrs.get(syntax.Attribute.HREF, str())).rsplit(markup.SLASH, 1)[-1]
        stem = tail.partition(markup.NAMESPACE)[2] or tail
        replaced = stem.rsplit(markup.SEPARATOR, 1)[0].replace(markup.UNDERSCORE, text.SPACE)
        return replaced or markup.Label.nameless

    @classmethod
    def frame(cls, figure: Element) -> Optional[Block]:
        image = find(figure, syntax.Tag.IMAGE)
        if image is None:
            return None
        caption = sentence(find(figure, markup.SELECTORS.figcaption)) or markup.Label.missing
        link = address(image.attrs.get(syntax.Attribute.SRC, str()))
        return Block(
            label=cls.name(select_one(figure, markup.SELECTORS.file)),
            rows=(Row(label=caption, cells=(Cell(data=link),)),),
        )

    @classmethod
    def read(cls, root: Element) -> tuple[Block, ...]:
        found = (cls.frame(figure) for figure in select(root, markup.SELECTORS.figure))
        return tuple(table for table in found if table is not None)


class Contents:
    part: Final = parts.Part.toc

    @staticmethod
    def entries(root: Element) -> Iterator[tuple[str, str]]:
        counters: list[int] = list()
        for block in select(root, markup.SELECTORS.heading):
            head = find(block, markup.HEADINGS)
            if head is None:
                continue
            depth = markup.HEADINGS.index(head.tag) + 1
            del counters[depth:]
            counters.extend(0 for _ in range(depth - len(counters)))
            counters[-1] += 1
            yield markup.SEPARATOR.join(str(count) for count in counters), sentence(head)

    @classmethod
    def read(cls, root: Element) -> tuple[Block, ...]:
        rows = tuple(
            Row(label=number, cells=(Cell(data=title),)) for number, title in cls.entries(root)
        )
        return (Block(label=markup.Label.contents, rows=rows),) if rows else tuple()
