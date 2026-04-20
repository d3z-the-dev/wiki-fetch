from wiki_fetch.base.extract.parts import Paragraph
from wiki_fetch.base.html.tokenizer import parse

PAGE = parse(
    '<div><p>Intro line</p>'
    "<div class='mw-heading mw-heading2'><h2>History</h2></div>"
    '<p>Formed in 1965</p>'
    "<div class='mw-heading mw-heading3'><h3>Early years</h3></div>"
    '<p>Whisky a Go Go</p>'
    "<div class='mw-heading mw-heading2'><h2>Legacy</h2></div>"
    '<p>Inducted in 1993</p></div>'
).root


def test_sections_split_on_h2() -> None:
    assert [table.label for table in Paragraph.read(PAGE)] == ['Prologue', 'History', 'Legacy']


def test_subsections_become_rows() -> None:
    history = Paragraph.read(PAGE)[1]
    assert [row.label for row in history.rows] == ['History', 'Early years']
    assert history.rows[1].cells[0].data == ('Whisky a Go Go',)


def test_prologue_keeps_the_leading_text() -> None:
    prologue = Paragraph.read(PAGE)[0]
    assert prologue.rows[0].label == 'Prologue'
    assert prologue.rows[0].cells[0].data == ('Intro line',)


def test_empty_sections_are_dropped() -> None:
    empty = parse("<div><div class='mw-heading'><h2>Notes</h2></div></div>").root
    assert Paragraph.read(empty) == ()
