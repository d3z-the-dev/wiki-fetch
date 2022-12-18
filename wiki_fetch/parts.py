from .generic import *
from .parser import Parser


class Infobox(Parser):

    def __init__(self, page: PAGE) -> None:
        Parser.__init__(self, page=page)
        self.tag = TAG(name='table', attrs={'class': ['infobox', 'infobox_v2']}, recursive=False)
        self.init()

    def extract(self, element: ELEMENT) -> TABLE:
        for inner in element.find_all(self.tag.name):
            inner.extract()
            yield self.parse(inner.find_all('tr'))

    def parse(self, elements: ELEMENTS) -> TABLE:
        table = TABLE(); row = ROW(); section = DICT(); order = 0
        stower = lambda row, section: (update(row, CELL(section)) if len(
            section) > 1 or len(section) == 1 and type(list(section.keys())[0]) != int else update(
            row, CELL(list(section.values()))) if len(section) == 1 and type(
            list(section.keys())[0]) == int else row) if section else row
        for tr in elements:
            if type(tr) != ELEMENT or not tr.text.strip(): continue
            label, data = '', ()
            ths, tds, th, td, ul = self.derive(tr)
            if th: 
                self.prepare(elements=th, tag=TAG(name='br'), replacer='&&')
                label = text[0] if ':' in th.text else ' '.join((text := th.text.split('&&')))
            if ul:
                data = [li.text.title() for li in ul.find_all('li')]
            elif td:
                if order <= 2 and (image := td.select_one('.image')):
                    section |= DICT({'Image': f"https:{image.find('img').get('src')}"})
                if td.find_all('br'):
                    self.prepare(elements=td, tag=TAG(name='br'), replacer='&&')
                    data = td.text.split('&&')
                elif next(td.children).name in ['div', 'span', 'time']:
                    data = [td.text.strip()]
                elif len((anchors := td.find_all('a', recursive=False))) > 1:
                    data = [anchor.text for anchor in anchors]
                else: data = [td.text.strip()]
            elif tds:
                data = [td.text for td in tds]
            label = self.clean(label)
            data = [clear for line in data if (clear := self.clean(line))]
            if not label and not data: continue
            if not label:
                if len(data) > 1 and ':' in data[0]: label = data.pop(0)
                if not label and len(section) > 0 and list(section.keys())[-1] == 'Image': label = 'Caption'
            if not label and len(data) == 1: label = data[0]; data = []
            if label and th and not td or not tds and not data:
                table = update(table, row) if (row := stower(row, section)).label else table
                row = ROW(label=label); section = DICT(); order = 0
                continue
            section |= DICT({label if label else order + 1: data[0] if len(data) == 1 else tuple(data)})
            order += 1
        table = update(table, row) if (row := stower(row, section)).label else table
        table = rename(table, table.rows[0].label) if table.length() else table
        return table

    def gather(self, elements: ELEMENTS) -> TABLE:
        for element in elements:
            nested = ROWS()
            self.prepare(elements=element, tag=TAG(name='span', attrs={'class': 'noprint'}))
            self.prepare(elements=element, tag=TAG(name='span', attrs={'style': 'display:none'}))
            self.prepare(elements=element, tag=TAG(name='td', attrs={'class': 'navigation-only'}))
            self.prepare(elements=element, tag=TAG(name='small'))
            self.prepare(elements=element, tag=TAG(attrs={'class': 'infobox-below'}))
            for order, inner in enumerate(self.extract(element=element)):
                if (title := inner.label) not in [row.label for row in nested]: label = title 
                else: label = f"{title} {order + 1}"
                nested += (ROW(label=label, cells=(CELL(data=inner.data()[title]),)),)
            if (caption := element.select_one('caption.infobox-title')):
                tr = HTML('<tr></tr>', 'html.parser'); caption.name = 'th'; tr.tr.insert(0, caption)
                table = self.parse([tr.find('tr')] + [tr for tr in element.find_all('tr')])
            else:
                table = self.parse(element.find_all('tr'))
            table = update(table, nested)
            yield table


class Paragraph(Parser):

    def __init__(self, page: PAGE) -> None:
        Parser.__init__(self, page=page)
        self.tag = TAG(name=['h2', 'h3', 'p'], recursive=False)
        self.init()

    def parse(self, elements: ELEMENTS) -> TABLE:
        row = None; header = 'Prologue'; headline = 'Prologue'; paragraphs = TUPLE()
        for order, element in enumerate(elements):
            if type(element) != ELEMENT: continue
            self.prepare(elements=element, tag=TAG(name='span', attrs={'class': 'noprint'}))
            self.prepare(elements=element, tag=TAG(name='small'))
            text = self.clean(element.text)
            if element.name == 'p':
                if text: paragraphs += (text,)
            elif element.name == 'h3':
                row = ROW(label=headline, cells=(CELL(paragraphs),))
                headline = text
                paragraphs = TUPLE()
            elif element.name == 'h2':
                if not row:
                    row = ROW(label=headline, cells=(CELL(paragraphs),))
                yield TABLE(label=header, rows=(row,))
                header = text

    def gather(self, elements: ELEMENTS) -> TABLE:
        for table in self.parse(elements):
            if table.rows[0].cells[0].data: yield table


