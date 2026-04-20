import json
from collections.abc import Mapping
from typing import Final

from wiki_fetch.generic import layout, types


def build(data: Mapping[str, types.Data]) -> str:
    return json.dumps(data, indent=layout.INDENT, ensure_ascii=False, allow_nan=True)


EMPTY: Final[str] = build(dict())
