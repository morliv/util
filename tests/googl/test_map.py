from relation import Relation
from googl.file import File
from googl.map import Map


def test_map(structure):
    local_paths = [f.p for f in structure.files]
    files = [Map(p).file for p in local_paths]
    assert Relation(files, local_paths, File.equivalent).bijection()
