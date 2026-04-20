from wiki_fetch.generic.syntax import IMPLICIT, TOKEN, VOID, Attribute, Capture, Tag


def test_attribute_values_are_the_html_spellings() -> None:
    assert Attribute.ID.value == 'id'
    assert Attribute.CLASS.value == 'class'
    assert Attribute.COLSPAN.value == 'colspan'


def test_the_class_attribute_keeps_an_uppercase_member_name() -> None:
    assert 'CLASS' in Attribute.__members__
    assert 'class' not in Attribute.__members__


def test_tag_values_are_the_html_tag_names() -> None:
    assert Tag.ROW.value == 'tr'
    assert Tag.PARAGRAPH.value == 'p'
    assert Tag.BREAK.value == 'br'
    assert Tag.LIST.value == 'ul'


def test_capture_names_match_the_selector_pattern_groups() -> None:
    assert set(TOKEN.groupindex) == {member.value for member in Capture}


def test_capture_uses_auto_so_the_value_repeats_the_name() -> None:
    assert all(member.value == member.name for member in Capture)


def test_void_and_implicit_stay_html_facts() -> None:
    assert 'br' in VOID
    assert IMPLICIT['td'] == frozenset({'td', 'th'})
