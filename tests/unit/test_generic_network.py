from wiki_fetch.generic.network import (
    ATTEMPTS,
    BACKOFF,
    HEADERS,
    HOPS,
    PREFIX,
    REDIRECTS,
    THROTTLED,
    TIMEOUT,
    UNAVAILABLE,
    Header,
)


def test_the_policy_came_from_the_configuration() -> None:
    assert TIMEOUT == 10.0
    assert HOPS == 5
    assert ATTEMPTS == 3
    assert BACKOFF == 0.5
    assert PREFIX == 4096


def test_header_names_stay_protocol_facts_in_code() -> None:
    assert Header.agent.value == 'User-Agent'
    assert Header.retry_after.value == 'Retry-After'


def test_the_request_headers_are_assembled_from_both() -> None:
    assert HEADERS[Header.agent].startswith('wiki-fetch/')
    assert HEADERS[Header.accept_encoding] == 'gzip, deflate'


def test_http_status_codes_stay_in_code() -> None:
    assert THROTTLED == 429
    assert 503 in UNAVAILABLE
    assert 301 in REDIRECTS
