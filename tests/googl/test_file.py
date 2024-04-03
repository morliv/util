from util.relation import Relation
from util.googl import file, File


def test_files(paths):
    files = [File.sync(p) for p in paths]
    assert Relation(paths, File(parents=['root']).match(pattern='tmp'),
                    file.equal).one_to_one()
    for f in files: File.delete(f)
