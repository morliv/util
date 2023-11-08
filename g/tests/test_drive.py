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

from util import test
from g import File, Map


class NoLocalTestCase(unittest.TestCase):

    def setUp(self):
        self.folder = File('Test').one()

    def tearDown(self):
        self.folder.delete() 

    def test_creates_folder(self):
        self.assertIsNotNone(self.folder.get())


class LocalFileCase(test.FileTestCase):
    def setUp(self):
        super().setUp()
        self.file_map = self.mapped()

    def mapped(self):
        return Map(self.file.name)

    def tearDown(self):
        super().tearDown()
        self.file_map.file.delete()


class LocalFileTestCase(LocalFileCase):
    def test_file_update(self):
        self.file.write('Content 2')
        self.assertTrue(self.file_map.equivalent())

    def test_local_and_drive_are_equivalent(self):
        self.assertTrue(self.file_map.equivalent())

    def test_delete(self): 
        self.file_map.file.delete()
        self.assertEqual(self.file_map.file.matches(), [])


class DupTestCase(LocalFileCase):
    def setUp(self):
        super().setUp()
        self.dup = self.mapped().file
        self.dup.create()
        
    def tearDown(self):
        super().tearDown()
        self.dup.delete()

    def test_list_size_2(self):
        self.assertEqual(len(self.dup.matches()), 2)

    def test_one(self):
        self.dup.one()
        self.assertEqual(len(self.dup.matches()), 1)


class LocalDirTestCase(test.DirTestCase):
    
    def test_syncs(self):
        Map(self.dir_path)

 
if __name__ == '__main__':
    single_func_from_class = None #or ['test_delete', LocalFileTestCase]
    try:
        if single_func_from_class:
            suite = unittest.TestLoader().loadTestsFromName(*single_func_from_class)
        else:
            loader = test.OrderedTestLoader()
            suite = loader.loadTestsFromModule(sys.modules[__name__])
        unittest.TextTestRunner(failfast=True).run(suite)
    except Exception:
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)

