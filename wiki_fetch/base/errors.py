from wiki_fetch.generic import messages


class WikiError(Exception):
    pass


class FetchError(WikiError):
    pass


class StatusError(FetchError):
    def __init__(self, status: int, url: str) -> None:
        super().__init__(messages.Message.status.format(status=status, url=url))
        self.status = status
        self.url = url


class DecodeError(FetchError):
    def __init__(self, url: str) -> None:
        super().__init__(messages.Message.decode.format(url=url))
        self.url = url


class SelectorError(WikiError):
    def __init__(self, selector: str) -> None:
        super().__init__(messages.Message.selector.format(value=selector))
        self.selector = selector
