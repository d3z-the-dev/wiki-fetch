from wiki_fetch.generic.parts import LABELS, Format, Part, Selection


def test_every_member_is_lowercase() -> None:
    assert all(member.name.islower() for member in (*Part, *Format, *Selection))


def test_auto_kept_the_values_identical_to_the_names() -> None:
    assert all(member.value == member.name for member in (*Part, *Format, *Selection))


def test_the_string_values_did_not_change() -> None:
    assert [member.value for member in Part] == [
        'infobox',
        'paragraph',
        'table',
        'list',
        'thumb',
        'toc',
        'all',
    ]
    assert [member.value for member in Format] == ['text', 'json', 'dict', 'toml']
    assert [member.value for member in Selection] == ['first', 'last', 'all']


def test_every_part_has_an_output_label() -> None:
    assert set(LABELS) == set(Part)
    assert LABELS[Part.infobox] == 'Infobox'
    assert LABELS[Part.toc] == 'Toc'
