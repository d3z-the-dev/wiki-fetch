import pytest

from tests.live import fetched
from tests.pages import PAGES, Expectation

pytestmark = pytest.mark.network

CASES = pytest.mark.parametrize('page', PAGES, ids=lambda page: page.name)


def counted(page: Expectation, key: str) -> int:
    found = fetched(page).dict[key]
    assert isinstance(found, tuple)
    return len(found)


@CASES
def test_every_documented_key_is_present(page: Expectation) -> None:
    assert list(fetched(page).dict) == [
        'Infobox',
        'Paragraph',
        'Table',
        'List',
        'Thumb',
        'Toc',
        'URL',
    ]


@CASES
def test_the_url_key_survives_a_non_ascii_address(page: Expectation) -> None:
    assert fetched(page).dict['URL'] == page.url


@CASES
def test_the_toc_opens_with_the_first_section(page: Expectation) -> None:
    toc = fetched(page).dict['Toc']
    assert isinstance(toc, tuple) and toc
    first = toc[0]
    assert isinstance(first, dict)
    sections = first['Contents']
    assert isinstance(sections, dict) and sections
    number, title = next(iter(sections.items()))
    assert number == '1'
    assert isinstance(title, str) and title
    assert title in fetched(page).text


@CASES
@pytest.mark.parametrize('key', ['Infobox', 'Paragraph', 'List', 'Thumb'])
def test_counts_stay_inside_the_recorded_range(page: Expectation, key: str) -> None:
    low, high = {
        'Infobox': page.infobox,
        'Paragraph': page.paragraph,
        'List': page.listing,
        'Thumb': page.thumb,
    }[key]
    assert low <= counted(page, key) <= high


@CASES
def test_the_prose_reaches_the_text_rendering(page: Expectation) -> None:
    blocks = fetched(page).dict['Paragraph']
    assert isinstance(blocks, tuple) and blocks
    text = fetched(page).text
    assert page.title in text
    for block in blocks:
        assert isinstance(block, dict)
        for section in block.values():
            assert isinstance(section, dict)
            for sentences in section.values():
                assert isinstance(sentences, tuple)
                for sentence in sentences:
                    assert isinstance(sentence, str)
                    assert sentence in text


@CASES
def test_illustrations_are_addressed_over_https(page: Expectation) -> None:
    thumbs = fetched(page).dict['Thumb']
    assert isinstance(thumbs, tuple)
    for table in thumbs:
        assert isinstance(table, dict)
        for rows in table.values():
            assert isinstance(rows, dict)
            for link in rows.values():
                assert isinstance(link, str) and link.startswith('https://')
