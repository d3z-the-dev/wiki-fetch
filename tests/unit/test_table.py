from wiki_fetch.base.extract.parts import Table
from wiki_fetch.base.html.tokenizer import parse

PAGE = parse(
    "<div><div class='mw-heading'><h3>Awards</h3></div>"
    "<table class='wikitable'>"
    '<tr><th>Year</th><th>Award</th><th>Result</th></tr>'
    "<tr><td rowspan='2'>1993</td><td>Hall of Fame</td><td>Inducted</td></tr>"
    "<tr><td colspan='2'>Nominated</td></tr>"
    '</table></div>'
).root


def test_heading_becomes_the_table_label() -> None:
    assert Table.read(PAGE)[0].label == 'Awards'


def test_header_row_is_labelled_by_position() -> None:
    assert Table.read(PAGE)[0].rows[0].label == 'Headers 1'


def test_rowspan_repeats_the_cell_with_a_counter() -> None:
    labels = [row.label for row in Table.read(PAGE)[0].rows]
    assert labels[1] == '1993'
    assert labels[2] == '1993 [2]'


def test_colspan_pads_the_row() -> None:
    assert len(Table.read(PAGE)[0].rows[2].cells) == 2


def test_rows_without_a_string_first_cell_are_numbered_and_keep_every_cell() -> None:
    grid = parse(
        "<div><table class='wikitable'>"
        '<tr><td></td><td>alpha</td></tr>'
        '<tr><td>one<br>two</td><td>beta</td></tr>'
        '</table></div>'
    ).root
    rows = Table.read(grid)[0].rows
    assert [row.label for row in rows] == ['Row 1', 'Row 2']
    assert [len(row.cells) for row in rows] == [2, 2]
    assert rows[1].cells[0].data == ('one', 'two')


def test_a_carried_cell_keeps_a_non_string_value_whole() -> None:
    grid = parse(
        "<div><table class='wikitable'>"
        '<tr><th>Year</th><th>Award</th></tr>'
        "<tr><td rowspan='2'>one<br>two</td><td>beta</td></tr>"
        '<tr><td>gamma</td></tr>'
        '</table></div>'
    ).root
    rows = Table.read(grid)[0].rows
    assert rows[1].cells[0].data == ('one', 'two')
    assert rows[2].cells[0].data == ('one', 'two')


def test_tables_without_a_heading_fall_back() -> None:
    orphan = parse("<div><table class='wikitable'><tr><td>a</td><td>b</td></tr></table></div>").root
    assert Table.read(orphan)[0].label == 'No header'


def test_plain_tables_are_ignored() -> None:
    assert Table.read(parse('<div><table><tr><td>a</td></tr></table></div>').root) == ()
