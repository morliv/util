import sys
from pathlib import Path
sys.path.append(str(Path.home() / 'util'))
print(sys.path)

import pytest

from file import Structure
from list import nestedly


@pytest.fixture(params=[
    [],
    ['1'],
    ['1', '2'],
    [[]],
    [[], []],
    [['1']],
    [['1'], ['2']],
    [['1', '2'], ['3', '4']],
    [[], '1']
])
def blueprint(request):
    return nestedly(request.param, lambda s: "Content " + s)


@pytest.fixture
def structure(blueprint):
    s = Structure(blueprint)
    yield s
    s.clean()


@pytest.fixture
def paths(structure):
    yield [f.p for f in structure.files]
