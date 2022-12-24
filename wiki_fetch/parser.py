from .generic import *


class Parser():

    def __init__(self, page: PAGE) -> None:
        self.page = page
        self.elements: ELEMENTS = None
        self.fields = {
            TABLES: ('tables',),
            ARRAY: ('array', 'last', 'first', 'merged',),
            ARRAYS: ('all',)}
        for TYPE in self.fields:
            for field in self.fields[TYPE]:
                self.__dict__ |= {field: TYPE()}

    def init(self) -> None:
        self.select()
        self.manage()
        self.export()

    def clean(self, string: str, mode: str = 'content') -> str:
        if mode == 'content':
            replacers = {'"':'', '\u200b': '', '\u2013': '-', '[edit]': '', '\n': ' '}
            string = re.sub(r'\[\d*\]|\[\.\.\.\]', '', normalize('NFKD', string))
        elif mode == 'href':
            replacers = {'_':' ', '#': ''}
        for chars, replacer in replacers.items(): string = string.replace(chars, replacer)
        return string.strip()

    def prepare(self,
        elements: ELEMENTS | ELEMENT,
        tag: TAG = None,
        replacer: str = None
        ) -> None:
        if isinstance(elements, ELEMENT): elements = (elements,)
        for element in elements:
            if not isinstance(element, ELEMENT): continue
            for tag in element.find_all(tag.name, tag.attrs
                    ) if tag.attrs else element.find_all(tag.name):
                tag.replace_with(replacer) if replacer else tag.extract()

    def derive(self, tr: ELEMENT) -> tuple[ELEMENT | ELEMENTS]:
        ths: ELEMENTS = tr.find_all('th')
        tds: ELEMENTS = tr.find_all('td')
        th: ELEMENT = (ths[0], ths.clear())[0] if len(ths) == 1 else None
        td: ELEMENT = (tds[0], tds.clear())[0] if len(tds) == 1 else None
        ul: ELEMENT = td.find('ul') if td else None
        return ths, tds, th, td, ul

    def scope(self, element: ELEMENT) -> SCOPE:
        return SCOPE(
            row=int(re.split(r'(\s|[a-zA-Z])', row)[0]) if (row := element.get('rowspan')) else 1, 
            col=int(re.split(r'(\s|[a-zA-Z])', col)[0]) if (col := element.get('colspan')) else 1, 
            scope=scope if (scope := element.get('scope')) else None)

    def select(self, page: PAGE = None, tag: TAG = None) -> None:
        if not tag: tag = self.tag
        if not page: page = self.page
        if not page: return None
        self.heading: str = self.clean(page.html.find('h1').text)
        self.elements: ELEMENTS = page.content.find_all(
            tag.name, attrs=tag.attrs, recursive=tag.recursive
            ) if tag.attrs else page.content.find_all(tag.name, recursive=tag.recursive)

    def manage(self) -> None:
        for table in self.gather(self.elements):
            self.tables += (table,)

    def export(self) -> None:
        for order, table in enumerate(self.tables):
            self.array = table.data()
            self.merged |= self.array
            self.all += (self.array,)
        self.last = self.array
        if self.all: self.first = self.all[0]
