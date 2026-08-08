from wiki_fetch.generic.console import PROGRAM, Code, Flag, Help


def test_exit_codes_follow_the_shell_convention() -> None:
    assert (Code.done, Code.failure, Code.misuse) == (0, 1, 2)


def test_every_documented_flag_has_a_short_and_a_long_form() -> None:
    assert Flag.url.short == '-u'
    assert Flag.url.long == '--url'
    assert all(len(member.short) == 2 and member.long.startswith('--') for member in Flag)


def test_every_flag_carries_a_help_line() -> None:
    assert {member.name for member in Flag} == {member.name for member in Help}


def test_the_program_is_named() -> None:
    assert PROGRAM == 'wiki-fetch'
