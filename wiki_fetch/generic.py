import re
from json import dumps
from urllib import request
from urllib.parse import quote, unquote
from unicodedata import normalize
from typing import Tuple, Dict, NamedTuple, TypedDict, TypeAlias, MutableMapping

from bs4 import BeautifulSoup, element


class TUPLE(Tuple[str]): pass
class DICT(Dict, MutableMapping[str, str | TUPLE]): pass

DATA: TypeAlias = str | TUPLE | DICT | dict[str, DICT]

HTML: TypeAlias = BeautifulSoup
ELEMENT: TypeAlias = element.Tag
ELEMENTS: TypeAlias = element.ResultSet | tuple[ELEMENT]

class PAGE(NamedTuple):
    url: str
    html: HTML
    content: ELEMENT = None

class TAG(NamedTuple):
    name: str | list[str] = None
    attrs: dict | None = None
    recursive: bool = True

class SCOPE(NamedTuple):
    row: int = 1
    col: int = 1
    scope: str = None

class CELL(NamedTuple):
    data: DATA | None
    scope: SCOPE = SCOPE()
    index: int = 1

class CELLS(Tuple[CELL]): pass

class ROW(NamedTuple):
    index: int = 1
    label: str | None = None
    cells: CELLS = CELLS()
    length = lambda self: len(self.cells)
    scope = lambda self: None if not self.cells else SCOPE(
        row=max(cell.scope.row for cell in self.cells),
        col=sum(cell.scope.col for cell in self.cells))
    data = lambda self: ARRAY({self.label: tuple([cell.data for cell in self.cells]
        ) if len(self.cells) != 1 else self.cells[0].data})

class ROWS(Tuple[ROW]): pass

class TABLE(NamedTuple):
    label: str | None = None
    rows: ROWS = ROWS()
    length = lambda self: len(self.rows)
    scope = lambda self: None if not self.rows else SCOPE(
        row=sum(row.scope().row for row in self.rows),
        col=max(row.scope().col for row in self.rows))
    data = lambda self: ARRAY({self.label:
        {label: data for row in self.rows for label, data in row.data().items()}})
    
class TABLES(Tuple[TABLE]): pass

class ARRAY(Dict, MutableMapping[str, DATA]): pass
class ARRAYS(Tuple[ARRAY]): pass

class OUTPUT(NamedTuple):
    dict: dict = None
    json: str = None
    text: str = None

FIELD: TypeAlias = CELL | ROW
FIELDS: TypeAlias = CELLS | ROWS
CONTEINER: TypeAlias = ROW | TABLE

def update(conteiner: CONTEINER, fields: FIELDS | FIELD) -> CONTEINER:
    if isinstance(fields, FIELD.__args__): fields = (fields,)
    for field in conteiner._fields:
        if fields and field.startswith(type(fields[0]).__name__.lower()): break
    return conteiner._replace(**{field: (*getattr(conteiner, field), *fields,)})

def merge(master: TABLE, slave: TABLE) -> TABLE:
    return master._replace(**{'rows': (*getattr(master, 'rows'), *getattr(slave, 'rows'),)})

def rename(conteiner: CONTEINER, label: str) -> CONTEINER:
    return conteiner._replace(**{'label': label})

def delete(conteiner: CONTEINER, field: str, index: int) -> CONTEINER:
    return conteiner._replace(**{field: ((fields := getattr(conteiner, field)),
        (fields[:index] + fields[index + 1:]))[1]})

def resize(cell: CELL, row: int = None, col: int = None) -> CELL:
    return cell._replace(**{'scope': SCOPE(
        row=row if row else cell.scope.row, col=col if col else cell.scope.col)})
