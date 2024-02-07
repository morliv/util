from relation import Relation
from googl.file import File
from googl.map import Map


def assert_mapped(paths, map=lambda p: Map(p).file):
    files = [map(p) for p in paths]
    assert Relation(files, paths, File.equivalent).bijection()
