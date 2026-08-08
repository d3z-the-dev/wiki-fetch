from collections.abc import Mapping
from dataclasses import dataclass, field

from wiki_fetch.base.html.fetch import Answer

SHELL = (
    '<html><body><div id="content"><div id="mw-content-text">'
    '<div class="mw-parser-output">{body}</div></div></div></body></html>'
)
INFOBOX = (
    '<table class="infobox"><caption>{title}</caption>'
    '<tr><th class="infobox-label">Origin</th><td>Los Angeles</td></tr>'
    '<tr><td><img src="//upload.example/x.jpg"/></td></tr></table>'
)
PROSE = (
    '<div class="mw-heading"><h2>History</h2></div>'
    '<p>The band formed in 1965.<sup class="reference">[1]</sup></p>'
    '<ul><li>First member</li><li>Second member</li></ul>'
)
FIGURE = (
    '<figure typeof="mw:File/Thumb">'
    '<a class="mw-file-description" href="/wiki/File:Stage_shot.jpg"></a>'
    '<img src="//upload.example/stage.jpg"/><figcaption>On stage</figcaption></figure>'
)
EDIT = '<span class="mw-editsection">edit</span>'


def article(title: str = 'The Doors') -> str:
    return SHELL.format(body=INFOBOX.format(title=title) + PROSE + FIGURE + EDIT)


SEARCH_PAGE = SHELL.format(
    body='<div class="mw-search-results">'
    '<div class="mw-search-result-heading">'
    '<a href="/wiki/The_Doors">The Doors</a></div></div>'
)
DISAMBIG_PAGE = SHELL.format(
    body='<div id="disambigbox"></div><ul><li><a href="/wiki/Category:Planets">Category</a></li>'
    '<li><a href="/wiki/Mercury_(planet)">Mercury</a></li></ul>'
)
EMPTY_PAGE = '<html><body>nothing</body></html>'


@dataclass(slots=True)
class Recorder:
    pages: Mapping[str, str]
    redirects: Mapping[str, str] = field(default_factory=dict)
    calls: list[str] = field(default_factory=list)

    def fetch(self, url: str) -> Answer:
        self.calls.append(url)
        if url not in self.pages:
            raise AssertionError(f'unexpected request to {url}')
        return Answer(url=self.redirects.get(url, url), text=self.pages[url])
