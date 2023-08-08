#!/usr/bin/env python3

import argparse
import io
import hashlib
from pathlib import Path
from typing import Optional, List, Set
from dataclasses import dataclass
from itertools import chain
from functools import partial

import magic
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

import processing
import google_api


def main():
    args = parsed_args()
    Drive.sync(Path(args.local_path).expanduser(), Path(args.drive_folder), args.only_contents)


def parsed_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--local_path', type=str)
    parser.add_argument('-d', '--drive_folder', type=str)
    parser.add_argument('-o', '--only_contents', action='store_true')
    return parser.parse_args()


@dataclass
class Metadata:
    mimeType: str
    parents: List[str]
    name: str

    def __post_init__(self):
        self.parents = list(self.parents)

    def query(self, parent_file_id):
        query_dict = vars(self)
        query_dict['parents'] = parent_file_id
        return Query.from_dict(query_dict)

    def matches_in_parents(self) -> Set[str]:
        return set(chain.from_iterable(map(lambda parent_file_id: self.matches(parent_file_id), self.parents)))

    def matches(self, parent_file_id: str) -> Set[str]:
        return set(map(lambda id_dict: id_dict['id'], Drive.files.list(q=self.query(parent_file_id), fields='files(id)').execute().get('files', [])))


class Query:
    class Clause:
        def __init__(self, key, val, op='='):
            self.key: str = str(key) 
            self.val: str = str(val)
            self.op: str = 'in' if key == 'parent_file_id' else str(op)

        def string(self):
            if self.key == 'parent_file_id':
                return f"'{self.val}' {self.op} {self.key}"
            return f"{self.key} {self.op} '{self.val}'"

    @staticmethod  
    def from_dict(dictionary: dict):
        return Query.query([Query.Clause(key, value) for key, value in dictionary.items()])

    @staticmethod
    def query(clauses: List[Clause], logic_op='and'):
        return f' {logic_op} '.join([clause.string() for clause in clauses])


class File:
    def __init__(self, parent_file_ids, file_path, mimeType=None):
        self.mimeType = mimeType if mimeType else magic.from_file(str(file_path), mime=True)
        self.parent_file_ids = parent_file_ids
        self.file_path = file_path
        self.metadata = Metadata(self.mimeType, self.parent_file_ids, self.file_path.name)

    def equivalents(self) -> Set[str]:
        file_ids_of_equivalents = set()
        for file_id in self.metadata.matches_in_parents():
            if Drive.equivalent(self.file_path, file_id):
                file_ids_of_equivalents.add(file_id)
        return file_ids_of_equivalents


class Drive:
    FOLDER_MIMETYPE = 'application/vnd.google-apps.folder'

    service = google_api.service('drive', 3)
    files = service.files()

    @staticmethod
    def sync(file_path: Path, drive_folder: Path, only_contents=False) -> str:
        drive_folder_id = Drive.keep_first(list(Drive.obtain_folders(drive_folder)))
        sync_parameterized = partial(Drive.sync, drive_folder=drive_folder if only_contents else
        drive_folder / file_path.name, only_contents=only_contents)
        if file_path.is_dir():
            processing.recurse_on_subpaths(sync_parameterized, file_path)
            return drive_folder_id

        file_for_drive = File({drive_folder_id}, file_path)
        equivalent_file_ids = file_for_drive.equivalents()
        for file_id in file_for_drive.metadata.matches(drive_folder_id) - equivalent_file_ids: Drive.try_delete(file_id)
        if equivalent_file_ids:
            return Drive.keep_first(list(equivalent_file_ids))
        return Drive.try_write(file_for_drive)

    @staticmethod
    def try_write(file_for_drive: File) -> str:
        try:
            Drive.write(file_for_drive)            
        except HttpError as error:
            print(f'An error occurred: {error}')

    @staticmethod
    def write(file_for_drive: File) -> str:
        media = MediaFileUpload(str(file_for_drive.file_path),
        mimetype=file_for_drive.mimeType)
        file_id = Drive.files.create(body=vars(file_for_drive.metadata),
                                      media_body=media,
                                      fields='id').execute().get("id")
        return file_id

    @staticmethod
    def obtain_folders(path: Path) -> Optional[Set[str]]:
        path = '/' / path
        if len(path.parts) == 1:
            return {'root'}
        folder = File(list(Drive.obtain_folders(path.parent)), path, Drive.FOLDER_MIMETYPE)
        folder_ids = folder.metadata.matches_in_parents()
        if not folder_ids:
            folder_ids = [Drive.files.create(body=vars(folder.metadata), fields='id').execute()['id']]
        return folder_ids

    @staticmethod
    def print_permissions(folder_id):
        permissions = Drive.service.permissions().list(fileId=folder_id).execute()
        for permission in permissions.get('permissions', []):
            print(f"ID: {permission['id']}, Type: {permission['type']}, Role: {permission['role']}")

    @staticmethod
    def file_content(file_id: str) -> bytes:
        request = Drive.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        return fh.getvalue()

    @staticmethod
    def equivalent(local_file_path: Path, file_id: str) -> bool:
        google_file_content = Drive.file_content(file_id)
        with open(local_file_path, 'rb') as local_file:
            local_file_content = local_file.read()
        google_file_md5 = hashlib.md5(google_file_content).hexdigest()
        local_file_md5 = hashlib.md5(local_file_content).hexdigest()
        return google_file_md5 == local_file_md5

    @staticmethod
    def keep_first(file_ids: List[str]) -> str:
        for file_id in file_ids[1:]:
            Drive.try_delete(file_id)
        return file_ids[0]
 
    @staticmethod
    def try_delete(file_id: str):
        try:
           Drive.files.delete(fileId=file_id).execute() 
        except HttpError as e:
            print(e)


if __name__=="__main__":
    main()

