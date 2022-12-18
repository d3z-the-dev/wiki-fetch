from .generic import *
from . import parts
from . import stuff


class Wiki():

    def __init__(self, lang: str = 'English') -> None:
        self.wiki = f"https://{stuff.linguist(lang)}.wikipedia.org/"
        self.headers = {
            'User-Agent': f"Mozilla/5.0 (X11; U; Linux x86_64) Gecko/081222 Firefox/108.0"}

    def get(self, url: str) -> str | None:
        response: http.client.HTTPResponse = request.urlopen(
            request.Request(url, headers=self.headers)) if url else None
        return response.read().decode('utf-8') if response else None

    def extract(self, response: str | None) -> HTML | None:
        return HTML(response, 'html.parser') if response else None

    def capture(self, url: str) -> PAGE:
        html = self.extract(self.get(url))
        if not html: return None
        contents: ELEMENT | None = html.find('div', {'id': 'bodyContent'})
        resuslts: ELEMENT | None = html.find('div', {'class': 'searchresults'})
        catlinks: ELEMENT | None = html.find('div', {'id': 'catlinks'})
        if resuslts:
            results = resuslts.find('ul'); resuslt = resuslts.find('li') if resuslts else None
            url = self.wiki + resuslt.find('a').get('href') if resuslt else None        
        elif catlinks and 'Disambiguation pages' in [li.text for li in catlinks.find('ul')]:
            href = [a.get('href') for a in contents.find_all('a') if a.get('href').startswith('/wiki/')][0]
            url = f"{self.wiki}{href}"
        html = self.extract(self.get(url)) if resuslts or catlinks else html
        body = html.select_one('#bodyContent')
        content = body.select_one('.mw-parser-output') if body else None
        return PAGE(url=url, html=html, content=content)

    def search(self, query: str = None, url: str = None, part: str = None, item: str = None) -> dict:
        self.output = dict()
        getter = lambda part, item: parts.__dict__[part.title()](page=self.page).__dict__[item]
        texter = lambda json: '\n'.join([line[4:] for line in re.sub(
            r'\",|\"|\},|\{|\}|\],|\[|\]', '', json).split('\n') if line.strip()])
        if not url and not query: return OUTPUT(text='There is no input data (query string or URL).')
        if query: url = f"{self.wiki}?search={quote(query.title())}"
        self.page = self.capture(url)
        Parts = ('Infobox', 'Paragraph', 'Table', 'List', 'Thumb', 'Toc',)
        [self.output.update({part: getter(part, item)}) for part in Parts
            ] if part == 'all' else self.output.update({part.title(): getter(part, item)})
        self.output |= {'URL': unquote(self.page.url)}
        return OUTPUT(
            dict=self.output,
            json=(json := dumps(self.output, indent=4, ensure_ascii=False, allow_nan=True)),
            text=texter(json))
