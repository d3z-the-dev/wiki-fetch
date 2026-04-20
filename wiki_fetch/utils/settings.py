import tomllib
from collections.abc import Mapping
from dataclasses import make_dataclass
from enum import StrEnum, auto
from pathlib import Path
from typing import Any


class Directory(StrEnum):
    config = auto()


class Suffix(StrEnum):
    toml = auto()


class Group(StrEnum):
    markup = auto()
    network = auto()
    site = auto()
    languages = auto()
    layout = auto()


class Settings:
    def __init__(self) -> None:
        self.config = Path(__file__).parent.parent / Directory.config

    def schema(self, name: str, source: Mapping[str, Any]) -> Any:
        built = {
            key: self.schema(key, value) if isinstance(value, dict) else value
            for key, value in source.items()
        }
        fields = [(key, type(value)) for key, value in built.items()]
        return make_dataclass(name, fields, frozen=True, slots=True)(**built)

    def load(self, group: Group) -> Any:
        source = self.config / f'{group}.{Suffix.toml}'
        with source.open('rb') as handle:
            return self.schema(group, tomllib.load(handle))


settings = Settings()
