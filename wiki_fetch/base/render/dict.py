from wiki_fetch.core.models import Block, Row
from wiki_fetch.generic import markup, parts, types


def line(row: Row) -> types.Data:
    if len(row.cells) == 1:
        return row.cells[0].data
    return tuple(cell.data for cell in row.cells)


def one(table: Block) -> types.Payload:
    rows: types.Payload = dict()
    for row in table.rows:
        rows[markup.unique(rows, str(row.label))] = line(row)
    return {str(table.label): rows}


def build(tables: tuple[Block, ...], selection: parts.Selection) -> types.Data:
    if selection is parts.Selection.all:
        return tuple(one(table) for table in tables)
    if not tables:
        return dict()
    return one(tables[0] if selection is parts.Selection.first else tables[-1])
