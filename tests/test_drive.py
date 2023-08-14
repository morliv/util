#!/usr/bin/env python3

import drive
import unittest
from pathlib import Path
import tempfile

class TestDrive(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_path = Path(self.test_dir.name)

        self.test_file_path = self.test_path / 'testfile.txt'
        with open(self.test_file_path, 'w') as file:
            file.write('Test sentence')

    
    def tearDown(self):
        self.test_dir.cleanup()


    def sync_test(self, only_contents):
        with self.subTest(only_contents=only_contents):
            only_contents_string = 'only the contents' if only_contents else 'with the directory containg the file'
            drive_folder_name = f"Test {only_contents_string}"
            drive_folder_id = drive.Drive.sync(Path(self.test_path),
                Path(drive_folder_name), only_contents=only_contents)
            manual_check = input(f"Did a folder with name {drive_folder_name} appear in root " +
                "with f{only_contents_string}? y/n")
            self.assertEqual(manual_check, 'y')
            while input("Did you delete the file, and from the trash or" +
                "you'll run again? y/n") != 'y':
                continue
        
    def test_syncs(self):
        for only_contents in [False, True]:
            self.sync_test(only_contents)

    def test_multiple_files(self):
        pass
        

if __name__ == '__main__':
    unittest.main()

