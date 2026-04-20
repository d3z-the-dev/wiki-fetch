import sys
from collections.abc import Sequence
from typing import Optional, assert_never

from wiki_fetch.base.errors import WikiError
from wiki_fetch.base.html.fetch import Transport
from wiki_fetch.cli.parser import read
from wiki_fetch.core.client import Wiki
from wiki_fetch.core.errors import InputError
from wiki_fetch.core.models import Output
from wiki_fetch.generic import console, parts, types


def shown(output: Output, form: parts.Format) -> str | types.Payload:
    match form:
        case parts.Format.dict:
            return output.dict
        case parts.Format.json:
            return output.json
        case parts.Format.text:
            return output.text
        case parts.Format.toml:
            return output.toml
        case _:
            assert_never(form)


def run(
    argv: Optional[Sequence[str]] = None, transport: Optional[Transport] = None
) -> console.Code:
    options = read(argv)
    try:
        output = Wiki(options.lang, transport=transport).search(
            query=options.query, url=options.url, part=options.part, item=options.item
        )
    except InputError as failure:
        print(failure, file=sys.stderr)
        return console.Code.misuse
    except WikiError as failure:
        print(failure, file=sys.stderr)
        return console.Code.failure
    print(shown(output, options.output))
    return console.Code.done
