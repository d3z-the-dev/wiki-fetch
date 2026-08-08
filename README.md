<div align="center">

# wiki-fetch

[![CI](https://img.shields.io/github/actions/workflow/status/d3z-the-dev/wiki-fetch/ci.yml?branch=master&label=CI)](https://github.com/d3z-the-dev/wiki-fetch/actions/workflows/ci.yml)
[![Live](https://img.shields.io/github/actions/workflow/status/d3z-the-dev/wiki-fetch/live.yml?branch=master&label=live)](https://github.com/d3z-the-dev/wiki-fetch/actions/workflows/live.yml)
[![PyPI](https://img.shields.io/pypi/v/wiki-fetch)](https://pypi.org/project/wiki-fetch/)
[![Status](https://img.shields.io/pypi/status/wiki-fetch)](https://pypi.org/project/wiki-fetch/)
[![Downloads](https://img.shields.io/pepy/dt/wiki-fetch)](https://pepy.tech/project/wiki-fetch)
[![Python](https://img.shields.io/badge/python-3.12%20--%203.14-244E71)](https://pypi.org/project/wiki-fetch/)

**Wikipedia parser for Python and the CLI. Dependency-free.**

_own HTTP client, own HTML parser_

</div>

## Installation

```bash
uv add wiki-fetch
```

```bash
pip install wiki-fetch
```

## Usage

### CLI

| Option           | Flag | Long       | Default | Example                                   |
| ---------------- | ---- | ---------- | ------- | ----------------------------------------- |
| Article URL      | `-u` | `--url`    | None    | <https://en.wikipedia.org/wiki/The_Doors> |
| Search query     | `-q` | `--query`  | None    | The Doors (band)                          |
| Language edition | `-l` | `--lang`   | English | English                                   |
| Article part     | `-p` | `--part`   | all     | infobox                                   |
| Blocks to keep   | `-i` | `--item`   | all     | first                                     |
| Output format    | `-o` | `--output` | text    | text                                      |

Give `--url` or `--query`; `--url` wins if both are set. A query takes the first search
result. A disambiguation page comes back whole, its lists of links included.

```bash
wiki-fetch -u https://en.wikipedia.org/wiki/The_Doors -p infobox -i first
```

<details>
<summary>output</summary>

```yaml
Infobox: 
    The Doors: 
        The Doors: 
            Image: https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/The_Doors_1968.JPG/250px-The_Doors_1968.JPG
            Caption: The Doors in 1966. From left to right: Jim Morrison, John Densmore, Ray Manzarek and Robby Krieger
        Background information: 
            Origin: Los Angeles, California, U.S.
            Genres: 
                Psychedelic rock
                blues rock
                acid rock
            Years active: 
                1965-1973
                1978
                1993
                1997
                2000
                2011-2012
                2012-2013
                2025
            Labels: 
                Elektra
                Rhino
            Spinoffs: 
                The Psychedelic Rangers
                Butts Band
                Nite City
                Manzarek-Krieger
            Spinoff of: Rick & the Ravens
            Past members: 
                Jim Morrison
                Ray Manzarek
                Robby Krieger
                John Densmore
            Website: thedoors.com
            Image: https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/The_Doors_Logo.png/250px-The_Doors_Logo.png
URL: https://en.wikipedia.org/wiki/The_Doors
```
</details>

Exit codes: `0` printed a result, `1` fetch failed or the page holds no article, `2` bad input.

### Python

| Argument | Values                                                         | Description                    |
| -------- | -------------------------------------------------------------- | ------------------------------ |
| url      | `str`                                                          | Article URL                    |
| query    | `str`                                                          | Search query                   |
| lang     | `str`                                                          | Language name, endonym or code |
| part     | `infobox`, `paragraph`, `table`, `list`, `thumb`, `toc`, `all` | Article part                   |
| item     | `first`, `last`, `all`                                         | Blocks to keep                 |

```python
from wiki_fetch import Wiki

page = 'https://en.wikipedia.org/wiki/The_Doors'
output = Wiki(lang='English').search(url=page, part='infobox', item='first')
print(output.json)
```

`search` returns one object holding the result four ways: `output.dict`, `output.json`,
`output.text`, `output.toml`. `item="first"` and `item="last"` yield one dictionary per part,
`item="all"` a list of them.

<details>
<summary>output</summary>

```json
{
    "Infobox": {
        "The Doors": {
            "The Doors": {
                "Image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/The_Doors_1968.JPG/250px-The_Doors_1968.JPG",
                "Caption": "The Doors in 1966. From left to right: Jim Morrison, John Densmore, Ray Manzarek and Robby Krieger"
            },
            "Background information": {
                "Origin": "Los Angeles, California, U.S.",
                "Genres": [
                    "Psychedelic rock",
                    "blues rock",
                    "acid rock"
                ],
                "Years active": [
                    "1965-1973",
                    "1978",
                    "1993",
                    "1997",
                    "2000",
                    "2011-2012",
                    "2012-2013",
                    "2025"
                ],
                "Labels": [
                    "Elektra",
                    "Rhino"
                ],
                "Spinoffs": [
                    "The Psychedelic Rangers",
                    "Butts Band",
                    "Nite City",
                    "Manzarek-Krieger"
                ],
                "Spinoff of": "Rick & the Ravens",
                "Past members": [
                    "Jim Morrison",
                    "Ray Manzarek",
                    "Robby Krieger",
                    "John Densmore"
                ],
                "Website": "thedoors.com",
                "Image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/The_Doors_Logo.png/250px-The_Doors_Logo.png"
            }
        }
    },
    "URL": "https://en.wikipedia.org/wiki/The_Doors"
}
```
</details>

<details>
<summary>toml</summary>

```toml
URL = "https://en.wikipedia.org/wiki/The_Doors"

[Infobox."The Doors"."The Doors"]
Image = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/The_Doors_1968.JPG/250px-The_Doors_1968.JPG"
Caption = "The Doors in 1966. From left to right: Jim Morrison, John Densmore, Ray Manzarek and Robby Krieger"

[Infobox."The Doors"."Background information"]
Origin = "Los Angeles, California, U.S."
Genres = ["Psychedelic rock", "blues rock", "acid rock"]
"Years active" = ["1965-1973", "1978", "1993", "1997", "2000", "2011-2012", "2012-2013", "2025"]
Labels = ["Elektra", "Rhino"]
Spinoffs = ["The Psychedelic Rangers", "Butts Band", "Nite City", "Manzarek-Krieger"]
"Spinoff of" = "Rick & the Ravens"
"Past members" = ["Jim Morrison", "Ray Manzarek", "Robby Krieger", "John Densmore"]
Website = "thedoors.com"
Image = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/The_Doors_Logo.png/250px-The_Doors_Logo.png"
```
</details>

Every error descends from `WikiError`, so one `except WikiError` catches the lot.

| Error           | Raised when                              |
| --------------- | ---------------------------------------- |
| `InputError`    | an argument is rejected                  |
| `FetchError`    | the transport fails                      |
| `StatusError`   | Wikipedia answers 4xx or 5xx             |
| `DecodeError`   | the body does not decode                 |
| `PageError`     | the page holds no article                |
| `SelectorError` | the selector is outside the CSS subset   |

`StatusError` and `DecodeError` sit under `FetchError`.

## Specification

| Parts of page | Output formats |
| ------------- | -------------- |
| `infobox`     | `text`         |
| `paragraph`   | `json`         |
| `table`       | `dict`         |
| `list`        | `toml`         |
| `thumb`       |                |
| `toc`         |                |
| `all`         |                |

The parser normalises image addresses: protocol-relative links become `https`, Wikipedia's
`utm_*` tracking parameters go, every other parameter stays. `toml` writes bare keys where
TOML allows them and spells a missing value the way `text` does, as `null`.

### Languages

`--lang` takes an English name, an endonym or a code, ignoring case and surrounding space:
`German`, `Deutsch` and `de` are the same edition. Thirty editions are known by name, most by
endonym too. The rest answer to their subdomain code, ISO 639-1 where one exists and 639-3
otherwise, with an optional variant suffix: `fi`, `ceb`, `zh-yue`. Anything else raises
`InputError`.

### Selectors

`select` and `select_one` in `wiki_fetch.base.html.query` read this subset of CSS:

| Pattern          | Example                |
| ---------------- | ---------------------- |
| type             | `table`                |
| id               | `#content`             |
| class            | `.infobox`             |
| attribute        | `[colspan]`            |
| attribute value  | `[typeof="mw:File"]`   |
| attribute prefix | `[typeof^="mw:File"]`  |
| descendant       | `table .infobox-label` |
| child            | `div > figure`         |
| grouping         | `.noprint, .navbox`    |

Classes match by token, so `.box` finds `class="box wide"` and skips `class="boxed"`.
Anything outside the table raises `SelectorError`, pseudo-classes and sibling combinators
included.

## License

Apache 2.0. See [LICENSE.md](LICENSE.md).
