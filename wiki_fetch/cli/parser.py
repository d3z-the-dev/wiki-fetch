import argparse
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional

from wiki_fetch.generic import console, parts, site


@dataclass(frozen=True, slots=True)
class Options:
    url: Optional[str] = None
    query: Optional[str] = None
    lang: str = site.DEFAULT
    part: parts.Part = parts.Part.all
    item: parts.Selection = parts.Selection.all
    output: parts.Format = parts.Format.text


def values(kind: type[StrEnum]) -> list[str]:
    return [member.value for member in kind]


def build() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=console.PROGRAM, description=console.SUMMARY)
    parser.add_argument(console.Flag.url.short, console.Flag.url.long, help=console.Help.url)
    parser.add_argument(console.Flag.query.short, console.Flag.query.long, help=console.Help.query)
    parser.add_argument(
        console.Flag.lang.short,
        console.Flag.lang.long,
        default=site.DEFAULT,
        help=console.Help.lang,
    )
    parser.add_argument(
        console.Flag.part.short,
        console.Flag.part.long,
        default=parts.Part.all,
        choices=values(parts.Part),
        help=console.Help.part,
    )
    parser.add_argument(
        console.Flag.item.short,
        console.Flag.item.long,
        default=parts.Selection.all,
        choices=values(parts.Selection),
        help=console.Help.item,
    )
    parser.add_argument(
        console.Flag.output.short,
        console.Flag.output.long,
        default=parts.Format.text,
        choices=values(parts.Format),
        help=console.Help.output,
    )
    return parser


def read(argv: Optional[Sequence[str]] = None) -> Options:
    parsed = build().parse_args(argv)
    return Options(
        url=parsed.url,
        query=parsed.query,
        lang=parsed.lang,
        part=parts.Part(parsed.part),
        item=parts.Selection(parsed.item),
        output=parts.Format(parsed.output),
    )
