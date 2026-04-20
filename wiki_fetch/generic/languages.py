import re
from collections.abc import Mapping
from dataclasses import asdict
from typing import Any, Final

from wiki_fetch.utils.settings import Group, settings

CONFIG: Any = settings.load(Group.languages)
CODES: Final[Mapping[str, str]] = asdict(CONFIG.codes)
ALIASES: Final[Mapping[str, list[str]]] = asdict(CONFIG.aliases)
NAMES: Final[Mapping[str, str]] = {
    **{name.casefold(): code for name, code in CODES.items()},
    **{
        spelling.casefold(): CODES[name]
        for name, spellings in ALIASES.items()
        for spelling in spellings
    },
}
PATTERN: Final = re.compile(r'^[a-z]{2,3}(-[a-z0-9]{2,8})?$')
