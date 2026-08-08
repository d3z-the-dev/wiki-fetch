from wiki_fetch.base.html.query import after, before, find, find_all, preceding, text
from wiki_fetch.base.html.tokenizer import parse

PAGE = parse(
    "<div id='content'>"
    "<div class='mw-heading mw-heading2'><h2>History</h2></div>"
    '<p>First <b>bold</b> line</p>'
    "<table class='wikitable'><tr><th>k</th><td>v</td></tr></table>"
    '<script>ignored()</script>'
    '</div>'
).root


def test_find_all_by_tag_and_class_uses_tokens() -> None:
    assert len(find_all(PAGE, 'div', classes='mw-heading')) == 1
    assert find_all(PAGE, 'div', classes='mw-head') == ()


def test_find_all_accepts_a_tag_sequence() -> None:
    assert len(find_all(PAGE, ('th', 'td'))) == 2


def test_find_all_never_returns_the_root() -> None:
    table = find(PAGE, 'table')
    assert table is not None
    assert find_all(table, 'table') == ()


def test_recursive_false_limits_to_direct_children() -> None:
    table = find(PAGE, 'table')
    assert table is not None
    assert find_all(table, 'td', recursive=False) == ()
    assert len(find_all(table, 'tr', recursive=False)) == 1


def test_limit_truncates() -> None:
    assert len(find_all(PAGE, ('div', 'p', 'table'), limit=2)) == 2


def test_find_returns_none_when_nothing_matches() -> None:
    assert find(PAGE, 'figure') is None


def test_text_collapses_and_skips_scripts() -> None:
    assert text(PAGE, separator=' ') == 'History First bold line k v'


def test_text_of_none_is_empty() -> None:
    assert text(None) == ''


def test_preceding_finds_the_earlier_heading() -> None:
    table = find(PAGE, 'table')
    assert table is not None
    assert text(preceding(table, 'h2')) == 'History'


def test_preceding_returns_none_at_the_start() -> None:
    heading = find(PAGE, 'h2')
    assert heading is not None
    assert preceding(heading, 'table') is None


def test_siblings_step_both_ways() -> None:
    table = find(PAGE, 'table')
    assert table is not None
    earlier = before(table)
    assert earlier is not None
    assert after(earlier) is table


def test_siblings_stop_at_the_edges() -> None:
    root = PAGE.children[0]
    assert before(root) is None
    assert after(PAGE.children[-1]) is None
