from wiki_fetch.generic.layout import INDENT, MARK, MISSING, NEWLINE, STEP


def test_the_text_renderer_indents_by_four() -> None:
    assert INDENT == 4
    assert STEP == '    '


def test_a_label_is_followed_by_a_colon_and_a_space() -> None:
    assert MARK == ': '


def test_the_newline_arrived_as_a_real_line_feed() -> None:
    assert NEWLINE == '\n'
    assert len(NEWLINE) == 1


def test_a_missing_value_renders_as_null() -> None:
    assert MISSING == 'null'
