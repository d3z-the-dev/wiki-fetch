from collections.abc import Mapping
from enum import StrEnum
from http import HTTPStatus
from typing import Any, Final

from wiki_fetch.utils.settings import Group, settings


class Scheme(StrEnum):
    secure = 'https'
    plain = 'http'


class Header(StrEnum):
    agent = 'User-Agent'
    accept = 'Accept'
    accept_encoding = 'Accept-Encoding'
    content_encoding = 'Content-Encoding'
    content_type = 'Content-Type'
    retry_after = 'Retry-After'


CONFIG: Any = settings.load(Group.network)
TIMEOUT: Final[float] = CONFIG.policy.timeout
HOPS: Final[int] = CONFIG.policy.hops
ATTEMPTS: Final[int] = CONFIG.policy.attempts
BACKOFF: Final[float] = CONFIG.policy.backoff
PREFIX: Final[int] = CONFIG.limits.prefix
AGENT: Final[str] = CONFIG.client.agent
HEADERS: Final[Mapping[str, str]] = {
    Header.agent: AGENT,
    Header.accept_encoding: CONFIG.client.encodings,
    Header.accept: CONFIG.client.accept,
}

PATH: Final = "/%:@()!$&'*+,;=~"
QUERY: Final = "%=&/:@()!$'*+,;~"
SCHEMES: Final[frozenset[str]] = frozenset(Scheme)
REDIRECTS: Final[frozenset[int]] = frozenset(
    {
        HTTPStatus.MOVED_PERMANENTLY,
        HTTPStatus.FOUND,
        HTTPStatus.SEE_OTHER,
        HTTPStatus.TEMPORARY_REDIRECT,
        HTTPStatus.PERMANENT_REDIRECT,
    }
)
THROTTLED: Final = HTTPStatus.TOO_MANY_REQUESTS
CEILING: Final = 600
UNAVAILABLE: Final = range(HTTPStatus.INTERNAL_SERVER_ERROR, CEILING)
GROWTH: Final = 2
