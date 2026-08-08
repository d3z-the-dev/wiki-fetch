from wiki_fetch.core.errors import InputError
from wiki_fetch.generic import languages, messages


def resolve(value: str) -> str:
    wanted = value.strip().casefold()
    named = languages.NAMES.get(wanted)
    if named is not None:
        return named
    if languages.PATTERN.match(wanted):
        return wanted
    raise InputError(messages.Message.language.format(value=value))
