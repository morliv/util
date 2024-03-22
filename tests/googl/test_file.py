from relation import Relation
from googl import file, File


def test_files(paths):
    files = [File.sync(p) for p in paths]
    assert Relation(paths, File(parents=['root']).list(pattern='tmp'),
                    file.equal).one_to_one()
    for f in files: f.delete()
