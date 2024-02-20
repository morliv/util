import sys

from relation import Relation
from googl import results
from googl import File
from googl import Map


def consistent(paths) -> bool:
    possibilities = [f for p in paths \
                for f in File(parents=['root']).prefixed(p.name)]
    assert Relation(paths,
                    possibilities,
                    lambda p: Map(p).file()) \
        .one_to_one()


def test_drive_map(paths):
    maps = []
    for p in paths:
        m = Map(p)
        m.sync()
        maps.append(m)
    consistent(paths)
    for m in maps: m.drive.delete()


def test_command_line(paths):
    maps = []
    for p in paths:
        sys.argv = ['', '-l', p]
        maps.append(results()['mapping'])
    consistent(paths)
    for m in maps: m.drive.delete()
 