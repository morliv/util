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

from util import dictionary, function, process, obj
from util.g import api


def main():
    args = parsed_args()
    drive_folder_path = Path(args.drive_folder)
    if args.list_files:
        Service.files(drive_folder_path)
    else:
        Map(Path(args.source).expanduser(), drive_folder_path)


def parsed_args():
    p = argparse.ArgumentParser()
    for a, k in [(('-l', '--source'), {type: str}),
              (('-d', '--drive_folder'), {type: str}),
              (('-f', '--list-files'), {action: 'store_true'})]:
        p.add_argument(*a, **k)
    return p.parse_args()

class Service:
    drive = api.service('drive', 3)
    files = drive.files()

class File:
    FOLDER_MIMETYPE = 'application/vnd.google-apps.folder'
    FIELDS = ['name', 'mimeType', 'id', 'parents']
    REQUEST_FIELDS = ['fileId' if f == 'id' else f for f in FIELDS]
    FIELDS_REQUEST = f"files({','.join(File.FIELDS)})"


    def __init__(self, name: Optional[str]=None, mimeType: Optional[str]=None, id: Optional[str]=None, parents: List[str]=[], media_body: Optional[MediaFileUpload]=None):
        self.name = name
        self.mimeType = mimeType or File.FOLDER_MIMETYPE
        self.parents = parents or ['root']
        self.id = id
        self.media_body = media_body
        self.one()

    def get(self):
        return api.set(self, Service.files.get(fileId=self.id))

    def single_parent(self, parent, request=True) -> dict:
        body = self.request_body() if request else self.body()
        body['parents'] = parent
        return body

    def body(self) -> dict:
        return {'fileId' if k == 'id' else k: v for k, v in self.__dict__.items() if k in self.FIELDS and v}

    def request_body(self) -> dict:
        body = self.body()
        body.pop('fileId', {})
        return body

    def one(self):
        return self.first(self.list()) or self.create()

    def list(self) -> List[File]:
        responses = []
        for parent in self.parents:
            responses += self.children(parent)
        return [obj.set(self, r, anew=True) for r in responses]

    def children(self, parent):
        return Query(self.single_parent(parent, request=True)).list()
                
    def first(self, files: List[File]) -> Optional[File]:
        for f in files[1:]: f.delete()
        return obj.set(self, next(iter(files), None))

    def delete(self) -> Optional[str]:
        return self.id and api.request(Service.files.delete(fileId=self.id))

    def create(self) -> File:
        return api.set(self, Service.files.create(body=self.body(), media_body=self.media_body))

    def content(self) -> bytes:
        request = self.id and Service.files.get_media(fileId=self.id)
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

    @staticmethod
    def files(drive_folder_path: Path=Path('/')):
        drive_folder_path = Path(drive_folder_path)
        file_lists = {}
        for folder_id in File.folder(drive_folder_path):
            file_lists[folder_id] = sorted(File.list_file_names_in_folder_by_id(folder_id))
            File.print_file_names(file_lists[folder_id])
        return file_lists

    @staticmethod
    def list_file_names(folder_id: str) -> List[str]:
        files = Service.files_in_by_id(folder_id, 'files(name)')
        return [file['name'] for file in files]

    @staticmethod
    def list_matching_files(drive_folder_path: Path, pattern: str):
        drive_folder_path = Path(drive_folder_path)
        file_lists = {}
        matching_files = []
        for folder_id in File.folder(drive_folder_path):
            file_lists[folder_id] = sorted(File.list_file_names_in_folder_by_id(folder_id))
            matching_files += [name for name in file_lists[folder_id] if fnmatch(name, pattern + '*')]
        return matching_files

    @staticmethod
    def delete_by_pattern(self, pat: str):
       for response in list_matching_files('root', 'tmp'): File(id=response['id']).delete()

    def delete_by_name(self, name: str):
        files = self.list()
        for file in files:
            if file.name == name:
                file.delete()

    @staticmethod
    def print_file_names(file_names: List[str]) -> None:
        print("Files in the folder:")
        for name in file_names:
            print(name)

    @staticmethod
    def print_permissions(folder_id):
        permissions = File.service.permissions().list(fileId=folder_id).execute()
        for permission in permissions.get('permissions', []):
            print(f"ID: {permission['id']}, Type: {permission['type']}, Role: {permission['role']}")


class Map():
    def __init__(self, local, drive: Path=Path('/')):
        self.local = Path(local)
        mimeType = magic.from_file(str(local), mime=True) if self.local.is_file() else File.FOLDER_MIMETYPE
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

    def __init__(self, obj: type):
        self.string = Query.query(Query.from_dict(vars(obj)))

    @staticmethod
    def list(query):
        responses = []
        pageToken = None
        while pageToken is not 'end':
            responses += api.request(Service.files.list(q=query, pageSize=1000, fields=fields + ',nextPageToken', pageToken=pageToken)).get('files', [])
            pageToken = response.get('nextPageToken', 'end')
        return responses

    @staticmethod
    def from_dict(dictionary: dict):
        return Query.query([Query.Clause(k, v) for k, v in dictionary.items()])

    @staticmethod
    def query(clauses: List[Clause], logic_op='and'):
        return f' {logic_op} '.join([clause.string() for clause in clauses])


if __name__=="__main__":
    main()

