#!/usr/bin/env python3

import unittest
from pathlib import Path
import tempfile
import sys
import traceback
import os
import shutil
import copy
import pdb

from util import dictionary, test
from g import File, Map


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
            self.file_map = self.mapped()

        def mapped(self, action='one'):
            return Map(self.file.name, file_action=action)

        def tearDown(self):
            super().tearDown()
            self.file_map.file.delete()
    return FileCase


LocalFileTestCaseMixin = file_case(test.FileTestCase)
LocalDirTestCaseMixin = file_case(test.DirTestCase)

class LocalFileTestCase(LocalFileTestCaseMixin):
    def test_file_update(self):
        self.file.write('Content 2')
        self.assertTrue(self.file_map.equivalent())

    def test_local_and_drive_are_equivalent(self):
        self.assertTrue(self.file_map.equivalent())

    def test_delete(self): 
        self.file_map.file.delete()
        self.assertEqual(self.file_map.file.matches(), [])


class DupTestCase(LocalFileTestCaseMixin):
    def setUp(self):
        super().setUp()
        self.dup = self.mapped("create").file
        
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
        self.assertEqual(vars(self.file_map.file), vars(self.file_map.file.get()))


def to_map(temp_file):
    return Map(temp_file.name)

class LocalDirWithFileTestCase(test.DirWithFileCase):
    def setUp(self):
        super().setUp()
        breakpoint()
        self.dir_maps = self.mapped()

    def mapped(self):
        return dictionary.recursive_map(self.dir['dir'], to_map)
 
    def test_folder(self):
        breakpoint()
        self.assertEqual(vars(self.file), vars(self.dir_maps['dir'].get()))

 
if __name__ == '__main__':
    hierarchy = f'{Path(__file__).stem}'#.DupTestCase' #.test_list_size_2'
    try:
        loader = test.OrderedTestLoader()
        suite = loader.loadTestsFromName(hierarchy)
        unittest.TextTestRunner(failfast=True).run(suite)
    except Exception:
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)

