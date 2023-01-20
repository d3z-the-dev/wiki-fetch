from .generic import *
from .parser import Parser


class Infobox(Parser):

    def __init__(self, page: PAGE) -> None:
        Parser.__init__(self, page=page)
        self.tag = TAG(name='table', attrs={'class': ['infobox', 'infobox_v2']}, recursive=False)
        self.init()

    def extract(self, element: ELEMENT) -> ELEMENTS:
        for inner in (nested := element.find_all(self.tag.name)):
            inner.extract()
        return nested if nested else ()

    def parse(self, elements: ELEMENTS) -> TABLE:
        table = TABLE(); row = ROW(); section = DICT(); order = 0

        def stower(row: ROW, section: DICT) -> ROW:
            dicts: dict[DICT] = {}; order = 0
            for key, value in zip(section.keys(), section.values()):
                if type(key) == int and type(value) in (list, tuple):
                    for line in value: dicts |= DICT({order + 1: line}); order += 1
                else: dicts |= DICT({key: value}); order += 1
            return update(row, CELL(dicts)) if section else row

        for line, tr in enumerate(elements):
            if type(tr) != ELEMENT: continue
            label, data = '', ()
            ths, tds, th, td, ul = self.derive(tr)
            if th:
                self.prepare(elements=th, tag=TAG(name='br'), replacer='&&')
                label = ' '.join(th.text.split('&&'))
            if ul:
                data = [li.text.title() for li in ul.find_all('li')]
            if tds:
                data = [td.text for td in tds]
            elif td:
                if order <= 2 and (image := td.find(attrs={'class': 'image'})):
                    section |= DICT({'Image': f"https:{image.find('img').get('src')}"})
                    if (caption := td.find(attrs={'class': 'infobox-caption'})):
                        section |= DICT({'Caption': self.clean(caption.text)})
                    if image or caption: order += 1; continue
                if 'class' in td.attrs and 'plainlist' in td['class']:
                    if (child := td.find('div', recursive=False)):
                        for div in [self.clean(div.text) for div in child.find_all('div', recursive=False)]:
                            if len((pair := div.split(':'))) > 1: section |= DICT({pair[0]: pair[1]})
                            else: section |= DICT({div: ''})
                        if div: continue
                if td.find_all('br'):
                    self.prepare(elements=td, tag=TAG(name='br'), replacer='&&')
                    if not data: data = td.text.split('&&')
                if len((anchors := td.find_all('a', recursive=False))) > 2:
                    if not data: data = [anchor.text for anchor in anchors]
                if next(td.children).name in ['div', 'span', 'time']:
                    if not data: data = [td.text.strip()]
                if not data: data = [td.text.strip()]
            label = self.clean(label)
            data = [clear for line in data if (clear := self.clean(line))]
            if not label and not data: continue
            if not label:
                if len(section) > 0 and list(section.keys())[-1] == 'Image': label = 'Caption'
                if len(data) >= 2 and ':' in data[0]: label = data.pop(0).replace(':', '')
                if not label and len(data) >= 1: label = order + 1
            if label and th and not td or not tds and not data:
                if (row := stower(row, section)) and row.label:
                    if row.cells or order != 0: table = update(table, row)
                row = ROW(label=label); section = DICT(); order = 0; continue
            section |= DICT({label: data[0] if len(data) == 1 else tuple(data)})
            order += 1
        table = update(table, row) if (row := stower(row, section)).label else table
        yield table

    def gather(self, elements: ELEMENTS) -> TABLE:
        unpacker = lambda table: ((trs := [tr for tr in table.find('tbody').find_all('tr')]),
            self.clean(caption.text) if (caption := table.select_one('caption.infobox-title')
                ) else self.clean((th := trs[0].find('th')).text) if trs else None)

        for element in elements:
            self.prepare(elements=element, tag=TAG(name='span', attrs={'class': 'noprint'}))
            self.prepare(elements=element, tag=TAG(name='span', attrs={'style': 'display:none'}))
            self.prepare(elements=element, tag=TAG(name='td', attrs={'class': 'navigation-only'}))
            self.prepare(elements=element, tag=TAG(name='small'))
            self.prepare(elements=element, tag=TAG(attrs={'class': 'infobox-below'}))
            nested = self.extract(element=element)
            trs, header = unpacker(element)
            table = merge(TABLE(label=header), next(self.parse(trs)))
            for order, inner in enumerate(nested):
                trs, header = unpacker(inner)
                inner = merge(TABLE(label=header), next(self.parse(trs)))
                if header not in [row.label for row in table.rows]: label = header 
                else: label = f"{header} {order + 1}"
                row = ROW(label=label, cells=(CELL(data=inner.data()[header]),))
                if row: table = update(table, row)
            yield table


class Paragraph(Parser):

    def __init__(self, page: PAGE) -> None:
        Parser.__init__(self, page=page)
        self.tag = TAG(name=['h2', 'h3', 'p'], recursive=False)
        self.init()

    def parse(self, elements: ELEMENTS) -> TABLE:
        table = TABLE(); row = None; paragraphs = TUPLE(); header = 'Prologue'; headline = 'Prologue'
        for order, element in enumerate(elements):
            if type(element) != ELEMENT: continue
            self.prepare(elements=element, tag=TAG(name='span', attrs={'class': 'noprint'}))
            self.prepare(elements=element, tag=TAG(name='span', attrs={'class': 'mw-editsection'}))
            self.prepare(elements=element, tag=TAG(name='small'))
            text = self.clean(element.text)
            if element.name == 'p':
                if text: paragraphs += (text,)
            if element.name == 'h3':
                if row and row.label: table = update(table, row)
                if paragraphs: row = ROW(label=headline, cells=(CELL(paragraphs),))
                headline = text
                paragraphs = TUPLE()
            if element.name == 'h2':
                table = rename(table, header)
                if row: table = update(table, row)
                if paragraphs:
                    if not headline:
                        for order, paragraph in enumerate(paragraphs):
                            table = update(table, ROW(label=order + 1, cells=(CELL(paragraph),)))
                    else:
                        table = update(table, ROW(label=headline, cells=(CELL(paragraphs),)))
                yield table
                header = text; table = TABLE(); row = None; paragraphs = TUPLE(); headline = None

    def gather(self, elements: ELEMENTS) -> TABLE:
        for table in self.parse(elements):
            if table.rows: yield table


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
