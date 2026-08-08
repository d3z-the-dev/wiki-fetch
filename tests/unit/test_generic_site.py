from wiki_fetch.generic.site import ADDRESS, DEFAULT, HOST, SEARCH


def test_the_host_template_takes_a_language() -> None:
    assert HOST.format(language='ru') == 'https://ru.wikipedia.org/'


def test_the_search_template_takes_a_query() -> None:
    assert SEARCH.format(query='cats') == '?search=cats'


def test_the_default_language_is_english() -> None:
    assert DEFAULT == 'English'


def test_the_url_key_is_named() -> None:
    assert ADDRESS == 'URL'
