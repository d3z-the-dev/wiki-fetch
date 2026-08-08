from wiki_fetch.base.extract.registry import EXTRACTORS, extract
from wiki_fetch.base.html.tokenizer import parse
from wiki_fetch.generic import parts

PAGE = parse(
    '<div>'
    "<div class='mw-heading mw-heading2'><h2>History</h2></div>"
    '<p>The band formed in 1965.</p>'
    '<ul><li>Jim Morrison</li></ul>'
    '</div>'
).root


def test_every_extractor_declares_the_part_it_reads() -> None:
    assert {extractor.part for extractor in EXTRACTORS} == set(parts.Part) - {parts.Part.all}


def test_extract_one_part_returns_one_piece() -> None:
    found = extract(parts.Part.list, PAGE)
    assert len(found) == 1
    assert found[0].label == 'List'
    assert found[0].blocks[0].rows[0].cells[0].data == 'Jim Morrison'


def test_missing_parts_come_back_empty_rather_than_absent() -> None:
    infobox = next(piece for piece in extract(parts.Part.all, PAGE) if piece.label == 'Infobox')
    assert infobox.blocks == ()


def test_extract_returns_pieces_in_the_documented_order() -> None:
    found = extract(parts.Part.all, PAGE)
    assert [piece.label for piece in found] == [
        'Infobox',
        'Paragraph',
        'Table',
        'List',
        'Thumb',
        'Toc',
    ]


def test_a_part_that_matches_nothing_still_yields_a_piece() -> None:
    found = extract(parts.Part.toc, parse('<div></div>').root)
    assert len(found) == 1
    assert found[0].part is parts.Part.toc
    assert found[0].blocks == ()
