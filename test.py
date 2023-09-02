import tempfile
from pathlib import Path
import unittest


class FileTestCase(unittest.TestCase):

    def setUp(self):
        self.file = tempfile.NamedTemporaryFile(mode='w+t')
        self.write()

    def write(self, content='Content'):
        self.content = content
        self.file.write(self.content)
        self.file.flush()

    def tearDown(self):
        self.file.close()


class DirTestCase(unittest.TestCase):
    
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.dir_path = Path(self.dir.name)

    def tearDown(self):
        self.dir.cleanup()


class DirWithFileTestCase(DirTestCase):

    def setUp(self):
        super().setUp()
        self.file_path = self.dir_path / 'testfile.txt'
        with open(self.file_path, 'w') as f:
            f.write('Content')


class OrderedTestLoader(unittest.TestLoader):
    def getTestCaseNames(self, testCaseClass):
        test_names = super().getTestCaseNames(testCaseClass)
        test_method_order = {name: order for order, name in enumerate(dir(testCaseClass))}
        return sorted(test_names, key=lambda name: test_method_order[name])

