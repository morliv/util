import inspect
import pytest
from typing import Callable

from relation import Relation
from googl.file import File
from googl.map import Map

@pytest.fixture
def test_map(paths, tear_down_mapped):
    for p in paths:
        m = Map(p)
        m.sync()
    yield m

def consistent(paths, map_func: Callable) -> bool:
    return Relation(paths,
                    File.files(), 
                    lambda local: Map(local).drive) \
        .one_to_one()

def assert_mapped(paths, map=lambda p: Map(p).file):
    files = [map(p) for p in paths]
    assert Relation(files, paths, File.equivalent).bijection()
