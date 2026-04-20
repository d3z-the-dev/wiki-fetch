from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Optional
from weakref import ReferenceType, ref

from wiki_fetch.generic import syntax

type Parent = Element


@dataclass(slots=True, weakref_slot=True, eq=False, kw_only=True)
class Node:
    origin: Optional[ReferenceType[Parent]] = None

    @property
    def parent(self) -> Optional[Parent]:
        return None if self.origin is None else self.origin()


@dataclass(slots=True, eq=False, kw_only=True)
class Element(Node):
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list[Node] = field(default_factory=list)


@dataclass(slots=True, eq=False, kw_only=True)
class Text(Node):
    content: str


@dataclass(slots=True)
class Document:
    root: Element


def attach(parent: Element, child: Node) -> None:
    child.origin = ref(parent)
    parent.children.append(child)


def classes(element: Element) -> frozenset[str]:
    return frozenset(element.attrs.get(syntax.Attribute.CLASS, str()).split())


def walk(root: Node) -> Iterator[Node]:
    stack: list[Node] = [root]
    while stack:
        node = stack.pop()
        yield node
        if isinstance(node, Element):
            stack.extend(reversed(node.children))


def elements(root: Node) -> Iterator[Element]:
    return (node for node in walk(root) if isinstance(node, Element))


def ancestors(node: Node) -> Iterator[Element]:
    current = node.parent
    while current is not None:
        yield current
        current = current.parent


def remove(node: Node) -> None:
    parent = node.parent
    if parent is None:
        return
    parent.children.remove(node)
    node.origin = None
