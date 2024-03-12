import sys
from typing import List

import pytest

from relation import Relation
from googl import results, file, File


def consistent(paths, files: List[File]) -> bool:
    possibilities = [drive_f for p in paths \
                for drive_f in File(parents=['root']).matches(p.name)]
    assert Relation(paths, possibilities, file.equal).one_to_one()
    for f in files: f.delete()


def test_file(paths):
    consistent(paths, [File(p=p) for p in paths])


@pytest.mark.skip
def test_command_line(paths):
    maps = []
    for p in paths:
        sys.argv = ['', '-l', p]
        maps.append(results()['mapping'])
    consistent(paths, maps)
