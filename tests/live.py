import os
from functools import cache
from pathlib import Path

from tests.pages import Expectation
from wiki_fetch import Output, Wiki

GOLDEN = Path(__file__).parent / 'golden'
REWRITE = os.environ.get('WIKI_FETCH_GOLDEN') == 'write'


@cache
def fetched(page: Expectation) -> Output:
    return Wiki(page.language).search(url=page.url)


def recorded(page: Expectation, produced: str) -> str:
    path = GOLDEN / f'{page.name}.json'
    if REWRITE:
        path.parent.mkdir(exist_ok=True)
        path.write_text(produced, encoding='utf-8')
    return path.read_text(encoding='utf-8')
