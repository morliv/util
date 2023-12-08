import tempfile
from pathlib import Path
from typing import Any
import unittest

from util import obj

class TestCase(unittest.TestCase):
    
    def assertEqualAttributes(self, first: type, second: type, msg: Any = None, ignore=[]) -> None:
        return self.assertTrue(obj.eq_attributes(first, second, ignore))
 

class FileSystemTestCase(TestCase):
    def setUp(self, file_structure):
        self.structure = self.create_structure(file_structure)

    def tearDown(self):
        self.tearDownStructure()
    
    def tearDownStructure(self, content):
        for name, content in self.structure.items():
            if isinstance(content, dict):
                self.tearDownStructure(content)
            else:
                content.name.unlink()
                content.close()

class FileTestCase(FileSystemTestCase):

    def setUp(self):
        super().setUp({'file': 'Content'})
        

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
