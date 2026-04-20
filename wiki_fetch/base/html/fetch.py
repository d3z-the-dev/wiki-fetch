import gzip
import time
import urllib.request
import zlib
from collections.abc import Callable
from dataclasses import dataclass
from typing import Optional, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit, urlunsplit

from wiki_fetch.base.errors import DecodeError, FetchError, StatusError
from wiki_fetch.generic import messages, network, text


@dataclass(frozen=True, slots=True)
class Policy:
    timeout: float = network.TIMEOUT
    redirects: int = network.HOPS
    attempts: int = network.ATTEMPTS
    backoff: float = network.BACKOFF


class Headers(Protocol):
    def get(self, name: str) -> Optional[str]: ...


class Reply(Protocol):
    @property
    def url(self) -> str: ...

    @property
    def headers(self) -> Headers: ...

    def read(self) -> bytes: ...

    def close(self) -> None: ...


class Director(Protocol):
    def open(
        self, fullurl: urllib.request.Request, data: None = ..., timeout: float = ...
    ) -> Reply: ...


@dataclass(frozen=True, slots=True)
class Answer:
    url: str
    text: str


class Transport(Protocol):
    def fetch(self, url: str) -> Answer: ...


def encode(url: str) -> str:
    parts = urlsplit(url)
    if parts.scheme not in network.SCHEMES:
        raise FetchError(messages.Message.scheme.format(value=parts.scheme or url))
    host = (
        parts.netloc
        if parts.netloc.isascii()
        else parts.netloc.encode(text.Encoding.idna).decode(text.Encoding.ascii)
    )
    return urlunsplit(
        (
            parts.scheme,
            host,
            quote(parts.path, safe=network.PATH),
            quote(parts.query, safe=network.QUERY),
            quote(parts.fragment, safe=network.PATH),
        )
    )


class Bounded(urllib.request.HTTPRedirectHandler):
    def __init__(self, redirects: int) -> None:
        self.max_redirections = redirects


def connect(policy: Policy) -> Director:
    return urllib.request.build_opener(Bounded(policy.redirects))


def unpack(payload: bytes, encoding: Optional[str]) -> bytes:
    if encoding == text.Encoding.gzip:
        return gzip.decompress(payload)
    if encoding != text.Encoding.deflate:
        return payload
    try:
        return zlib.decompress(payload)
    except zlib.error:
        return zlib.decompress(payload, -zlib.MAX_WBITS)


def charset(payload: bytes, header: Optional[str]) -> str:
    declared = (
        None
        if header is None
        else text.CHARSET.search(header.encode(text.Encoding.ascii, text.LENIENT))
    )
    embedded = text.CHARSET.search(payload[: network.PREFIX])
    found = declared or embedded
    if found is None:
        return text.Encoding.fallback.value
    return found[text.Capture.charset].decode(text.Encoding.ascii)


@dataclass(frozen=True, slots=True)
class Network:
    policy: Policy = Policy()
    director: Optional[Director] = None
    sleep: Callable[[float], None] = time.sleep

    def fetch(self, url: str) -> Answer:
        target = encode(url)
        request = urllib.request.Request(target, headers=dict(network.HEADERS))
        director = self.director or connect(self.policy)
        attempt = 1
        while True:
            try:
                reply = director.open(request, timeout=self.policy.timeout)
            except HTTPError as failure:
                self.escalate(failure, target, attempt)
                self.sleep(self.pause(attempt, failure.headers.get(network.Header.retry_after)))
                attempt += 1
            except URLError as failure:
                raise FetchError(
                    messages.Message.network.format(url=target, reason=failure.reason)
                ) from failure
            else:
                return Answer(url=reply.url, text=self.read(reply, target))

    def escalate(self, failure: HTTPError, target: str, attempt: int) -> None:
        if failure.code in network.REDIRECTS:
            raise FetchError(messages.Message.redirect.format(url=target)) from failure
        retriable = failure.code == network.THROTTLED or failure.code in network.UNAVAILABLE
        if not retriable or attempt >= self.policy.attempts:
            raise StatusError(status=failure.code, url=target) from failure

    def pause(self, attempt: int, retry: Optional[str]) -> float:
        if retry is not None and retry.strip().isdigit():
            return float(retry.strip())
        return self.policy.backoff * float(network.GROWTH ** (attempt - 1))

    def read(self, reply: Reply, target: str) -> str:
        try:
            payload = unpack(reply.read(), reply.headers.get(network.Header.content_encoding))
            declared = reply.headers.get(network.Header.content_type)
        finally:
            reply.close()
        try:
            return payload.decode(charset(payload, declared))
        except (UnicodeDecodeError, LookupError) as failure:
            raise DecodeError(target) from failure
