from wiki_fetch.base.html.text import collapse, normalize


def test_normalize_folds_compatibility_forms_and_strips_footnotes() -> None:
    source = 'Light My Fire[1] \N{EN DASH} 1967\N{ZERO WIDTH SPACE}'
    assert normalize(source) == 'Light My Fire - 1967'


def test_normalize_drops_edit_links_and_ellipsis_marks() -> None:
    assert normalize('History[edit] [...]') == 'History'


def test_collapse_squeezes_whitespace() -> None:
    assert collapse('  The   Doors \n formed  ') == 'The Doors formed'


def test_collapse_treats_non_breaking_space_as_whitespace() -> None:
    assert collapse('Years\xa0active') == 'Years active'
