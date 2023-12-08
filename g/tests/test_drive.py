#!/usr/bin/env python3

import unittest
from pathlib import Path
import tempfile
import sys
import os
import shutil
import copy

from util import dictionary, test, error, iterable
from g import File, Map


def main():
    hierarchy = f'{Path(__file__).stem}'#.DupTestCase' #.test_list_size_2' loader = test.OrderedTestLoader() suite = loader.loadTestsFromName(hierarchy) unittest.TextTestRunner(failfast=True).run(suite)
    loader = test.OrderedTestLoader()
    suite = loader.loadTestsFromName(hierarchy)
    unittest.TextTestRunner(failfast=True).run(suite)


class NoLocalTestCase(unittest.TestCase):

    def setUp(self):
        self.folder = File('Test').one()

    def tearDown(self):
        self.folder.delete() 

    def test_creates_folder(self):
        self.assertIsNotNone(self.folder.get())


def file_case(test_case):
    class FileCase(test_case):
        def setUp(self):
            super().setUp()
            self.map = Map(self.file.name)

        def tearDown(self):
            super().tearDown()
            self.map.file.delete()
    return FileCase


LocalFileTestCaseMixin = file_case(test.FileTestCase)
LocalDirTestCaseMixin = file_case(test.DirTestCase)

class LocalFileTestCase(LocalFileTestCaseMixin):

    def test_file_update(self):
        self.file.write('Content 2')
        self.assertTrue(self.map.equivalent())

    def test_local_and_drive_are_equivalent(self):
        self.assertTrue(self.map.equivalent())

    def test_delete(self): 
        self.map.file.delete()
        self.assertEqual(self.map.file.matches(), [])


class DupTestCase(LocalFileTestCaseMixin):

    def setUp(self):
        super().setUp()
        self.dup = Map(self.file.name, action="create").file
        
    def tearDown(self):
        super().tearDown()
        self.dup.delete()

    def test_list_size_2(self):
        self.assertEqual(len(self.dup.matches()), 2)

    def test_one(self):
        self.dup.one()
        self.assertEqual(len(self.dup.matches()), 1)


class LocalDirTestCase(LocalDirTestCaseMixin):
    
    def test_match(self):
        self.assertEqualAttributes(self.map.file, self.map.file.get())


def identical(p, f: File):
    if p.is_file():
        return identical_file(p, f)
    if bijection := iterable.Comparative(p.iterdir(), f.parents, identical_file).bijection():
        return all(identical(sub_p, sub_f) for sub_p, sub_f in bijection)
    return False

def identical_file(p: Path, id: str):
    f = File(id)
    with open(p) as local:
        return p.name == f.name and local.read() == f.content()


class LocalDirWithFileTestCase(test.DirWithFileCase):
    def setUp(self):
        breakpoint()
        super().setUp()
        self.map = Map(self.file.name)

    def test_local_matches_drive(self):
        self.assertTrue(identical(self.file, self.map.file))
 
if __name__ == '__main__':
    error.react(main)
