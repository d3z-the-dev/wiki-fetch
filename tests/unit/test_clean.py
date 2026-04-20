from wiki_fetch.base.extract.clean import address, label, sentence, strip
from wiki_fetch.base.html.query import find_all, text
from wiki_fetch.base.html.tokenizer import parse


def test_strip_removes_noise_once() -> None:
    root = parse(
        "<div><span class='mw-editsection'>[edit]</span>"
        "<sup class='reference'>[1]</sup><span style='display:none'>hidden</span>"
        '<p>Real text</p></div>'
    ).root
    strip(root)
    assert text(root) == 'Real text'
    assert find_all(root, 'sup') == ()


def test_strip_keeps_ordinary_content() -> None:
    root = parse("<div><p>Kept</p><table class='navbox'>gone</table></div>").root
    strip(root)
    assert text(root) == 'Kept'


def test_sentence_normalises_and_label_drops_colon() -> None:
    root = parse('<th>Years active&nbsp;:</th>').root
    assert sentence(root) == 'Years active :'
    assert label(root) == 'Years active'


def test_label_drops_a_tight_colon() -> None:
    assert label(parse('<th>Origin:</th>').root) == 'Origin'


def test_address_completes_a_protocol_relative_link() -> None:
    assert address('//upload.example/x.jpg') == 'https://upload.example/x.jpg'
    assert address('https://upload.example/x.jpg') == 'https://upload.example/x.jpg'


def test_address_drops_wikipedia_tracking_parameters() -> None:
    tracked = (
        '//upload.example/x.jpg?utm_source=en.wikipedia.org'
        '&utm_campaign=parser&utm_content=thumbnail'
    )
    assert address(tracked) == 'https://upload.example/x.jpg'


def test_address_keeps_parameters_that_are_not_tracking() -> None:
    assert address('https://upload.example/x.jpg?page=2') == 'https://upload.example/x.jpg?page=2'
    assert (
        address('https://upload.example/x.jpg?page=2&utm_source=en.wikipedia.org')
        == 'https://upload.example/x.jpg?page=2'
    )
