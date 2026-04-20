from enum import StrEnum
from typing import Optional
from urllib.parse import unquote

from wiki_fetch.base.extract.registry import extract
from wiki_fetch.base.html.fetch import Network, Transport
from wiki_fetch.base.render import dict as dictionary
from wiki_fetch.base.render import json as jsonize
from wiki_fetch.base.render import text as textize
from wiki_fetch.base.render import toml as tomlize
from wiki_fetch.core.config import Search, Site
from wiki_fetch.core.errors import InputError
from wiki_fetch.core.languages import resolve as language
from wiki_fetch.core.models import Output
from wiki_fetch.core.page import resolve
from wiki_fetch.generic import messages, parts, site, types


def choose[Choice: StrEnum](
    kind: type[Choice], value: str | Choice, message: messages.Message
) -> Choice:
    try:
        return kind(value)
    except ValueError as failure:
        raise InputError(message.format(value=value)) from failure


class Wiki:
    def __init__(self, lang: str = site.DEFAULT, *, transport: Optional[Transport] = None) -> None:
        self.site = Site(language=language(lang))
        self.transport: Transport = Network() if transport is None else transport

    def search(
        self,
        query: Optional[str] = None,
        url: Optional[str] = None,
        part: str | parts.Part = parts.Part.all,
        item: str | parts.Selection = parts.Selection.all,
    ) -> Output:
        return self.read(
            Search(
                query=query,
                url=url,
                part=choose(parts.Part, part, messages.Message.part),
                item=choose(parts.Selection, item, messages.Message.selection),
            )
        )

    def read(self, request: Search) -> Output:
        page = resolve(self.target(request), self.site, self.transport)
        found = extract(request.part, page.root)
        data: types.Payload = {
            piece.label: dictionary.build(piece.blocks, request.item) for piece in found
        }
        data[site.ADDRESS] = unquote(page.url)
        return Output(
            dict=data,
            json=jsonize.build(data),
            text=textize.build(data),
            toml=tomlize.build(data),
        )

    def target(self, request: Search) -> str:
        if request.url:
            return request.url
        if request.query:
            return self.site.query(request.query)
        raise InputError(messages.Message.input)
