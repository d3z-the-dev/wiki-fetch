import pytest

from wiki_fetch.core.models import Block, Cell, Piece, Row
from wiki_fetch.generic import parts


def test_models_are_frozen_and_slotted() -> None:
    cell = Cell(data='value')
    with pytest.raises(AttributeError):
        cell.data = 'other'
    assert not hasattr(cell, '__dict__')


def test_model_defaults_are_immutable_containers() -> None:
    assert Row().cells == ()
    assert Block().rows == ()


def test_piece_label_for_every_part() -> None:
    expected = {
        parts.Part.infobox: 'Infobox',
        parts.Part.paragraph: 'Paragraph',
        parts.Part.table: 'Table',
        parts.Part.list: 'List',
        parts.Part.thumb: 'Thumb',
        parts.Part.toc: 'Toc',
    }
    for part, label in expected.items():
        piece = Piece(part=part)
        assert type(piece.label) is str
        assert piece.label == label


def test_piece_label_covers_the_all_member_too() -> None:
    assert Piece(part=parts.Part.all).label == 'All'


def test_piece_is_slotted() -> None:
    assert not hasattr(Piece(part=parts.Part.infobox), '__dict__')
