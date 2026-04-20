from wiki_fetch.base.extract.parts import List
from wiki_fetch.base.html.tokenizer import parse

LISTS = parse(
    "<div><div class='mw-heading'><h2>Legacy</h2></div>"
    '<ul><li>Inducted in 1993</li><li>Grammy in 1998</li></ul>'
    "<table class='wikitable'><tr><td><ul><li>skip me</li></ul></td></tr></table>"
    "<div class='navbox'><ul><li>navigation</li></ul></div></div>"
).root


def test_listing_takes_content_lists_only() -> None:
    tables = List.read(LISTS)
    assert len(tables) == 1
    assert tables[0].label == 'Legacy'
    assert [row.label for row in tables[0].rows] == ['1', '2']


def test_listing_keeps_the_item_text() -> None:
    assert [row.cells[0].data for row in List.read(LISTS)[0].rows] == [
        'Inducted in 1993',
        'Grammy in 1998',
    ]


def test_listing_falls_back_when_no_heading_precedes() -> None:
    orphan = parse('<div><ul><li>alone</li></ul></div>').root
    assert List.read(orphan)[0].label == 'No header'


def test_nested_items_stay_with_their_own_list() -> None:
    nested = parse('<div><ul><li>outer<ul><li>inner</li></ul></li></ul></div>').root
    assert [len(table.rows) for table in List.read(nested)] == [1, 1]