class Table(Parser):

    def __init__(self, page: PAGE) -> None:
        Parser.__init__(self, page=page)
        self.tag = TAG(name='table', attrs={'class': 'wikitable'}, recursive=True)
        self.init()

    def parse(self, elements: ELEMENTS) -> TABLE:
        table = TABLE(); headers = ROWS(); previous = None
        packer = lambda element, order: CELL(
            data=self.clean(element.text), scope=self.scope(element))
        for line, tr in enumerate(elements):
            if type(tr) != ELEMENT: continue
            ths, tds, th, td, ul = self.derive(tr)
            cells = []
            for rows in (ths, (th,), tds, (td,)):
                if not rows or type(rows[0]) != ELEMENT: continue
                cells += [packer(row, order) for order, row in enumerate(rows)]
            if previous:
                for order, cell in enumerate(previous):
                    if (colspan := cell.scope.col) > 1:
                        for i in range(1, colspan):
                            previous.insert(order + i, CELL(data='', scope=SCOPE(col=0)))
                    if (rowspan := cell.scope.row) > 1:
                        mutual = resize(cell, row=rowspan - 1)
                        if order == 0:
                            label = re.split(r'(\s\[\d\])', mutual.data)[0] + f" [{mutual.index + 1}]" 
                            mutual = CELL(data=label, scope=mutual.scope, index=mutual.index + 1)
                        previous[order] = mutual
                        cells.insert(order, mutual)
                    else:
                        if len(cells) - 1 >= order: previous[order] = cells[order]
            else: previous = cells
            if len(cells) > 1 and not cells[0].data: cells.pop(0)
            if not tds and not td: row = ROW(label=f"Headers {line + 1}", cells=CELLS(cells))
            else: row = ROW(label=cells[0].data, cells=CELLS(cells[1:]))
            if len(row.cells) > 0 and row.cells[0].data: table = update(table, row)
        yield table

    def gather(self, elements: ELEMENTS) -> TABLE:
        for element in elements:
            root = TABLE(label=self.clean(title.text) if (
                title := element.find_previous('h3')) else 'No header')
            for table in self.parse(element.find_all('tr')):
                yield merge(root, table)


class List(Parser):

    def __init__(self, page: PAGE) -> None:
        Parser.__init__(self, page=page)
        self.tag = TAG(name='ul', recursive=False)
        self.init() 

    def parse(self, elements: ELEMENTS) -> TABLE:
        table = TABLE()
        for order, li in enumerate(elements):
            table = update(table, ROW(label=order + 1, cells=(CELL(self.clean(li.text)),)))
        yield table

    def gather(self, elements: ELEMENTS) -> TABLE:
        for element in elements:
            header = self.clean(title.text) if (title := element.find_previous('h2')) else 'No header'
            for table in self.parse(element.find_all('li', recursive=False)):
                yield rename(table, header)
                

class Thumb(Parser):

    def __init__(self, page: PAGE) -> None:
        Parser.__init__(self, page=page)
        self.tag = TAG(name='div', attrs={'class': 'thumb'}, recursive=False)
        self.init()

    def parse(self, elements: ELEMENTS) -> TABLE:
        for order, element in enumerate(elements):
            anchor: ELEMENT = element.find('a', {'class': 'image'})
            image = f"https:{anchor.find('img').get('src')}" if anchor else None
            header = self.clean(string=anchor.get(
                'href').split(':')[1].split('.')[0], mode='href') if anchor else order
            caption = self.clean(caption.text) if (caption := element.select_one('.thumbcaption')
                ) else 'No caption'
            yield TABLE(label=header, rows=(ROW(label=caption, cells=(CELL(image),)),))

    def gather(self, elements: ELEMENTS) -> TABLE:
        for table in self.parse(elements):
            yield table


class Toc(Parser):

    def __init__(self, page: PAGE) -> None:
        Parser.__init__(self, page=page)
        self.tag = TAG(name='div', attrs={'id': 'toc'}, recursive=True)
        self.init()

    def parse(self, elements: ELEMENTS) -> TABLE:
        table = TABLE()
        packer = lambda li, order: ROW(
            label=number.text if (number := li.select_one('.tocnumber')) else str(order + 1),
            cells=(CELL(text.text if (text := li.select_one('.toctext')) else 'No text'),))
        for order, li in enumerate(elements):
            table = update(table, packer(li, order))
            if (nested := li.find_all('li')):
                for inner in nested:
                    table = update(table, packer(inner, order))
        yield table

    def gather(self, elements: ELEMENTS) -> TABLE:
        for element in elements:
            header = title.text if (title := element.select_one('.toctitle')) else 'No title'
            if (ul := element.find('ul')):
                for table in self.parse(ul.find_all('li', recursive=False)):
                    yield rename(table, header)
