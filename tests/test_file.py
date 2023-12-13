from pathlib import Path

from util import file, test
from util.iterable import Comparative


class FileSystemTestCase(test.TestCase):
    def setUp(self, blueprint):
        self.structure = file.Structure(blueprint)

    def tearDown(self):
        self.structure.clean()
    
    def match(self, f: file.File, blueprint: list):
        if f.p.is_dir():
            self.dir_match()
        elif f.p.is_file():
            return f.read() == blueprint

    def dir_match(self, f: file.Dir, blueprint: list):
        if not isinstance(blueprint, list):
            return False 
        comparative = Comparative(list(f.p.iterdir()), blueprint, self.match)
        return comparative.bijection()


class FileTestCase(FileSystemTestCase):
    def setUp(self):
        self.content = 'Content'
        super().setUp([self.content])
        self.f = self.structure.files[0]
        self.p = Path(self.f.name)

    def test_exists(self):
        self.assertTrue(self.p.exists())
    
    def test_is_file(self):
        self.assertTrue(self.is_dir())
    
    def test_content(self):
        with open(self.p) as f:
            self.assertEqual(f.read(), self.content)
        

class DirTestCase(FileSystemTestCase):
    def setUp(self):
        super().setUp([[]])
        self.dir = self.structure.files[0]

    def test_exists(self):
        self.assertTrue(self.dir.p.exists())

    def test_is_dir(self):
        self.assertTrue(self.dir.p.is_dir())


class DirWithFileCase(DirTestCase, FileTestCase):
    def setUp(self):
        super().setUp()
