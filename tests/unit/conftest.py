import urllib.request
from dataclasses import dataclass, field
from email.message import Message
from typing import Optional
from urllib.error import HTTPError

import pytest


@dataclass(slots=True)
class Answer:
    body: bytes = bytes()
    status: int = 200
    headers: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class Reply:
    url: str
    body: bytes
    headers: dict[str, str]
    closed: bool = False

    def read(self) -> bytes:
        return self.body

    def close(self) -> None:
        self.closed = True


@dataclass(slots=True)
class Director:
    queue: list[Answer] = field(default_factory=list)
    calls: int = 0

    def answer(
        self, *, body: bytes = bytes(), status: int = 200, headers: Optional[dict[str, str]] = None
    ) -> None:
        self.queue.append(Answer(body=body, status=status, headers=headers or dict()))

    def open(
        self,
        fullurl: urllib.request.Request,
        data: None = None,
        timeout: float = 0.0,
    ) -> Reply:
        self.calls += 1
        answer = self.queue.pop(0)
        if answer.status >= 300:
            headers = Message()
            for name, value in answer.headers.items():
                headers[name] = value
            raise HTTPError(fullurl.full_url, answer.status, 'error', headers, None)
        return Reply(url=fullurl.full_url, body=answer.body, headers=answer.headers)


@pytest.fixture
def director() -> Director:
    return Director()
