from wiki_fetch.base.extract.parts import Contents
from wiki_fetch.base.html.tokenizer import parse

PAGE = parse(
    '<div>'
    "<div class='mw-heading mw-heading2'><h2>History</h2></div>"
    "<div class='mw-heading mw-heading3'><h3>Early years</h3></div>"
    "<div class='mw-heading mw-heading3'><h3>Breakthrough</h3></div>"
    "<div class='mw-heading mw-heading2'><h2>Legacy</h2></div>"
    '</div>'
).root


def test_toc_numbers_follow_heading_levels() -> None:
    rows = Contents.read(PAGE)[0].rows
    assert [row.label for row in rows] == ['1', '1.1', '1.2', '2']
    assert [row.cells[0].data for row in rows] == [
        'History',
        'Early years',
        'Breakthrough',
        'Legacy',
    ]


def test_toc_is_a_single_table() -> None:
    tables = Contents.read(PAGE)
    assert len(tables) == 1
    assert tables[0].label == 'Contents'


def test_deeper_counters_restart_under_a_new_section() -> None:
    deep = parse(
        '<div>'
        "<div class='mw-heading'><h2>One</h2></div>"
        "<div class='mw-heading'><h3>One A</h3></div>"
        "<div class='mw-heading'><h4>One A i</h4></div>"
        "<div class='mw-heading'><h2>Two</h2></div>"
        "<div class='mw-heading'><h3>Two A</h3></div>"
        '</div>'
    ).root
    assert [row.label for row in Contents.read(deep)[0].rows] == ['1', '1.1', '1.1.1', '2', '2.1']


def test_pages_without_headings_yield_nothing() -> None:
    assert Contents.read(parse('<div><p>text only</p></div>').root) == ()
