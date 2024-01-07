from relation import Relation
from g.files import File, Map


def test_map(structure):
    local_paths = [f.p for f in structure.files]
    if len(structure.files) > 0:
        breakpoint()
    files = [Map(p).file for p in local_paths]
    assert Relation(files, local_paths, File.equivalent).bijection()
 