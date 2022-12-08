# wiki-fetch

<p>
  <a href="https://github.com/d3z-the-dev/wiki-fetch/releases/">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/wiki-fetch" />
  </a>
  <a href="https://github.com/d3z-the-dev/wiki-fetch/releases/">
    <img alt="PyPI Downloads" src="https://img.shields.io/pypi/dm/wiki-fetch" />
  </a>
  <a href="https://github.com/d3z-the-dev/wiki-fetch/releases/">
    <img alt="Python Version" src="https://img.shields.io/pypi/pyversions/wiki-fetch" />
  </a>
  <a href="https://github.com/d3z-the-dev/wiki-fetch/releases/">
    <img alt="License" src="https://img.shields.io/pypi/l/wiki-fetch" />
  </a>
  <a href="https://github.com/d3z-the-dev/wiki-fetch/releases/">
    <img alt="Issues" src="https://img.shields.io/bitbucket/issues/d3z-the-dev/wiki-fetch" />
  </a>
</p>

## Installation

- PyPI

```bash
pip install wiki-fetch
```

- Source

```bash
git clone git@github.com:d3z-the-dev/wiki-fetch.git
cd wiki-fetch && poetry build
pip install ./dist/*.whl
```

## Usage

### CLI

| Option           | Flag | Long      | Default | Example                                   |
| ---------------- | ---- | --------- | ------- | ----------------------------------------- |
| Wiki's page link | `-u` | `--url`   | None    | <https://en.wikipedia.org/wiki/The_Doors> |
| Search query     | `-q` | `--query` | None    | The Doors (band)                          |
| Page language    | `-l` | `--lang`  | English | English                                   |
| Part of the page | `-p` | `--part`  | all     | infobox                                   |
| Parts by order   | `-i` | `--item`  | all     | first                                     |

```bash
wiki-fetch -q 'The Doors (band)' -p infobox -i first
```

<details>
<summary>output</summary>

```text
Infobox:
    The Doors:
        The Doors:
            Image 1: https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/The_Doors_1968.JPG/250px-The_Doors_1968.JPG
            Image title: The Doors in 1966: Morrison (left), Densmore (centre), Krieger (right) and Manzarek (seated)
        Background information:
            Origin: Los Angeles, California, U.S.
            Genres:
                Psychedelic Rock
                Blues Rock
                Acid Rock
            Years active:
                1965-1973
                1978
            Labels: Elektra, Rhino
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
```


</details>

### Python

| Argument | Values                                                         | Description                         |
| -------- | -------------------------------------------------------------- | ----------------------------------- |
| url      | `str`                                                          | Any Wiki's page URL                 |
| query    | `str`                                                          | Any query string                    |
| lang     | `English`                                                      | Currently only English is available |
| part     | `infobox`, `paragraph`, `table`, `list`, `thumb`, `toc`, `all` | Specify page part                   |
| item     | `first`, `last`, `all`                                         | Specify the order of the part       |

```python
from wiki_fetch.driver import Wiki

output = Wiki().search(query='The Doors (band)', part='infobox', item='first')
print(output.json)
```

<details>
<summary>output</summary>

```json
{
    "Infobox": {
        "The Doors": {
            "The Doors": {
                "Image 1": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/The_Doors_1968.JPG/250px-The_Doors_1968.JPG",
                "Image title": "The Doors in 1966: Morrison (left), Densmore (centre), Krieger (right) and Manzarek (seated)"
            },
            "Background information": {
                "Origin": "Los Angeles, California, U.S.",
                "Genres": [
                    "Psychedelic Rock",
                    "Blues Rock",
                    "Acid Rock"
                ],
                "Years active": [
                    "1965-1973",
                    "1978"
                ],
                "Labels": "Elektra, Rhino",
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
                "Website": "thedoors.com"
            }
        }
    }
}
```
</details>
