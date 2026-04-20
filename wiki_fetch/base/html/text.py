import unicodedata

from wiki_fetch.generic import text as generic


def collapse(source: str) -> str:
    return generic.SPACES.sub(generic.SPACE, source).strip()


def normalize(source: str) -> str:
    folded = unicodedata.normalize(generic.Encoding.form.value, source)
    return collapse(generic.FOOTNOTE.sub('', folded).translate(generic.FOLD))
