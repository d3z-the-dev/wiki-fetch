import pytest

from wiki_fetch.core.errors import InputError
from wiki_fetch.core.languages import resolve
from wiki_fetch.generic.languages import ALIASES, CODES, NAMES, PATTERN

SPELLINGS = [*CODES, *(spelling for spellings in ALIASES.values() for spelling in spellings)]


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        ('English', 'en'),
        ('english', 'en'),
        ('Русский', 'ru'),
        ('Nederlands', 'nl'),
        ('Chinese', 'zh'),
        ('Dutch', 'nl'),
        ('Türkçe', 'tr'),
        ('한국어', 'ko'),
        ('Bahasa Indonesia', 'id'),
        ('ja', 'ja'),
        ('pt', 'pt'),
        ('zh-yue', 'zh-yue'),
    ],
)
def test_resolve_accepts_names_endonyms_and_codes(value: str, expected: str) -> None:
    assert resolve(value) == expected


@pytest.mark.parametrize('value', ['Klingon', '', 'e', 'ENGLISH!', 'toolongcode'])
def test_resolve_rejects_nonsense(value: str) -> None:
    with pytest.raises(InputError):
        resolve(value)


def test_resolve_trims_surrounding_space() -> None:
    assert resolve('  Deutsch  ') == 'de'


@pytest.mark.parametrize('value', SPELLINGS)
def test_every_configured_spelling_resolves_in_any_case(value: str) -> None:
    assert resolve(value.upper()) == resolve(value.lower()) == resolve(value)


@pytest.mark.parametrize('value', ['RU', 'Zh-Yue', 'CEB'])
def test_codes_resolve_in_any_case(value: str) -> None:
    assert resolve(value) == value.casefold()


def test_the_codes_came_from_the_configuration() -> None:
    assert CODES['english'] == 'en'
    assert CODES['chinese'] == 'zh'


def test_the_named_editions_cover_the_largest_wikipedias() -> None:
    assert len(CODES) >= 30
    assert {'en', 'de', 'fr', 'es', 'ru', 'ja', 'ar', 'fa', 'ko', 'tr', 'vi'} <= set(CODES.values())


def test_every_named_edition_carries_a_distinct_code() -> None:
    assert len(set(CODES.values())) == len(CODES)


def test_endonyms_resolve_to_the_same_code_as_their_english_name() -> None:
    assert NAMES['русский'] == NAMES['russian'] == 'ru'
    assert NAMES['español'] == NAMES['spanish'] == 'es'


def test_every_alias_names_a_configured_edition() -> None:
    assert set(ALIASES) <= set(CODES)


def test_the_section_code_pattern_stays_narrow() -> None:
    assert PATTERN.match('ceb') is not None
    assert PATTERN.match('englsh') is None
