from wiki_fetch.core.config import Search, Site
from wiki_fetch.generic import parts


def test_base_is_the_language_edition_root() -> None:
    assert Site().base == 'https://en.wikipedia.org/'
    assert Site(language='ru').base == 'https://ru.wikipedia.org/'


def test_query_percent_encodes_everything_unsafe() -> None:
    assert Site(language='ru').query('The Doors (band)') == (
        'https://ru.wikipedia.org/?search=The%20Doors%20%28band%29'
    )


def test_query_keeps_the_words_as_entered() -> None:
    assert Site().query('the doors').endswith('?search=the%20doors')


def test_join_never_doubles_the_slash() -> None:
    site = Site(language='ru')
    assert site.join('/wiki/Дорз') == 'https://ru.wikipedia.org/wiki/Дорз'
    assert site.join('wiki/Дорз') == 'https://ru.wikipedia.org/wiki/Дорз'


def test_join_leaves_absolute_links_alone() -> None:
    assert Site().join('https://ja.wikipedia.org/wiki/X') == 'https://ja.wikipedia.org/wiki/X'


def test_search_defaults_to_everything() -> None:
    request = Search()
    assert (request.query, request.url) == (None, None)
    assert (request.part, request.item) == (parts.Part.all, parts.Selection.all)
