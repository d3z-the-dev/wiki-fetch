from wiki_fetch.base.extract.parts import Thumb
from wiki_fetch.base.html.tokenizer import parse

FIGURE = parse(
    "<div><figure typeof='mw:File/Thumb'>"
    "<a class='mw-file-description' href='/wiki/File:Whisky_a_Go-Go.jpg'>"
    "<img src='//upload/whisky.jpg'></a>"
    '<figcaption>Whisky a Go Go</figcaption></figure></div>'
).root


def test_thumb_reads_name_link_and_caption() -> None:
    table = Thumb.read(FIGURE)[0]
    assert table.label == 'Whisky a Go-Go'
    assert table.rows[0].label == 'Whisky a Go Go'
    assert table.rows[0].cells[0].data == 'https://upload/whisky.jpg'


def test_absolute_links_are_left_alone() -> None:
    absolute = parse("<figure typeof='mw:File'><img src='https://upload/logo.png'></figure>").root
    assert Thumb.read(absolute)[0].rows[0].cells[0].data == 'https://upload/logo.png'


def test_missing_caption_falls_back() -> None:
    bare = parse("<figure typeof='mw:File'><img src='//upload/logo.png'></figure>").root
    assert Thumb.read(bare)[0].rows[0].label == 'No caption'


def test_namespace_prefix_and_extension_are_dropped() -> None:
    localised = parse(
        "<figure typeof='mw:File'>"
        "<a class='mw-file-description' href='https://ja.wikipedia.org/wiki/"
        "%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB:The_doors_logo_2.png'>"
        "<img src='//upload/logo.png'></a></figure>"
    ).root
    assert Thumb.read(localised)[0].label == 'The doors logo 2'


def test_figures_without_an_image_are_skipped() -> None:
    empty = parse("<figure typeof='mw:File'><figcaption>nothing</figcaption></figure>").root
    assert Thumb.read(empty) == ()
