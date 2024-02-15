import pytest
import subprocess
from typing import Callable
from pathlib import Path

from relation import Relation
from . import results
from googl.file import File
from googl.map import Map


@pytest.fixture
def drive_map(paths):
    maps = []
    for p in paths:
        m = Map(p)
        m.sync()
        maps.append(m)
    yield
    for m in maps: m.drive.delete()

@pytest.fixture
def upload(paths, monkeypatch):
    for p in paths:
        monkeypatch.setattr('argv', ['-l', p])
        m = results()['mapping']
    yield
    for m in map: m.drive.delete()
 
def consistent(paths) -> bool:
    assert Relation(paths,
                    File.files(),
                    lambda p: Map(p).file()) \
        .one_to_one()

@pytest.mark.parametrize('mapping', [drive_map, upload])
def test_map(structure_paths, mapping):
    mapping(structure_paths)
    consistent(structure_paths)
