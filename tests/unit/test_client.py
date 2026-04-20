import pytest

from tests.support import Recorder, article
from wiki_fetch import Output, Wiki
from wiki_fetch.core.errors import InputError

URL = 'https://en.wikipedia.org/wiki/The_Doors'
RUSSIAN = 'https://ru.wikipedia.org/wiki/The_Doors'


def wiki(lang: str = 'English') -> Wiki:
    return Wiki(lang, transport=Recorder({URL: article(), RUSSIAN: article('The Doors')}))


def test_search_returns_all_three_forms() -> None:
    output = wiki().search(url=URL, part='infobox', item='first')
    assert isinstance(output, Output)
    assert output.dict['Infobox']
    assert output.text.startswith('Infobox: ')
    assert '"Infobox"' in output.json


def test_url_key_is_unquoted_and_last() -> None:
    output = wiki().search(url=URL, part='toc')
    assert list(output.dict) == ['Toc', 'URL']
    assert output.dict['URL'] == URL


def test_all_parts_are_present_and_populated() -> None:
    output = wiki().search(url=URL)
    assert list(output.dict) == ['Infobox', 'Paragraph', 'Table', 'List', 'Thumb', 'Toc', 'URL']
    for part in ('Infobox', 'Paragraph', 'List', 'Thumb', 'Toc'):
        assert output.dict[part], f'{part} is empty'


def test_a_query_is_sent_to_the_chosen_language_edition() -> None:
    transport = Recorder({})
    with pytest.raises(AssertionError):
        Wiki('Russian', transport=transport).search(query='The Doors')
    assert transport.calls == ['https://ru.wikipedia.org/?search=The%20Doors']


def test_a_language_code_works_as_well_as_a_name() -> None:
    assert Wiki('ru').site.base == 'https://ru.wikipedia.org/'


def test_unknown_language_raises() -> None:
    with pytest.raises(InputError):
        Wiki('Klingonese')


def test_missing_input_raises() -> None:
    with pytest.raises(InputError) as failure:
        wiki().search()
    assert str(failure.value) == 'No input: give a URL or a query.'


@pytest.mark.parametrize(('field', 'value'), [('part', 'sidebar'), ('item', 'second')])
def test_unknown_enumeration_values_raise(field: str, value: str) -> None:
    with pytest.raises(InputError):
        wiki().search(url=URL, **{field: value})


def collected(value: object, found: list[object]) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            found.append(key)
            collected(nested, found)
    elif isinstance(value, tuple | list):
        for nested in value:
            collected(nested, found)


def test_dict_keys_are_plain_strings() -> None:
    found: list[object] = list()
    collected(wiki().search(url=URL).dict, found)
    assert [key for key in found if type(key) is not str] == []
