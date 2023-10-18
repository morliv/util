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
from util.g import drive


class NoLocalTestCase(unittest.TestCase):

    def setUp(self):
        self.folder = drive.File('Test')

    def tearDown(self):
        self.folder.delete() 

    def test_creates_folder(self):
        self.assertIsNotNone(self.folder.get())


class LocalFileTestCase(test.FileTestCase):

    def setUp(self):
        super().setUp()
        self.file_map = self.mapped()

    def mapped(self):
        return drive.Map(self.file.name)

    def tearDown(self):
        super().tearDown()
        self.file_map.file.delete()

    def test_file_update(self):
        self.file.write('Content 2')
        self.assertTrue(self.file_map.equivalent())

    def test_local_and_drive_are_equivalent(self):
        self.assertTrue(self.file_map.equivalent())

    def test_delete(self): 
        self.file_map.file.delete()
        self.assertIsNone(self.file_map.file.get())


class DupTestCase(LocalFileTestCase):
    
    def setUp(self):
        super().setUp()
        self.dup = self.mapped().file
        
    def tearDown(self):
        super().tearDown()
        self.dup.delete()

    def test_list_size_still_1(self):
        self.assertEqual(len(self.file_map.file.list()), 1)


class LocalDirTestCase(test.DirTestCase):
    
    def test_syncs(self):
        drive.Map(self.dir_path)

 
if __name__ == '__main__':
    single_func_from_class = None #or ['test_list_size_still_1', DupTestCase]
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

