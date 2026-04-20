from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Expectation:
    topic: str
    language: str
    url: str
    title: str
    infobox: tuple[int, int]
    paragraph: tuple[int, int]
    listing: tuple[int, int]
    thumb: tuple[int, int]

    @property
    def name(self) -> str:
        return f'{self.topic}-{self.language}'


PAGES: tuple[Expectation, ...] = (
    Expectation(
        topic='quantum',
        language='en',
        url='https://en.wikipedia.org/wiki/Quantum_mechanics',
        title='Quantum mechanics',
        infobox=(0, 0),
        paragraph=(5, 20),
        listing=(3, 12),
        thumb=(5, 22),
    ),
    Expectation(
        topic='quantum',
        language='ru',
        url='https://ru.wikipedia.org/wiki/Квантовая_механика',
        title='Квантовая механика',
        infobox=(0, 0),
        paragraph=(4, 18),
        listing=(1, 5),
        thumb=(5, 22),
    ),
    Expectation(
        topic='quantum',
        language='ja',
        url='https://ja.wikipedia.org/wiki/量子力学',
        title='量子力学',
        infobox=(0, 0),
        paragraph=(4, 16),
        listing=(8, 32),
        thumb=(1, 6),
    ),
    Expectation(
        topic='floyd',
        language='en',
        url='https://en.wikipedia.org/wiki/Pink_Floyd',
        title='Pink Floyd',
        infobox=(1, 5),
        paragraph=(3, 14),
        listing=(4, 16),
        thumb=(8, 32),
    ),
    Expectation(
        topic='floyd',
        language='ru',
        url='https://ru.wikipedia.org/wiki/Pink_Floyd',
        title='Pink Floyd',
        infobox=(1, 5),
        paragraph=(3, 14),
        listing=(2, 10),
        thumb=(12, 48),
    ),
    Expectation(
        topic='floyd',
        language='ja',
        url='https://ja.wikipedia.org/wiki/ピンク・フロイド',
        title='ピンク・フロイド',
        infobox=(1, 5),
        paragraph=(2, 8),
        listing=(19, 78),
        thumb=(5, 20),
    ),
    Expectation(
        topic='stanley',
        language='en',
        url='https://en.wikipedia.org/wiki/Stanley_Cup',
        title='Stanley Cup',
        infobox=(1, 5),
        paragraph=(2, 10),
        listing=(3, 14),
        thumb=(6, 26),
    ),
    Expectation(
        topic='stanley',
        language='ru',
        url='https://ru.wikipedia.org/wiki/Кубок_Стэнли',
        title='Кубок Стэнли',
        infobox=(1, 5),
        paragraph=(2, 10),
        listing=(3, 14),
        thumb=(1, 6),
    ),
    Expectation(
        topic='stanley',
        language='ja',
        url='https://ja.wikipedia.org/wiki/スタンレー・カップ',
        title='スタンレー・カップ',
        infobox=(1, 5),
        paragraph=(4, 18),
        listing=(4, 16),
        thumb=(1, 5),
    ),
)
