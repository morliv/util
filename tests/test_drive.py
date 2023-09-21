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


class FileTestCase(unittest.TestCase):

    def test_clean(self):
        self.assertEqual(drive.File()._clean(), {})

    def test_only_one_creates_file(self):
        mapped = drive.Map(Path(self.file.name))
        self.assertTrue(mapped.only_one().equivalent())

class MapTestCase(test.FileTestCase):
    
    def setUp(self):
        super().setUp()
        self.dups = [self.file_to_drive() for i in range(2)]

    def file_to_drive(self):
        return drive.Map(Path(self.file.name), drive.File()).write()

    def tearDown(self):
        super().tearDown()
        self.delete_drive_files() 

    def delete_drive_files(self):
        try:
            for dup in self.dups: dup.file.delete()
        except Exception:
            print("Delete and empty from trash any files created in Drive")
            raise

    def test_local_and_drive_are_equivalent(self):
        self.assertTrue(self.dups[0].equivalent())

    def test_delete(self):
        self.delete_drive_files()
        self.assertIsNone(self.dups[0].file.get())

    def test_first_dup_in_drive(self):
        self.assertIsNotNone(self.dups[0].file.get())

    def test_second_dup_in_drive(self):
        self.assertIsNotNone(self.dups[1].file.get())

    def only_one_test(self):
        self.dups[0].only_one()

    def test_only_one_keep_dup_1(self):
        self.only_one_test()
        self.assertIsNotNone(self.dups[0].file.get())

    def test_only_one_deletes_dup_2(self):
        self.only_one_test()
        self.assertIsNone(self.dups[1].file.get())

    def test_sync_file(self):
        self.file.write('Content 2')
        self.assertTrue(self.dups[0].sync().equivalent())


class LocalDirTestCase(test.DirTestCase):
    
    def test_syncs(self):
        drive.Map(self.dir_path).sync()

 
if __name__ == '__main__':
    try:
        loader = test.OrderedTestLoader()
        suite = loader.loadTestsFromModule(sys.modules[__name__])
        unittest.TextTestRunner(failfast=True).run(suite)
    except Exception:
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)

