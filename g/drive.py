#!/usr/bin/env python3

from __future__ import annotations
import argparse
import io
import hashlib
from pathlib import Path
from typing import Optional, List, Callable
from dataclasses import dataclass, field
from itertools import chain
from functools import partial
import copy

import magic
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

from .. import dictionary, function, process, obj
from . import api


def main():
    args = parsed_args()
    drive_folder_path = Path(args.drive_folder)
    if args.list_files:
        Drive.files_in(drive_folder_path)
    else:
        Map(Path(args.source).expanduser(), drive_folder_path)


def parsed_args():
    p = argparse.ArgumentParser()
    for a, k in [(('-l', '--source'), {type: str}),
              (('-d', '--drive_folder'), {type: str}),
              (('-f', '--list-files'), {action: 'store_true'})]:
        p.add_argument(*a, **k)
    return p.parse_args()


class File:
    FIELDS = ['name', 'mimeType', 'fileId', 'parents']
    FIELDS_REQUEST = ','.join(FIELDS)

    def __init__(self, name: Optional[str]=None, mimeType: Optional[str]=None, id: Optional[str]=None, parents: Optional[List[str]]=None, media_body: Optional[MediaFileUpload]=None):
        self.name = name
        self.mimeType = mimeType or Drive.FOLDER_MIMETYPE
        self.parents = parents
        self.id = id
        self.media_body = media_body
        self.one()

    def get(self):
        api.update(self, Drive.files.get(fileId=self.id))

    def single_parent(self, parent) -> dict:
        body = self.body()
        body['parents'] = parent
        return body

    def body(self) -> dict:
        return {'fileId' if k == 'id' else k: v for k, v in self.__dict__.items() if k in self.FIELDS and v}

    def one(self):
        breakpoint()
        api.update(self, File.first(self.list()) or self.create())

    def list(self) -> List[File]:
        responses = []
        for parent in self.parents:
            if response := api.call(Drive.files.list(q=Query.from_dict(self.single_parent(parent)))):
                responses += response.get('files', []) 
        return [obj.sync(self, response) for r in responses]

    @staticmethod
    def first(files: List[File]) -> Optional[File]:
        for f in files[1:]: f.delete()
        return next(iter(files), [])

    def delete(self) -> Optional[str]:
        return self.id and api.call(Drive.files.delete(fileId=self.id))

    def create(self) -> File:
        return api.update(self, Drive.files.create(body=self.body(), media_body=self.media_body))

    def content(self) -> bytes:
        request = self.id and Drive.service.files().get_media(fileId=self.id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        return fh.getvalue()

    @staticmethod
    def folder(path: Path) -> str:
        path = '/' / Path(path)
        return File(name=path.name, parents=[File.folder(path.parent)]).one().id if len(path.parts) > 1 else 'root'


class Map():
    def __init__(self, local, drive: Path=Path('/')):
        self.local = Path(local)
        mimeType = magic.from_file(str(local), mime=True) if self.local.is_file() else Drive.FOLDER_MIMETYPE
        media = MediaFileUpload(str(self.local), mimetype=mimeType) if self.local.is_file() else None
        self.file = File(self.local.name, mimeType, parents=[File.folder(drive)], media_body=media)
        self.sync()

    def sync(self):
        if self.local.is_dir():
            for p in self.local.iterdir(): Map(local=p, drive=self.drive / p.name)

    def list(self) -> List[File]:
        equivalent, matching_metadata = [], []
        for f in self.file.list():
            if f.equivalent(): equivalent.append()
            else: matching_metadata.append(f)
        return equivalent.extend(matching_metadata)

    def equivalent(self) -> bool:
        with open(self.local, 'rb') as local_file:
            return hashlib.md5(local_file.read()).hexdigest() == hashlib.md5(self.file.content()).hexdigest()


class Query:
    class Clause:
        IN_KEYS = ['parents']

        def __init__(self, key, val, op='='):
            self.key: str = str(key)
            self.val: str = str(val)
            self.op: str = 'in' if key in Query.Clause.IN_KEYS else str(op)

        def string(self):
            if self.key in Query.Clause.IN_KEYS: 
                return f"'{self.val}' {self.op} {self.key}"
            return f"{self.key} {self.op} '{self.val}'"

    @staticmethod
    def from_dict(dictionary: dict):
        return Query.query([Query.Clause(k, v) for k, v in dictionary.items()])

    @staticmethod
    def query(clauses: List[Clause], logic_op='and'):
        return f' {logic_op} '.join([clause.string() for clause in clauses])


class Drive:
    FOLDER_MIMETYPE = 'application/vnd.google-apps.folder'

    service = api.service('drive', 3)
    files = service.files()

    @staticmethod
    def print_permissions(folder_id):
        permissions = Drive.service.permissions().list(fileId=folder_id).execute()
        for permission in permissions.get('permissions', []):
            print(f"ID: {permission['id']}, Type: {permission['type']}, Role: {permission['role']}")

    @staticmethod
    def files_in(drive_folder_path: Path):
        drive_folder_path = Path(drive_folder_path)
        file_lists = {}
        for folder_id in File.folder(drive_folder_path):
            print(folder_id)
            file_lists[folder_id] = sorted(Drive.list_file_names_in_folder_by_id(folder_id))
            Drive.print_file_names(file_lists[folder_id])
        return file_lists

    @staticmethod
    def files_in_by_id(folder_id: str, fields: str = 'files(id)') -> List[dict]:
        query = f"'{folder_id}' in parents"
        files = []
        page_token = None
        while True:
            try:
                response = Drive.files.list(q=query, pageSize=1000, fields=fields + ',nextPageToken', pageToken=page_token).execute()
                files += response.get('files', [])
                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break
            except HttpError as e:
                print(f"Error fetching files for folder ID {folder_id}. Error: {e}")
                return []
        return files

    @staticmethod
    def list_file_names_in_folder_by_id(folder_id: str) -> List[str]:
        files = Drive.files_in_by_id(folder_id, 'files(name)')
        return [file['name'] for file in files]

    @staticmethod
    def print_file_names(file_names: List[str]) -> None:
        print("Files in the folder:")
        for name in file_names:
            print(name)
        

if __name__=="__main__":
    main()

