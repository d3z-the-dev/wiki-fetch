# wiki-fetch

[![PyPI](https://img.shields.io/pypi/v/wiki-fetch)](https://github.com/d3z-the-dev/wiki-fetch/releases/)
[![Status](https://img.shields.io/pypi/status/wiki-fetch)](https://pypi.org/project/wiki-fetch/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/wiki-fetch)](https://pypi.org/project/wiki-fetch/)
[![Python Version](https://img.shields.io/pypi/pyversions/wiki-fetch?color=%23244E71)](https://pypi.org/project/wiki-fetch/)
[![License](https://img.shields.io/pypi/l/wiki-fetch?color=272727)](https://en.wikipedia.org/wiki/Apache_License#Apache_License_2.0)
[![Issues](https://img.shields.io/github/issues/d3z-the-dev/wiki-fetch)](https://github.com/d3z-the-dev/wiki-fetch/issues)

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

<table>
<tr><th>Options for use in console</th></tr>
<tr><td>

| Option           | Flag | Long       | Default | Example                                   |
| ---------------- | ---- | ---------- | ------- | ----------------------------------------- |
| Wiki's page link | `-u` | `--url`    | None    | <https://en.wikipedia.org/wiki/The_Doors> |
| Search query     | `-q` | `--query`  | None    | The Doors (band)                          |
| Page language    | `-l` | `--lang`   | English | English                                   |
| Part of the page | `-p` | `--part`   | all     | infobox                                   |
| Parts by order   | `-i` | `--item`   | all     | first                                     |
| Output format    | `-o` | `--output` | text    | text                                      |
    
</td></tr>
</table>

```bash
wiki-fetch -q 'The Doors (band)' -p infobox -i first
```

<details>
<summary>output</summary>

```yaml
Infobox: 
    The Doors: 
        The Doors: 
            Image: https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/The_Doors_1968.JPG/250px-The_Doors_1968.JPG
            Caption: The Doors in 1966: Morrison (left), Densmore (centre), Krieger (right) and Manzarek (seated)
        Background information: 
            Origin: Los Angeles, California, U.S.
            Genres: 
                Psychedelic Rock
                Blues Rock
                Acid Rock
            Years active: 
                1965-1973
                1978
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
URL: https://en.wikipedia.org/?search=The Doors (Band)
```
</details>

### Python

<table>
<tr><th>Arguments of function and class</th></tr>
<tr><td>
    
| Argument | Values                                                         | Description                     |
| -------- | -------------------------------------------------------------- | ------------------------------- |
| url      | `str`                                                          | Any Wiki's page URL             |
| query    | `str`                                                          | Any query string                |
| lang     | `str`                                                          | Any of available languages      |
| part     | `infobox`, `paragraph`, `table`, `list`, `thumb`, `toc`, `all` | Specify page part               |
| item     | `first`, `last`, `all`                                         | Specify the order of the part   |

</td></tr>
</table>

```python
from wiki_fetch.driver import Wiki

output = Wiki(lang='English').search(query='The Doors (band)', part='infobox', item='first')
print(output.json)
```

<details>
<summary>output</summary>

```json
{
    "Infobox": [
        {
            "The Doors": {
                "The Doors": {
                    "Image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/The_Doors_1968.JPG/250px-The_Doors_1968.JPG",
                    "Caption": "The Doors in 1966: Morrison (left), Densmore (centre), Krieger (right) and Manzarek (seated)"
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
                    "Website": "thedoors.com"
                }
            }
        }
    ],
    "URL": "https://en.wikipedia.org/?search=The Doors (Band)"
}
```
</details>

## Specification
    
<table>
<tr><th>Available options</th></tr>
<tr><td>

| Parts of page | Output formats | Language       |
| ------------- | -------------- | -------------- |
| `infobox`     | `text`         | `English`      |
| `paragraph`   | `json`         | `Ukrainian`    |
| `table`       | `dict`         | `Russian`      |
| `list`        |                | `Polish`       |
| `thumb`       |                | `German`       |
| `toc`         |                | `Nederlands`   |
|               |                | `Swedish`      |
|               |                | `Spanish`      |
|               |                | `French`       |
|               |                | `Italian`      |
|               |                | `Japanese`     |
|               |                | `Chainese`     |
|               |                | `Cebuano`      |

</td></tr>
</table>
