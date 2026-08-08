import pytest

from tests.support import DISAMBIG_PAGE, EMPTY_PAGE, SEARCH_PAGE, Recorder, article
from wiki_fetch.base.html.query import select
from wiki_fetch.core.config import Site
from wiki_fetch.core.errors import PageError
from wiki_fetch.core.page import resolve

SEARCH = 'https://en.wikipedia.org/?search=zzzq'
MERCURY = 'https://en.wikipedia.org/wiki/Mercury'
DOORS = 'https://en.wikipedia.org/wiki/The_Doors'


def test_resolve_follows_the_first_search_result() -> None:
    transport = Recorder({SEARCH: SEARCH_PAGE, DOORS: article()})
    page = resolve(SEARCH, Site(), transport)
    assert page.url == DOORS
    assert transport.calls == [SEARCH, DOORS]


def test_resolve_reports_the_url_a_redirect_landed_on() -> None:
    transport = Recorder({SEARCH: article()}, redirects={SEARCH: DOORS})
    page = resolve(SEARCH, Site(), transport)
    assert page.url == DOORS
    assert transport.calls == [SEARCH]


def test_a_disambiguation_page_is_taken_as_it_is() -> None:
    transport = Recorder({MERCURY: DISAMBIG_PAGE})
    page = resolve(MERCURY, Site(), transport)
    assert page.url == MERCURY
    assert transport.calls == [MERCURY]


def test_a_disambiguation_page_keeps_every_link_it_lists() -> None:
    transport = Recorder({MERCURY: DISAMBIG_PAGE})
    root = resolve(MERCURY, Site(), transport).root
    listed = [link.attrs.get('href') for link in select(root, 'a')]
    assert listed == ['/wiki/Category:Planets', '/wiki/Mercury_(planet)']


def test_a_plain_article_is_taken_as_it_is() -> None:
    transport = Recorder({DOORS: article()})
    page = resolve(DOORS, Site(), transport)
    assert page.url == DOORS
    assert transport.calls == [DOORS]


def test_resolve_reports_the_url_the_answer_actually_came_from() -> None:
    transport = Recorder({SEARCH: article()}, redirects={SEARCH: DOORS})
    page = resolve(SEARCH, Site(), transport)
    assert page.url == DOORS
    assert transport.calls == [SEARCH]


def test_resolve_reaches_the_parser_output() -> None:
    transport = Recorder({DOORS: article()})
    root = resolve(DOORS, Site(), transport).root
    assert 'mw-parser-output' in root.attrs.get('class', '')


def test_resolve_strips_the_chrome() -> None:
    transport = Recorder({DOORS: article()})
    assert select(resolve(DOORS, Site(), transport).root, '.mw-editsection') == ()


def test_missing_content_raises_page_error() -> None:
    transport = Recorder({DOORS: EMPTY_PAGE})
    with pytest.raises(PageError):
        resolve(DOORS, Site(), transport)
