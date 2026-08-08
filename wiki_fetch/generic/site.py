from typing import Any, Final

from wiki_fetch.utils.settings import Group, settings

CONFIG: Any = settings.load(Group.site)
HOST: Final[str] = CONFIG.address.host
SEARCH: Final[str] = CONFIG.address.search
ADDRESS: Final[str] = CONFIG.address.key
DEFAULT: Final[str] = CONFIG.defaults.language
SAFE: Final = str()
