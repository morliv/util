import sys
from pathlib import Path
from typing import List

import pytest

from relation import Relation
from googl import results, File, Files, Map


def consistent(paths) -> bool:
    possibilities = [f for p in paths \
                for f in File(parents=['root']).matches(p.name)]
    assert Relation(paths,
                    possibilities,
                    lambda p: Map(p).file()) \
        .one_to_one()

def finalize(paths: List[Path], maps: List[Map]):
    consistent(paths)
    for m in maps: m.drive.delete()

def test_drive_map(paths):
    maps = []
    for p in paths:
        m = Map(p)
        m.sync()
        maps.append(m)
    finalize(paths, maps)

@pytest.mark.skip
def test_command_line(paths):
    maps = []
    for p in paths:
        sys.argv = ['', '-l', p]
        maps.append(results()['mapping'])
    finalize(paths, maps)