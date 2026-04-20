from wiki_fetch.generic import layout, notation, types


def quote(value: str) -> str:
    return notation.QUOTED.format(value=value.translate(notation.ESCAPES))


def label(key: str) -> str:
    return key if notation.BARE.match(key) else quote(key)


def nested(value: types.Data) -> bool:
    if isinstance(value, dict):
        return True
    return isinstance(value, tuple) and bool(value) and all(isinstance(one, dict) for one in value)


def scalar(value: types.Data) -> str:
    if value is None:
        return quote(layout.MISSING)
    if isinstance(value, dict):
        return inline(value)
    if isinstance(value, tuple):
        return notation.ARRAY.format(items=notation.SEPARATOR.join(scalar(item) for item in value))
    return quote(value)


def inline(table: types.Payload) -> str:
    return notation.INLINE.format(
        fields=notation.SEPARATOR.join(
            notation.FIELD.format(key=label(key), value=scalar(value))
            for key, value in table.items()
        )
    )


def header(lines: list[str], path: tuple[str, ...], template: str) -> None:
    if lines:
        lines.append(str())
    lines.append(template.format(path=notation.PATH.join(label(step) for step in path)))


def bare(table: types.Payload) -> bool:
    return not table or any(not nested(value) for value in table.values())


def section(lines: list[str], path: tuple[str, ...], source: types.Payload) -> None:
    for key, value in source.items():
        if not nested(value):
            lines.append(notation.FIELD.format(key=label(key), value=scalar(value)))
    for key, value in source.items():
        if isinstance(value, dict):
            if bare(value):
                header(lines, (*path, key), notation.HEADER)
            section(lines, (*path, key), value)
        elif nested(value):
            for element in value:
                header(lines, (*path, key), notation.REPEATED)
                section(lines, (*path, key), element)


def build(data: types.Payload) -> str:
    lines: list[str] = list()
    section(lines, tuple(), data)
    return layout.NEWLINE.join(lines)
