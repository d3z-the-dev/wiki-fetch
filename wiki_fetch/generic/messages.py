from enum import StrEnum


class Message(StrEnum):
    language = 'Unknown language: {value}.'
    part = 'Unknown part: {value}.'
    selection = 'Unknown item: {value}.'
    input = 'No input: give a URL or a query.'
    status = 'Wikipedia answered {status} for {url}.'
    network = 'Cannot reach {url}: {reason}.'
    decode = 'Cannot decode the response from {url}.'
    redirect = 'Too many redirects for {url}.'
    scheme = 'Unsupported URL scheme: {value}.'
    content = 'No article content at {url}.'
    selector = 'Unsupported selector: {value}.'
