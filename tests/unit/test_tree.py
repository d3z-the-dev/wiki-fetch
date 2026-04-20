import sys
import weakref

from wiki_fetch.base.html.tree import (
    Element,
    Text,
    ancestors,
    attach,
    classes,
    elements,
    remove,
    walk,
)


def chain(depth: int) -> Element:
    root = Element(tag='div')
    node = root
    for _ in range(depth):
        child = Element(tag='div')
        attach(node, child)
        node = child
    attach(node, Text(content='deep'))
    return root


def test_walk_visits_in_document_order() -> None:
    root = Element(tag='ul')
    for label in ('a', 'b'):
        entry = Element(tag='li')
        attach(entry, Text(content=label))
        attach(root, entry)
    seen: list[str] = list()
    for node in walk(root):
        if isinstance(node, Element):
            seen.append(node.tag)
        if isinstance(node, Text):
            seen.append(node.content)
    assert seen == ['ul', 'li', 'a', 'li', 'b']


def test_deep_tree_does_not_hit_recursion_limit() -> None:
    depth = sys.getrecursionlimit() * 2
    assert sum(1 for _ in walk(chain(depth))) == depth + 2


def test_parent_link_resolves() -> None:
    root = Element(tag='table')
    row = Element(tag='tr')
    attach(root, row)
    assert row.parent is root
    assert [node.tag for node in ancestors(row)] == ['table']


def test_parent_link_does_not_create_a_cycle() -> None:
    root = Element(tag='div')
    attach(root, Element(tag='p'))
    monitor = weakref.ref(root)
    del root
    assert monitor() is None


def test_classes_are_tokenised() -> None:
    element = Element(tag='table', attrs={'class': 'infobox vcard plainlist'})
    assert classes(element) == frozenset({'infobox', 'vcard', 'plainlist'})
    assert 'info' not in classes(element)


def test_remove_detaches_from_parent() -> None:
    root = Element(tag='p')
    span = Element(tag='span')
    attach(root, span)
    remove(span)
    assert list(elements(root)) == [root]
    assert span.parent is None


def test_detached_node_removal_is_a_no_op() -> None:
    orphan = Element(tag='div')
    remove(orphan)
    assert orphan.parent is None
