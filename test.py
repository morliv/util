import tempfile
from pathlib import Path
from typing import Any, Callable
import unittest

from util import obj, file

class TestCase(unittest.TestCase):
    def assertEqualAttributes(self, first: type, second: type, msg: Any = None, ignore=[]) -> None:
        self.assertTrue(obj.eq_attributes(first, second, ignore))
    

class OrderedTestLoader(unittest.TestLoader):
    def getTestCaseNames(self, testCaseClass):
        test_names = super().getTestCaseNames(testCaseClass)
        test_method_order = {name: order for order, name in enumerate(dir(testCaseClass))}
        return sorted(test_names, key=lambda name: test_method_order[name])
