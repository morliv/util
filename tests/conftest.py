import pytest
print(pytest.__file__)

from file import Structure

@pytest.fixture(params=[
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
    return request.param

@pytest.fixture
def structure(blueprint):
    s = Structure(blueprint)
    yield s
    s.clean()
