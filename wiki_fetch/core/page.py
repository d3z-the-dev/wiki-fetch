from dataclasses import dataclass
from typing import Optional

from wiki_fetch.base.extract.clean import strip
from wiki_fetch.base.html.fetch import Transport
from wiki_fetch.base.html.query import find, select_one
from wiki_fetch.base.html.tokenizer import parse
from wiki_fetch.base.html.tree import Document, Element, Node
from wiki_fetch.core.config import Site
from wiki_fetch.core.errors import PageError
from wiki_fetch.generic import markup, syntax


@dataclass(frozen=True, slots=True)
class Page:
    url: str
    root: Element


def locate(document: Document, url: str) -> Element:
    found: Optional[Element] = None
    scope: Node = document.root
    for layer in markup.LAYERS:
        deeper = select_one(scope, layer)
        if deeper is not None:
            found = scope = deeper
    if found is None:
        raise PageError(url)
    return found


def detour(root: Element, edition: Site) -> Optional[str]:
    results = select_one(root, markup.SELECTORS.search)
    if results is None:
        return None
    link = find(select_one(results, markup.SELECTORS.result) or results, syntax.Tag.ANCHOR)
    return None if link is None else edition.join(link.attrs.get(syntax.Attribute.HREF, str()))


def resolve(url: str, edition: Site, transport: Transport) -> Page:
    answer = transport.fetch(url)
    root = locate(parse(answer.text), answer.url)
    target = detour(root, edition)
    if target is not None:
        answer = transport.fetch(target)
        root = locate(parse(answer.text), answer.url)
    strip(root)
    return Page(url=answer.url, root=root)
