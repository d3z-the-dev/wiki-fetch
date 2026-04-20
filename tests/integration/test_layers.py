import ast
from pathlib import Path
from typing import Optional

import pytest

PACKAGE = 'wiki_fetch'
ROOT = Path(__file__).parent.parent.parent / PACKAGE
ORDER = {
    'cli': 0,
    'core': 1,
    'base.render': 2,
    'base.extract': 2,
    'base.html': 3,
    'generic': 4,
    'utils': 5,
}
SHARED = {f'{PACKAGE}.base.errors', f'{PACKAGE}.core.models'}
MODULES = sorted(ROOT.rglob('*.py'))


def submodule(base: str, name: str) -> bool:
    directory = ROOT.parent.joinpath(*base.split('.'))
    return (directory / f'{name}.py').exists() or (directory / name / '__init__.py').exists()


def imports(path: Path) -> set[str]:
    found: set[str] = set()
    package = '.'.join((PACKAGE, *path.relative_to(ROOT).parts[:-1]))
    for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ''
            qualified = base if node.level == 0 else f'{package}.{base}'
            found.update(
                f'{qualified}.{alias.name}' if submodule(qualified, alias.name) else qualified
                for alias in node.names
            )
    return {module for module in found if module.startswith(f'{PACKAGE}.')}


def layer(path: Path) -> Optional[str]:
    name = '.'.join(path.relative_to(ROOT).parts[:-1])
    return name if name in ORDER else None


def owner(module: str) -> Optional[str]:
    parts = module.split('.')[1:]
    for size in (2, 1):
        name = '.'.join(parts[:size])
        if name in ORDER:
            return name
    return None


@pytest.mark.parametrize('path', MODULES, ids=lambda path: path.stem)
def test_imports_never_flow_upward(path: Path) -> None:
    here = layer(path)
    if here is None:
        return
    for module in imports(path) - SHARED:
        target = owner(module)
        if target is not None:
            assert ORDER[here] <= ORDER[target], f'{path.name} imports upward into {module}'


@pytest.mark.parametrize('path', MODULES, ids=lambda path: path.stem)
def test_the_html_layer_stands_alone(path: Path) -> None:
    if layer(path) != 'base.html':
        return
    allowed = {
        f'{PACKAGE}.base.errors',
        f'{PACKAGE}.generic.syntax',
        f'{PACKAGE}.generic.text',
        f'{PACKAGE}.generic.network',
        f'{PACKAGE}.generic.messages',
    }
    for module in imports(path):
        assert module in allowed or module.startswith(f'{PACKAGE}.base.html')


@pytest.mark.parametrize('path', MODULES, ids=lambda path: path.stem)
def test_extractors_know_nothing_about_output(path: Path) -> None:
    here = layer(path)
    if here is None or not here.startswith('base.extract'):
        return
    assert not any(module.startswith(f'{PACKAGE}.base.render') for module in imports(path))


@pytest.mark.parametrize('path', MODULES, ids=lambda path: path.stem)
def test_renderers_know_nothing_about_html(path: Path) -> None:
    if layer(path) != 'base.render':
        return
    assert not any(module.startswith(f'{PACKAGE}.base.html') for module in imports(path))


def test_every_layer_was_examined() -> None:
    seen = {layer(path) for path in MODULES} - {None}
    assert seen <= set(ORDER)
    assert {'cli', 'core', 'base.html', 'base.extract', 'base.render', 'generic'} <= seen


@pytest.mark.parametrize('path', MODULES, ids=lambda path: path.stem)
def test_the_html_layer_never_reads_wikipedia_markup(path: Path) -> None:
    if layer(path) != 'base.html':
        return
    assert f'{PACKAGE}.generic.markup' not in imports(path)


@pytest.mark.parametrize('path', MODULES, ids=lambda path: path.stem)
def test_the_generic_package_never_imports_a_layer(path: Path) -> None:
    if layer(path) != 'generic':
        return
    for module in imports(path):
        assert module.startswith((f'{PACKAGE}.generic', f'{PACKAGE}.utils'))


@pytest.mark.parametrize('path', MODULES, ids=lambda path: path.stem)
def test_the_loader_imports_nothing_from_the_package(path: Path) -> None:
    if layer(path) != 'utils':
        return
    assert imports(path) == set()
