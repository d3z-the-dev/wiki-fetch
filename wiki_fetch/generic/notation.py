import re
from collections.abc import Mapping
from typing import Final

BARE: Final = re.compile(r'^[A-Za-z0-9_-]+$')
QUOTED: Final = '"{value}"'
FIELD: Final = '{key} = {value}'
ARRAY: Final = '[{items}]'
INLINE: Final = '{{{fields}}}'
HEADER: Final = '[{path}]'
REPEATED: Final = '[[{path}]]'
SEPARATOR: Final = ', '
PATH: Final = '.'
ESCAPES: Final[Mapping[int, str]] = {
    ord('\\'): '\\\\',
    ord('"'): '\\"',
    ord('\b'): '\\b',
    ord('\t'): '\\t',
    ord('\n'): '\\n',
    ord('\f'): '\\f',
    ord('\r'): '\\r',
    **{code: f'\\u{code:04X}' for code in range(0x20) if chr(code) not in '\b\t\n\f\r'},
    0x7F: '\\u007F',
}
