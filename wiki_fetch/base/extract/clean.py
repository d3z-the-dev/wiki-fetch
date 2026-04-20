from collections.abc import Iterator
from typing import Optional

from wiki_fetch.base.html.query import find, find_all, preceding, select
from wiki_fetch.base.html.text import normalize
from wiki_fetch.base.html.tree import Element, Node, Text, classes, elements, remove
from wiki_fetch.generic import markup, syntax, text, types


def hidden(element: Element) -> bool:
    return markup.HIDDEN.search(element.attrs.get(syntax.Attribute.STYLE, str())) is not None


def strip(root: Element) -> None:
    doomed = [
        *select(root, markup.SELECTORS.noise),
        *(node for node in elements(root) if hidden(node)),
    ]
    for node in doomed:
        remove(node)


def marked(element: Element, name: str) -> bool:
    return name in classes(element)


def sentence(node: Optional[Node]) -> str:
    return str() if node is None else normalize(text.SPACE.join(divide(node)))


def label(node: Optional[Node]) -> str:
    return markup.COLON.sub('', sentence(node))


def heading(block: Element) -> str:
    return sentence(preceding(block, markup.HEADINGS)) or markup.Label.nameless


def address(source: str) -> str:
    absolute = f'{markup.SCHEME}{source}' if source.startswith(markup.PROTOCOL) else source
    head, mark, query = absolute.partition(markup.QUESTION)
    if not mark:
        return absolute
    kept = markup.AMPERSAND.join(
        one for one in query.split(markup.AMPERSAND) if not one.startswith(markup.TRACKING)
    )
    return f'{head}{markup.QUESTION}{kept}' if kept else head


def divide(node: Node) -> Iterator[str]:
    parts: list[str] = list()
    stack: list[Node] = [node]
    while stack:
        current = stack.pop()
        if isinstance(current, Text):
            parts.append(current.content)
        elif not isinstance(current, Element) or current.tag in syntax.SILENT:
            continue
        elif current.tag == syntax.Tag.BREAK:
            yield ''.join(parts)
            parts = list()
        else:
            stack.extend(reversed(current.children))
    yield ''.join(parts)


def stream(root: Element, wanted: frozenset[str]) -> Iterator[Element]:
    stack: list[Node] = [root]
    while stack:
        current = stack.pop()
        if not isinstance(current, Element) or (
            current is not root and current.tag in markup.BARRIER
        ):
            continue
        if current.tag in wanted:
            yield current
        else:
            stack.extend(reversed(current.children))


def pieces(node: Element) -> tuple[str, ...]:
    bullets = [
        bullet
        for bullet in find_all(node, syntax.Tag.ITEM)
        if find(bullet, syntax.Tag.ITEM) is None
    ]
    if bullets:
        return tuple(value for value in (sentence(bullet) for bullet in bullets) if value)
    return tuple(value for value in (normalize(part) for part in divide(node)) if value)


def content(cell: Element) -> types.Data:
    found = pieces(cell)
    if not found:
        return None
    return found[0] if len(found) == 1 else found
