import tomllib

from wiki_fetch.base.render import dict as dictionary
from wiki_fetch.base.render import toml as tomlize
from wiki_fetch.core.models import Block, Cell, Row
from wiki_fetch.generic import layout, parts, types

PAYLOAD = {
    'Infobox': {
        'The Doors': {
            'Background information': {
                'Origin': 'Los Angeles',
                'Genres': ('Psychedelic rock', 'blues rock'),
                'Website': None,
            }
        }
    },
    'URL': 'https://en.wikipedia.org/wiki/The_Doors',
}


def flattened(value: types.Data) -> object:
    if isinstance(value, dict):
        return {key: flattened(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [flattened(item) for item in value]
    return layout.MISSING if value is None else value


def test_output_parses_back_into_the_same_shape() -> None:
    assert tomllib.loads(tomlize.build(PAYLOAD)) == flattened(PAYLOAD)


def test_bare_values_are_written_before_any_table() -> None:
    lines = tomlize.build(PAYLOAD).splitlines()
    assert lines[0] == 'URL = "https://en.wikipedia.org/wiki/The_Doors"'
    assert lines[2] == '[Infobox."The Doors"."Background information"]'


def test_keys_are_quoted_only_when_they_have_to_be() -> None:
    rendered = tomlize.build({'Origin': 'LA', 'Years active': '1965-1973'})
    assert rendered == 'Origin = "LA"\n"Years active" = "1965-1973"'


def test_missing_values_keep_the_layout_spelling() -> None:
    assert f'Website = "{layout.MISSING}"' in tomlize.build(PAYLOAD)


def test_quotes_backslashes_and_control_characters_are_escaped() -> None:
    payload = {'Caption': 'The "Stovepipe Cup"\\ tab\there'}
    rendered = tomlize.build(payload)
    assert rendered == 'Caption = "The \\"Stovepipe Cup\\"\\\\ tab\\there"'
    assert tomllib.loads(rendered) == payload


def test_unicode_labels_survive_untouched() -> None:
    payload = {'Кубок Стэнли': {'Страна': 'Канада и США'}}
    assert tomllib.loads(tomlize.build(payload)) == payload


def test_a_tuple_of_tables_becomes_an_array_of_tables() -> None:
    tables = (
        Block(label='The Doors', rows=(Row(label='Origin', cells=(Cell(data='LA'),)),)),
        Block(label='Awards', rows=(Row(label='1993', cells=(Cell(data='Hall of Fame'),)),)),
    )
    payload = {'Infobox': dictionary.build(tables, parts.Selection.all)}
    rendered = tomlize.build(payload)
    assert rendered.count('[[Infobox]]') == 2
    assert tomllib.loads(rendered) == {
        'Infobox': [{'The Doors': {'Origin': 'LA'}}, {'Awards': {'1993': 'Hall of Fame'}}]
    }


def test_mixed_arrays_fall_back_to_inline_tables() -> None:
    payload = {'Row': ('plain', {'Origin': 'LA'}, None)}
    rendered = tomlize.build(payload)
    assert rendered == 'Row = ["plain", {Origin = "LA"}, "null"]'
    assert tomllib.loads(rendered) == {'Row': ['plain', {'Origin': 'LA'}, layout.MISSING]}


def test_empty_containers_stay_valid() -> None:
    assert tomlize.build(dict()) == str()
    assert tomllib.loads(tomlize.build({'Table': tuple(), 'Empty': dict()})) == {
        'Table': [],
        'Empty': {},
    }
