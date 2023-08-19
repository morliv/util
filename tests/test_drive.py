#!/usr/bin/env python3

import drive
import unittest
from pathlib import Path
import tempfile
import pdb
import sys
import traceback


class TestCRUD(unittest.TestCase):

    def setUp(self):
        with tempfile.NamedTemporaryFile(mode='w+t') as file:
            file.write('Content')
            file.flush()
            drive_file = drive.File(Path(file.name), parent_file_ids=['root'])
            self.file_id = drive.Drive.try_write(drive_file)
    
    def test_exists(self):
        self.assertTrue(self.exists(self.file_id))
        self.delete_in_test()

    def exists(file_id: str) -> bool:
        try:
            Drive.files.get(fileId=file_id).execute()
            return True
        except HttpError as e:
            if e.resp.status == 404:
                return False
            raise

    def test_delete(self):
        self.delete_in_test()
        self.assertFalse(drive.Drive.exists(self.file_id))

    def delete_in_test(self):
        try:
            drive.Drive.try_delete(self.file_id)
        except AssertionError:
            print("Delete and empty from trash any files created in Drive")
            raise


class TestSync(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_path = Path(self.test_dir.name)
        self.test_file_path = self.test_path / 'testfile.txt'
        with open(self.test_file_path, 'w') as file:
            file.write('Content')
    
    def tearDown(self):
        self.test_dir.cleanup()

    def sync_test(self, only_contents):
        with self.subTest(only_contents=only_contents):
            only_contents_string = 'only the contents' if only_contents else 'with the directory containg the file'
            drive_folder_name = f"Test {only_contents_string}"
            drive_folder_id = drive.Drive.sync(Path(self.test_path),
                Path(drive_folder_name), only_contents=only_contents)
            manual_check = input(f"Did a folder with name {drive_folder_name} appear in root " +
                f"with {only_contents_string}? y/n")
            self.assertEqual(manual_check, 'y')
        
    def test_syncs(self):
        for only_contents in [False, True]:
            self.sync_test(only_contents)

    def test_multiple_files(self):
        pass       
        while input("Did you delete the folders and from the trash, or you'll run again? y/n") != 'y':
            continue

        
if __name__ == '__main__':
    try:
        TestCRUD('test_write').debug()
    except Exception:
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)

