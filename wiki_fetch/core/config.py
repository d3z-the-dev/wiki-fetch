from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote, urljoin

from wiki_fetch.core.languages import resolve
from wiki_fetch.generic import parts, site


@dataclass(frozen=True, slots=True)
class Site:
    language: str = resolve(site.DEFAULT)

    @property
    def base(self) -> str:
        return site.HOST.format(language=self.language)

    def query(self, value: str) -> str:
        return self.base + site.SEARCH.format(query=quote(value, safe=site.SAFE))

    def join(self, href: str) -> str:
        return urljoin(self.base, href)


@dataclass(frozen=True, slots=True)
class Search:
    query: Optional[str] = None
    url: Optional[str] = None
    part: parts.Part = parts.Part.all
    item: parts.Selection = parts.Selection.all
