import pytest

from wiki_fetch.base.errors import (
    DecodeError,
    FetchError,
    SelectorError,
    StatusError,
    WikiError,
)
from wiki_fetch.core.errors import InputError, PageError
from wiki_fetch.generic.messages import Message


def test_status_error_carries_code_and_message() -> None:
    error = StatusError(status=429, url='https://en.wikipedia.org/wiki/A')
    assert isinstance(error, FetchError)
    assert isinstance(error, WikiError)
    assert error.status == 429
    assert '429' in str(error)


def test_input_error_uses_template() -> None:
    error = InputError(Message.language.format(value='Klingon'))
    assert str(error) == 'Unknown language: Klingon.'


def test_page_error_keeps_the_url() -> None:
    error = PageError('https://en.wikipedia.org/wiki/A')
    assert error.url == 'https://en.wikipedia.org/wiki/A'
    assert 'https://en.wikipedia.org/wiki/A' in str(error)


def test_selector_error_quotes_the_selector() -> None:
    error = SelectorError('td:nth-child(2)')
    assert error.selector == 'td:nth-child(2)'
    assert 'nth-child' in str(error)


@pytest.mark.parametrize(
    'kind', [FetchError, InputError, StatusError, DecodeError, PageError, SelectorError]
)
def test_every_error_derives_from_base(kind: type[Exception]) -> None:
    assert issubclass(kind, WikiError)
