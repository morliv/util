import tempfile
from pathlib import Path
from typing import Any
import unittest


class TestCase(unittest.TestCase):
    def assertEqualAttributes(self, first: type, second: type, msg: Any = None) -> None:
        return self.assertEqual(vars(first), vars(second), msg)

class FileTestCase(TestCase):

    def setUp(self):
        self.file = tempfile.NamedTemporaryFile(mode='w+t')
        self.write()

    def write(self, content='Content'):
        self.content = content
        self.file.write(self.content)
        self.file.flush()

    def tearDown(self):
        self.file.close()


class DirTestCase(TestCase):
    
    def setUp(self):
        self.file = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.file.cleanup()


class DirWithFileCase(DirTestCase):
    def setUp(self):
       super().setUp()
       self.files = {'dir': self.file,
                     'file': tempfile.NamedTemporaryFile(dir=self.file.name, delete=False)}


class OrderedTestLoader(unittest.TestLoader):
    def getTestCaseNames(self, testCaseClass):
        test_names = super().getTestCaseNames(testCaseClass)
        test_method_order = {name: order for order, name in enumerate(dir(testCaseClass))}
        return sorted(test_names, key=lambda name: test_method_order[name])

