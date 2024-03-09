import sys
from pathlib import Path
from typing import List

import pytest

from relation import Relation
from googl import results, file, File


def consistent(paths) -> bool:
    possibilities = [drive_f for p in paths \
                for drive_f in File(parents=['root']).matches(p.name)]
    assert Relation(paths, possibilities, file.equal).one_to_one()


def finalize(paths: List[Path], files: List[File]):
    consistent(paths)
    for f in files: f.delete()


def test_drive_map(paths):
    finalize(paths, [File.load(p) for p in paths])


@pytest.mark.skip
def test_command_line(paths):
    maps = []
    for p in paths:
        sys.argv = ['', '-l', p]
        maps.append(results()['mapping'])
    finalize(paths, maps)
