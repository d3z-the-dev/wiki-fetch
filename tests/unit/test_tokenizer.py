from wiki_fetch.base.html.tokenizer import parse
from wiki_fetch.base.html.tree import Element, Text, elements


def tags(source: str) -> list[str]:
    return [node.tag for node in elements(parse(source).root)]


def first(source: str, tag: str) -> Element:
    return next(node for node in elements(parse(source).root) if node.tag == tag)


def test_void_elements_do_not_swallow_siblings() -> None:
    assert tags('<div><br><img src=x><p>text</p></div>') == ['html', 'div', 'br', 'img', 'p']


def test_self_closing_syntax_is_accepted() -> None:
    assert tags('<div><br /><span>tail</span></div>') == ['html', 'div', 'br', 'span']


def test_unclosed_list_items_close_implicitly() -> None:
    assert tags('<ul><li>one<li>two</ul>').count('li') == 2


def test_nested_lists_keep_their_depth() -> None:
    document = parse('<ul><li>a<ul><li>b<li>c</ul><li>d</ul>')
    outer = next(node for node in elements(document.root) if node.tag == 'ul')
    assert [node.tag for node in outer.children if isinstance(node, Element)] == ['li', 'li']


def test_unclosed_cells_close_implicitly() -> None:
    assert tags('<table><tr><th>k<td>v<tr><th>k2<td>v2</table>').count('tr') == 2


def test_script_content_is_raw() -> None:
    assert 'b' not in tags("<div><script>var a = '<b>not markup</b>';</script></div>")


def test_entities_are_decoded() -> None:
    paragraph = first('<p>Rock &amp; Roll</p>', 'p')
    assert [node.content for node in paragraph.children if isinstance(node, Text)] == [
        'Rock & Roll'
    ]


def test_attribute_entities_are_decoded() -> None:
    link = first("<a href='/w/index.php?a=1&amp;b=2'>x</a>", 'a')
    assert link.attrs['href'] == '/w/index.php?a=1&b=2'


def test_malformed_markup_does_not_raise() -> None:
    document = parse('<div><p>text</div></span><b>tail')
    assert document.root.tag == 'html'
    assert 'b' in [node.tag for node in elements(document.root)]


def test_attributes_without_value_become_empty_strings() -> None:
    assert first('<input disabled>', 'input').attrs['disabled'] == ''


def test_comments_and_doctype_are_dropped() -> None:
    assert tags('<!DOCTYPE html><!-- note --><p>x</p>') == ['html', 'p']
