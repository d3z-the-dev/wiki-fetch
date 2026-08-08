from wiki_fetch.base.errors import WikiError
from wiki_fetch.generic import messages


class PageError(WikiError):
    def __init__(self, url: str) -> None:
        super().__init__(messages.Message.content.format(url=url))
        self.url = url


class InputError(WikiError):
    pass
