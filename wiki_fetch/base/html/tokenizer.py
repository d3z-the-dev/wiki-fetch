from html.parser import HTMLParser
from typing import Optional

from wiki_fetch.base.html.tree import Document, Element, Text, attach
from wiki_fetch.generic import syntax


class Builder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Element(tag=syntax.Tag.ROOT)
        self.stack: list[Element] = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        self.unwind(syntax.IMPLICIT.get(tag, frozenset()))
        element = Element(tag=tag, attrs={name: value or str() for name, value in attrs})
        attach(self.stack[-1], element)
        if tag not in syntax.VOID:
            self.stack.append(element)

    def handle_endtag(self, tag: str) -> None:
        for depth in range(len(self.stack) - 1, 0, -1):
            if self.stack[depth].tag == tag:
                del self.stack[depth:]
                return

    def handle_data(self, data: str) -> None:
        attach(self.stack[-1], Text(content=data))

    def unwind(self, targets: frozenset[str]) -> None:
        while len(self.stack) > 1 and self.stack[-1].tag in targets:
            self.stack.pop()


def parse(source: str) -> Document:
    builder = Builder()
    builder.feed(source)
    builder.close()
    return Document(root=builder.root)
