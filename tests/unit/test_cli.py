import pytest

from tests.support import EMPTY_PAGE, Recorder, article
from wiki_fetch.cli.app import run
from wiki_fetch.cli.parser import build, read
from wiki_fetch.generic import parts

URL = 'https://en.wikipedia.org/wiki/The_Doors'


def transport() -> Recorder:
    return Recorder({URL: article()})


def test_argv_becomes_a_typed_options_record() -> None:
    options = read([])
    assert options.url is None
    assert options.lang == 'English'
    assert options.part is parts.Part.all
    assert options.item is parts.Selection.all
    assert options.output is parts.Format.text


def test_enumerations_are_parsed_at_the_boundary() -> None:
    options = read(['-p', 'toc', '-o', 'json', '-i', 'first'])
    assert (options.part, options.output, options.item) == (
        parts.Part.toc,
        parts.Format.json,
        parts.Selection.first,
    )


def test_text_output_is_printed(capsys: pytest.CaptureFixture[str]) -> None:
    assert run(['-u', URL, '-p', 'toc'], transport=transport()) == 0
    assert capsys.readouterr().out.startswith('Toc: ')


def test_json_output_is_selected(capsys: pytest.CaptureFixture[str]) -> None:
    assert run(['-u', URL, '-p', 'toc', '-o', 'json'], transport=transport()) == 0
    assert capsys.readouterr().out.lstrip().startswith('{')


def test_dict_output_is_selected(capsys: pytest.CaptureFixture[str]) -> None:
    assert run(['-u', URL, '-p', 'toc', '-o', 'dict'], transport=transport()) == 0
    assert capsys.readouterr().out.startswith("{'Toc'")


def test_missing_input_exits_with_two(capsys: pytest.CaptureFixture[str]) -> None:
    assert run([], transport=transport()) == 2
    assert 'No input' in capsys.readouterr().err


def test_unknown_language_exits_with_two(capsys: pytest.CaptureFixture[str]) -> None:
    assert run(['-u', URL, '-l', 'Klingonese'], transport=transport()) == 2
    assert 'Unknown language' in capsys.readouterr().err


def test_an_unreachable_page_exits_with_one(capsys: pytest.CaptureFixture[str]) -> None:
    empty = Recorder({URL: EMPTY_PAGE})
    assert run(['-u', URL], transport=empty) == 1
    assert 'No article content' in capsys.readouterr().err


@pytest.mark.parametrize('flag', ['-p', '-i', '-o'])
def test_unknown_enumeration_values_are_rejected_by_the_parser(flag: str) -> None:
    with pytest.raises(SystemExit):
        build().parse_args([flag, 'sidebar'])
