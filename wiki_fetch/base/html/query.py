import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Optional

from wiki_fetch.base.errors import SelectorError
from wiki_fetch.base.html import tree
from wiki_fetch.base.html.text import collapse
from wiki_fetch.base.html.tree import Element, Node, Text, ancestors, elements
from wiki_fetch.generic import syntax


@dataclass(frozen=True, slots=True)
class Condition:
    name: str
    value: Optional[str] = None
    prefix: bool = False

    def holds(self, element: Element) -> bool:
        found = element.attrs.get(self.name)
        if found is None:
            return False
        if self.value is None:
            return True
        return found.startswith(self.value) if self.prefix else found == self.value


@dataclass(frozen=True, slots=True)
class Rule:
    tags: frozenset[str] = frozenset()
    identifier: Optional[str] = None
    classes: frozenset[str] = frozenset()
    conditions: tuple[Condition, ...] = tuple()
    direct: bool = False

    def holds(self, element: Element) -> bool:
        if self.tags and element.tag not in self.tags:
            return False
        if (
            self.identifier is not None
            and element.attrs.get(syntax.Attribute.ID) != self.identifier
        ):
            return False
        if not self.classes <= tree.classes(element):
            return False
        return all(condition.holds(element) for condition in self.conditions)


@dataclass(slots=True)
class Draft:
    tag: Optional[str] = None
    identifier: Optional[str] = None
    classes: set[str] = field(default_factory=set)
    conditions: list[Condition] = field(default_factory=list)
    filled: bool = False

    def freeze(self, direct: bool) -> Rule:
        return Rule(
            tags=frozenset() if self.tag is None else frozenset({self.tag}),
            identifier=self.identifier,
            classes=frozenset(self.classes),
            conditions=tuple(self.conditions),
            direct=direct,
        )


def names(value: Optional[str | Sequence[str]]) -> frozenset[str]:
    if value is None:
        return frozenset()
    if isinstance(value, str):
        return frozenset({value})
    return frozenset(value)


def descendants(root: Node, recursive: bool) -> Iterator[Element]:
    if not isinstance(root, Element):
        return iter(())
    if not recursive:
        return (child for child in root.children if isinstance(child, Element))
    return (node for node in elements(root) if node is not root)


def gather(stream: Iterator[Element], rule: Rule, limit: Optional[int]) -> tuple[Element, ...]:
    found: list[Element] = list()
    for element in stream:
        if not rule.holds(element):
            continue
        found.append(element)
        if limit is not None and len(found) == limit:
            break
    return tuple(found)


def find_all(
    root: Node,
    tag: Optional[str | Sequence[str]] = None,
    *,
    classes: Optional[str | Sequence[str]] = None,
    recursive: bool = True,
    limit: Optional[int] = None,
) -> tuple[Element, ...]:
    rule = Rule(tags=names(tag), classes=names(classes))
    return gather(descendants(root, recursive), rule, limit)


def find(
    root: Node,
    tag: Optional[str | Sequence[str]] = None,
    *,
    classes: Optional[str | Sequence[str]] = None,
    recursive: bool = True,
) -> Optional[Element]:
    found = find_all(root, tag, classes=classes, recursive=recursive, limit=1)
    return found[0] if found else None


@lru_cache(maxsize=syntax.CACHE)
def compile_selector(selector: str) -> tuple[tuple[Rule, ...], ...]:
    return tuple(chain(group, selector) for group in selector.split(syntax.GROUP))


def chain(group: str, selector: str) -> tuple[Rule, ...]:
    source = group.strip()
    if not source:
        raise SelectorError(selector)
    rules: list[Rule] = list()
    draft = Draft()
    direct = False
    position = 0
    while position < len(source):
        found = syntax.TOKEN.match(source, position)
        if found is None:
            raise SelectorError(selector)
        position = found.end()
        combinator = found[syntax.Capture.combinator]
        if combinator is None:
            absorb(draft, found)
            continue
        if not draft.filled:
            raise SelectorError(selector)
        rules.append(draft.freeze(direct))
        draft = Draft()
        direct = syntax.CHILD in combinator
    if not draft.filled:
        raise SelectorError(selector)
    rules.append(draft.freeze(direct))
    return tuple(rules)


def absorb(draft: Draft, found: re.Match[str]) -> None:
    draft.filled = True
    if found[syntax.Capture.tag] is not None:
        draft.tag = found[syntax.Capture.tag].lower()
    elif found[syntax.Capture.identifier] is not None:
        draft.identifier = found[syntax.Capture.identifier]
    elif found[syntax.Capture.label] is not None:
        draft.classes.add(found[syntax.Capture.label])
    else:
        operator = found[syntax.Capture.operator]
        draft.conditions.append(
            Condition(
                name=found[syntax.Capture.attribute],
                value=None
                if operator is None
                else found[syntax.Capture.content].strip(syntax.QUOTES),
                prefix=operator == syntax.PREFIXED,
            )
        )


def fits(element: Element, rules: tuple[Rule, ...]) -> bool:
    stack: list[tuple[Element, int]] = [(element, len(rules) - 1)]
    while stack:
        node, index = stack.pop()
        if not rules[index].holds(node):
            continue
        if index == 0:
            return True
        if rules[index].direct:
            if node.parent is not None:
                stack.append((node.parent, index - 1))
            continue
        stack.extend((ancestor, index - 1) for ancestor in ancestors(node))
    return False


def select(root: Node, selector: str, *, limit: Optional[int] = None) -> tuple[Element, ...]:
    groups = compile_selector(selector)
    found: list[Element] = list()
    for element in descendants(root, recursive=True):
        if not any(fits(element, rules) for rules in groups):
            continue
        found.append(element)
        if limit is not None and len(found) == limit:
            break
    return tuple(found)


def select_one(root: Node, selector: str) -> Optional[Element]:
    found = select(root, selector, limit=1)
    return found[0] if found else None


def text(node: Optional[Node], *, separator: str = str()) -> str:
    if node is None:
        return str()
    parts: list[str] = list()
    stack: list[Node] = [node]
    while stack:
        current = stack.pop()
        if isinstance(current, Text):
            parts.append(current.content)
        elif isinstance(current, Element) and current.tag not in syntax.SILENT:
            stack.extend(reversed(current.children))
    return collapse(separator.join(parts))


def before(node: Node) -> Optional[Node]:
    parent = node.parent
    if parent is None:
        return None
    position = parent.children.index(node)
    return parent.children[position - 1] if position else None


def after(node: Node) -> Optional[Node]:
    parent = node.parent
    if parent is None:
        return None
    position = parent.children.index(node) + 1
    return parent.children[position] if position < len(parent.children) else None


def preceding(element: Element, tag: str | Sequence[str]) -> Optional[Element]:
    wanted = names(tag)
    current: Node = element
    while True:
        previous = before(current)
        if previous is None:
            parent = current.parent
            if parent is None:
                return None
            current = parent
            continue
        found = [node for node in elements(previous) if node.tag in wanted]
        if found:
            return found[-1]
        current = previous
