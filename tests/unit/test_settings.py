from dataclasses import asdict, is_dataclass

import pytest

from wiki_fetch.utils.settings import Group, settings


def test_schema_turns_a_flat_mapping_into_a_dataclass() -> None:
    built = settings.schema('sample', {'count': 3, 'name': 'wiki'})
    assert is_dataclass(built)
    assert built.count == 3
    assert built.name == 'wiki'


def test_schema_recurses_into_nested_tables() -> None:
    built = settings.schema('sample', {'policy': {'timeout': 10.0, 'hops': 5}})
    assert is_dataclass(built.policy)
    assert built.policy.timeout == 10.0
    assert built.policy.hops == 5


def test_a_built_object_is_frozen() -> None:
    built = settings.schema('sample', {'count': 3})
    with pytest.raises(AttributeError):
        built.count = 4


def test_a_built_object_has_no_instance_dictionary() -> None:
    built = settings.schema('sample', {'count': 3})
    assert asdict(built) == {'count': 3}
    with pytest.raises(TypeError):
        vars(built)


def test_every_group_loads() -> None:
    assert all(is_dataclass(settings.load(group)) for group in Group)


def test_the_configuration_directory_ships_inside_the_package() -> None:
    assert settings.config.is_dir()
    assert sorted(path.stem for path in settings.config.glob('*.toml')) == [
        'languages',
        'layout',
        'markup',
        'network',
        'site',
    ]


def test_the_layout_newline_is_a_real_line_feed() -> None:
    layout = settings.load(Group.layout)
    assert layout.newline == '\n'
    assert len(layout.newline) == 1
