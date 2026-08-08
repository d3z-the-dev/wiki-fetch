import gzip
import zlib

import pytest

from tests.unit.conftest import Director
from wiki_fetch.base.errors import DecodeError, FetchError, StatusError
from wiki_fetch.base.html.fetch import Network, Policy, encode

URL = 'https://en.wikipedia.org/wiki/A'
PATIENT = Policy(attempts=3)


def quiet(_: float) -> None:
    return None


def test_encode_percent_encodes_non_ascii_paths() -> None:
    encoded = encode('https://ru.wikipedia.org/wiki/Меркурий')
    assert encoded.endswith('/wiki/%D0%9C%D0%B5%D1%80%D0%BA%D1%83%D1%80%D0%B8%D0%B9')


def test_encode_is_idempotent() -> None:
    once = encode('https://en.wikipedia.org/wiki/The_Doors_(band)')
    assert once == 'https://en.wikipedia.org/wiki/The_Doors_(band)'
    assert encode(once) == once


def test_encode_keeps_existing_escapes() -> None:
    assert encode('https://en.wikipedia.org/?search=The%20Doors') == (
        'https://en.wikipedia.org/?search=The%20Doors'
    )


def test_encode_applies_idna_to_the_host() -> None:
    assert encode('https://пример.рф/wiki/A').startswith('https://xn--e1afmkfd.xn--p1ai/')


def test_encode_rejects_a_file_scheme() -> None:
    with pytest.raises(FetchError):
        encode('file:///etc/passwd')


def test_encode_rejects_an_unknown_scheme() -> None:
    with pytest.raises(FetchError):
        encode('ftp://example.com/x')


def test_encode_names_the_offending_scheme_in_the_message() -> None:
    with pytest.raises(FetchError) as failure:
        encode('ftp://example.com/x')
    assert 'ftp' in str(failure.value)


def test_plain_body_is_returned(director: Director) -> None:
    director.answer(body=b'<p>ok</p>')
    assert Network(director=director).fetch(URL).text == '<p>ok</p>'


def test_gzip_body_is_decompressed(director: Director) -> None:
    director.answer(body=gzip.compress(b'<p>ok</p>'), headers={'Content-Encoding': 'gzip'})
    assert Network(director=director).fetch(URL).text == '<p>ok</p>'


def test_deflate_body_is_decompressed(director: Director) -> None:
    director.answer(body=zlib.compress(b'<p>ok</p>'), headers={'Content-Encoding': 'deflate'})
    assert Network(director=director).fetch(URL).text == '<p>ok</p>'


def test_charset_comes_from_the_header(director: Director) -> None:
    director.answer(
        body='<p>Ток</p>'.encode('cp1251'),
        headers={'Content-Type': 'text/html; charset=cp1251'},
    )
    assert 'Ток' in Network(director=director).fetch(URL).text


def test_charset_falls_back_to_the_meta_tag(director: Director) -> None:
    director.answer(body="<meta charset='cp1251'><p>Ток</p>".encode('cp1251'))
    assert 'Ток' in Network(director=director).fetch(URL).text


def test_charset_falls_back_to_utf8(director: Director) -> None:
    director.answer(body='<p>Ток</p>'.encode())
    assert 'Ток' in Network(director=director).fetch(URL).text


def test_fetch_reports_the_url_the_response_actually_came_from(director: Director) -> None:
    director.answer(body=b'<p>ok</p>')
    assert Network(director=director).fetch(URL).url == URL


def test_retries_on_429_then_succeeds(director: Director) -> None:
    director.answer(status=429, headers={'Retry-After': '0'})
    director.answer(body=b'<p>ok</p>')
    network = Network(director=director, policy=PATIENT, sleep=quiet)
    assert network.fetch(URL).text == '<p>ok</p>'
    assert director.calls == 2


def test_retries_on_503_then_gives_up(director: Director) -> None:
    for _ in range(3):
        director.answer(status=503)
    network = Network(director=director, policy=PATIENT, sleep=quiet)
    with pytest.raises(StatusError) as failure:
        network.fetch(URL)
    assert failure.value.status == 503
    assert director.calls == 3


def test_client_errors_are_not_retried(director: Director) -> None:
    director.answer(status=404)
    network = Network(director=director, policy=PATIENT, sleep=quiet)
    with pytest.raises(StatusError):
        network.fetch(URL)
    assert director.calls == 1


def test_exhausted_redirects_are_reported_as_such(director: Director) -> None:
    director.answer(status=302)
    with pytest.raises(FetchError) as failure:
        Network(director=director, sleep=quiet).fetch(URL)
    assert 'redirect' in str(failure.value).lower()


def test_undecodable_body_raises_decode_error(director: Director) -> None:
    director.answer(body=b'\xff\xfe\x00', headers={'Content-Type': 'text/html; charset=ascii'})
    with pytest.raises(DecodeError):
        Network(director=director).fetch(URL)


def test_retry_after_header_drives_the_pause() -> None:
    assert Network().pause(attempt=1, retry='7') == 7.0
    assert Network(policy=Policy(backoff=0.5)).pause(attempt=3, retry=None) == 2.0
