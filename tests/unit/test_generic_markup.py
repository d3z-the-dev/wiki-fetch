from wiki_fetch.generic.markup import (
    BARRIER,
    CLASSES,
    HEADINGS,
    LAYERS,
    PAIR,
    PROSE,
    SCHEME,
    SELECTORS,
    Label,
    unique,
)


def test_selectors_came_from_the_configuration() -> None:
    assert SELECTORS.infobox == 'table.infobox'
    assert SELECTORS.figure == 'figure[typeof^="mw:File"]'
    assert SELECTORS.noise.startswith('.noprint')


def test_classes_are_bare_names_not_selectors() -> None:
    assert CLASSES.above == 'infobox-above'
    assert CLASSES.label == 'infobox-label'
    assert not any(
        value.startswith(('.', '#')) for value in (CLASSES.above, CLASSES.label, CLASSES.caption)
    )


def test_layers_are_built_from_the_selectors_rather_than_repeated() -> None:
    assert (SELECTORS.content, SELECTORS.body, SELECTORS.parser) == LAYERS


def test_label_templates_survived_the_move() -> None:
    assert Label.caption.value == 'Caption'
    assert Label.headers.format(order=2) == 'Headers 2'


def test_scheme_is_built_from_the_fetchable_one() -> None:
    assert SCHEME == 'https:'


def test_unique_numbers_a_label_only_when_it_is_taken() -> None:
    assert unique(dict(), 'Origin') == 'Origin'
    assert unique({'Origin': 'x'}, 'Origin') == 'Origin 2'
    assert unique({'Origin': 'x', 'Origin 2': 'y'}, 'Origin') == 'Origin 3'
    assert unique({'Origin 2': 'y'}, 'Origin') == 'Origin'


def test_the_tag_groupings_are_unchanged() -> None:
    assert PAIR == ('th', 'td')
    assert HEADINGS == ('h2', 'h3', 'h4')
    assert 'p' in PROSE
    assert 'table' in BARRIER
