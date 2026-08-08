import pytest

from wiki_fetch.base.errors import SelectorError
from wiki_fetch.base.html.query import compile_selector, select, select_one, text
from wiki_fetch.base.html.tokenizer import parse

PAGE = parse(
    "<div id='content'>"
    "<figure typeof='mw:File/Thumb'><figcaption>Whisky</figcaption></figure>"
    "<table class='infobox vcard'><caption class='infobox-title'>The Doors</caption>"
    "<tr><th class='infobox-label'>Origin</th><td class='infobox-data'>LA</td></tr></table>"
    '</div>'
).root


def test_type_id_and_class() -> None:
    found = select_one(PAGE, '#content')
    assert found is not None
    assert found.attrs['id'] == 'content'
    assert text(select_one(PAGE, 'caption.infobox-title')) == 'The Doors'


def test_grouping_collects_both_branches() -> None:
    assert len(select(PAGE, '.infobox-label, .infobox-data')) == 2


def test_attribute_presence_and_prefix_match() -> None:
    assert len(select(PAGE, 'figure[typeof]')) == 1
    assert len(select(PAGE, 'figure[typeof^="mw:File"]')) == 1
    assert select(PAGE, 'figure[typeof^="mw:Image"]') == ()
    assert len(select(PAGE, 'figure[typeof="mw:File/Thumb"]')) == 1


def test_descendant_and_child_combinators() -> None:
    assert len(select(PAGE, 'table th')) == 1
    assert select(PAGE, 'div > td') == ()
    assert len(select(PAGE, 'div > table')) == 1


def test_multiple_classes_in_one_compound() -> None:
    assert len(select(PAGE, 'table.infobox.vcard')) == 1
    assert select(PAGE, 'table.infobox.plainlist') == ()


def test_limit_truncates() -> None:
    assert len(select(PAGE, 'th, td, caption', limit=2)) == 2


@pytest.mark.parametrize('selector', ['td:nth-child(2)', '', 'table >', 'th + td', '*'])
def test_unsupported_syntax_raises(selector: str) -> None:
    with pytest.raises(SelectorError):
        select(PAGE, selector)


def test_the_offending_selector_is_quoted_in_the_message() -> None:
    with pytest.raises(SelectorError) as failure:
        select(PAGE, 'td:nth-child(2)')
    assert 'nth-child' in str(failure.value)


def test_compilation_is_cached() -> None:
    compile_selector.cache_clear()
    select(PAGE, 'table th')
    select(PAGE, 'table th')
    assert compile_selector.cache_info().hits == 1
