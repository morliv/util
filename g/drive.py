from __future__ import annotations
import io
import hashlib
from pathlib import Path, PurePath
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


class Service:
    drive = api.service('drive', 3)
    files = drive.files()

class File:
    FOLDER_MIMETYPE = 'application/vnd.google-apps.folder'
    FIELDS = ['name', 'mimeType', 'id', 'parents']

    def __init__(self, name: Optional[str]=None, mimeType: Optional[str]=None, id: Optional[str]=None, parents: List[str]=[], media_body: Optional[MediaFileUpload]=None):
        self.name = name
        self.mimeType = mimeType or File.FOLDER_MIMETYPE
        self.parents = parents or ['root']
        self.id = id
        self.media_body = media_body

    def get(self):
        return api.set(self, Service.files.get(fileId=self.id))

    def body(self, id=True) -> dict:
        return {('fileId' if k == 'id' else k): v for k, v in self.__dict__.items() if k in self.FIELDS and v and (id or not k == 'id')}

    def one(self):
        return self.first() or self.create()

    def first(self) -> Optional[File]:
        files = self.list() 
        for f in files[1:]: f.delete()
        return obj.set(self, next(iter(files), None))

    def list(self) -> List[File]:
        responses = []
        for parent in self.parents:
            responses += self.children(parent)
        return [obj.set(self, r, anew=True) for r in responses]

    def children(self, parent):
        return Query(self.body(parent, id=False)).list()
                
    def list(self):
        results = []
        pageToken = None
        while pageToken != 'end':
            breakpoint()
            response = api.request(Service.files.list(q=Query(self.body()), pageSize=1000, fields=Query.LIST_FIELDS, pageToken=pageToken))
            results +=  response.get('files', [])
            pageToken = response.get('nextPageToken', 'end')
        return results

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
    def folders(path: PurePath, action: Callable=None) -> Optional[List[File]]:
        
        if action:
            
        return File(name=path.name, parents=[File.folders(path.parent)]).id if len(path.parts) > 1 else 'root'

    @staticmethod
    def list_by_pattern(self, pat: str):
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


class Query(str):
    class Clause(str):
        IN_KEYS = ['parents']

        @classmethod
        def __new__(cls, string):
            return super(Query.Clause, cls).__new__(cls, string)

        @staticmethod
        def from_parts(key, val, op):
            if key in Query.Clause.IN_KEYS: 
                return f"'{val}' {op} {key}"
            return  f"{key} {op} '{val}'"

    LIST_FIELDS = f"files({','.join(File.FIELDS)}),nextPageToken"

    @staticmethod
    def __typical(dictionary: dict, pat, logic_op):
        query = Query.concat([Query.expression(k, v) for k, v in dictionary.items()])
        return Query(f"{query} and name contains {pat}" if pat else query)

    @staticmethod
    def expression(k, v):
        if isintance(v, list):
            return '(' + Query.concat([Clause(f"{k} contains {e}") for e in v], 'or') + ')'
        return Query.from_parts(k, v)
        

    @staticmethod
    def concat(expressions, logic_op='and'):
        return f' {logic_op} '.join(expressions) 

