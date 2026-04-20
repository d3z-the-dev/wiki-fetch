import json

import pytest

from tests.live import fetched, recorded
from tests.pages import PAGES, Expectation

pytestmark = [pytest.mark.network, pytest.mark.golden]


@pytest.mark.parametrize('page', PAGES, ids=lambda page: page.name)
def test_json_output_matches_the_record(page: Expectation) -> None:
    produced = fetched(page).json
    assert produced == recorded(page, produced)


@pytest.mark.parametrize('page', PAGES, ids=lambda page: page.name)
def test_the_dictionary_round_trips_through_json(page: Expectation) -> None:
    output = fetched(page)
    assert json.loads(output.json) == json.loads(json.dumps(output.dict, ensure_ascii=False))
