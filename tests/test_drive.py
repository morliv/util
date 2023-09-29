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

from googleapiclient.errors import HttpError

import drive
import test


class NoLocalTestCase(unittest.TestCase):

    def setUp(self):
        self.folder = drive.File('Test').create()

    def tearDown(self):
        self.folder.delete() 

    def test_creates_folder(self):
        self.assertIsNotNone(self.folder.get())


class LocalFileTestCase(test.FileTestCase):

    def setUp(self):
        super().setUp()
        self.file_map = self.mapped()

    def mapped(self):
        breakpoint()
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
        self.dups = [self.mapped().file for i in range(2)]
        
    def tearDown(self):
        super().tearDown()
        for dup in self.dups: dup.delete()

    def test_first_dup_in_drive(self):
        self.assertIsNotNone(self.dups[0].get())

    def test_second_dup_in_drive(self):
        self.assertIsNotNone(self.dups[1].get())

    def one_test(self):
        return self.dups[0].one()

    def test_one_keeps_dup_1(self):
        self.one_test()
        self.assertIsNotNone(self.dups[0].get())

    def test_one_deletes_dup_2(self):
        self.one_test()
        self.assertIsNone(self.dups[1].get())


class LocalDirTestCase(test.DirTestCase):
    
    def test_syncs(self):
        drive.Map(self.dir_path)

 
if __name__ == '__main__':
    single_func_from_class = ['test_one_deletes_dup_2', DupTestCase]
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

