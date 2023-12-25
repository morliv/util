from util import dictionary, test, error
from util.relation import Relation
from g import File, Map


def test_map(structure):
    maps = [Map(f.p) for f in structure.files]
    assert Relation(structure.files, maps, File.equivalent).bijection()
 