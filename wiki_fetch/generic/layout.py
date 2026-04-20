from typing import Any, Final

from wiki_fetch.generic.text import SPACE
from wiki_fetch.utils.settings import Group, settings

CONFIG: Any = settings.load(Group.layout)
INDENT: Final[int] = CONFIG.indent
MISSING: Final[str] = CONFIG.missing
NEWLINE: Final[str] = CONFIG.newline
MARK: Final[str] = CONFIG.mark
STEP: Final[str] = SPACE * INDENT
