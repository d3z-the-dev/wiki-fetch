from wiki_fetch.base.render import dict as dictionary
from wiki_fetch.base.render import json as jsonize
from wiki_fetch.base.render import text as textize
from wiki_fetch.core.models import Block, Cell, Row
from wiki_fetch.generic import parts

TABLES = (
    Block(
        label='The Doors',
        rows=(
            Row(
                label='Background information',
                cells=(
                    Cell(
                        data={
                            'Origin': 'Los Angeles',
                            'Genres': ('Psychedelic rock', 'Blues rock'),
                        }
                    ),
                ),
            ),
        ),
    ),
    Block(label='Awards', rows=(Row(label='1993', cells=(Cell(data='Hall of Fame'),)),)),
)

FIRST = {
    'The Doors': {
        'Background information': {
            'Origin': 'Los Angeles',
            'Genres': ('Psychedelic rock', 'Blues rock'),
        }
    }
}


def test_dict_shape_for_first() -> None:
    assert dictionary.build(TABLES, parts.Selection.first) == FIRST


def test_dict_shape_for_last() -> None:
    assert dictionary.build(TABLES, parts.Selection.last) == {'Awards': {'1993': 'Hall of Fame'}}


def test_dict_shape_for_all_holds_every_table() -> None:
    assert dictionary.build(TABLES, parts.Selection.all) == (
        dictionary.build(TABLES, parts.Selection.first),
        dictionary.build(TABLES, parts.Selection.last),
    )


def test_rows_of_several_cells_become_a_tuple() -> None:
    wide = (Block(label='Grid', rows=(Row(label='1', cells=(Cell(data='a'), Cell(data='b'))),)),)
    assert dictionary.build(wide, parts.Selection.first) == {'Grid': {'1': ('a', 'b')}}


def test_rows_sharing_a_label_are_all_kept() -> None:
    repeated = (
        Block(
            label='Awards',
            rows=(
                Row(label='1993', cells=(Cell(data='Hall of Fame'),)),
                Row(label='1993', cells=(Cell(data='Grammy'),)),
                Row(label='1993', cells=(Cell(data='Inducted'),)),
            ),
        ),
    )
    assert dictionary.build(repeated, parts.Selection.first) == {
        'Awards': {'1993': 'Hall of Fame', '1993 2': 'Grammy', '1993 3': 'Inducted'}
    }


def test_nothing_extracted_stays_empty() -> None:
    assert dictionary.build((), parts.Selection.first) == {}
    assert dictionary.build((), parts.Selection.last) == {}
    assert dictionary.build((), parts.Selection.all) == ()


def test_text_matches_the_documented_layout() -> None:
    payload = {'Infobox': dictionary.build(TABLES, parts.Selection.first), 'URL': 'https://x'}
    assert textize.build(payload) == (
        'Infobox: \n'
        '    The Doors: \n'
        '        Background information: \n'
        '            Origin: Los Angeles\n'
        '            Genres: \n'
        '                Psychedelic rock\n'
        '                Blues rock\n'
        'URL: https://x'
    )


def test_text_unwraps_a_list_of_tables() -> None:
    payload = {'Table': dictionary.build(TABLES, parts.Selection.all)}
    assert textize.build(payload) == (
        'Table: \n'
        '        The Doors: \n'
        '            Background information: \n'
        '                Origin: Los Angeles\n'
        '                Genres: \n'
        '                    Psychedelic rock\n'
        '                    Blues rock\n'
        '        Awards: \n'
        '            1993: Hall of Fame'
    )


def test_text_spells_out_missing_values() -> None:
    assert textize.build({'Result': None}) == 'Result: null'


def test_json_is_indented_and_keeps_unicode() -> None:
    rendered = jsonize.build({'Infobox': {'Дорз': 'ок'}})
    assert '"Дорз": "ок"' in rendered
    assert rendered.startswith('{\n    ')


def test_json_writes_tuples_as_arrays() -> None:
    assert jsonize.build({'Genres': ('rock', 'blues')}) == (
        '{\n    "Genres": [\n        "rock",\n        "blues"\n    ]\n}'
    )
