from wiki_fetch.base.extract.parts import Infobox
from wiki_fetch.base.html.tokenizer import parse

SEMANTIC = parse(
    "<div><table class='infobox'><tbody>"
    "<tr><th class='infobox-above'>The Doors</th></tr>"
    "<tr><td class='infobox-image'><img src='//upload/doors.jpg'>"
    "<div class='infobox-caption'>The Doors in 1966</div></td></tr>"
    "<tr><th class='infobox-header'>Background information</th></tr>"
    "<tr><th class='infobox-label'>Origin</th><td class='infobox-data'>Los Angeles</td></tr>"
    "<tr><th class='infobox-label'>Genres</th><td class='infobox-data'>"
    '<ul><li>Psychedelic rock</li><li>Blues rock</li></ul></td></tr>'
    '</tbody></table></div>'
).root

STRUCTURAL = parse(
    "<div><table class='infobox'><tbody>"
    '<tr><th>ドアーズ</th></tr>'
    '<tr><th>基本情報</th></tr>'
    '<tr><th>出身地</th><td>ロサンゼルス</td></tr>'
    '</tbody></table></div>'
).root


def section(root_index: int, row_index: int) -> dict[str, object]:
    data = Infobox.read(SEMANTIC)[root_index].rows[row_index].cells[0].data
    assert isinstance(data, dict)
    return dict(data)


def test_semantic_tier_builds_sections() -> None:
    table = Infobox.read(SEMANTIC)[0]
    assert table.label == 'The Doors'
    assert [row.label for row in table.rows] == ['The Doors', 'Background information']


def test_semantic_tier_keeps_image_and_caption() -> None:
    opening = section(0, 0)
    assert opening['Image'] == 'https://upload/doors.jpg'
    assert opening['Caption'] == 'The Doors in 1966'


def test_multi_value_data_becomes_a_tuple() -> None:
    background = section(0, 1)
    assert background['Genres'] == ('Psychedelic rock', 'Blues rock')
    assert background['Origin'] == 'Los Angeles'


def test_structural_tier_works_without_semantic_classes() -> None:
    table = Infobox.read(STRUCTURAL)[0]
    assert table.label == 'ドアーズ'
    assert table.rows[0].label == '基本情報'
    assert table.rows[0].cells[0].data == {'出身地': 'ロサンゼルス'}


def test_pages_without_an_infobox_yield_nothing() -> None:
    assert Infobox.read(parse('<div><p>No box here</p></div>').root) == ()
