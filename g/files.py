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

from util import dictionary, function, process, obj, path
from util.g import api, Service, Query


class File:
    FOLDER_MIMETYPE = 'application/vnd.google-apps.folder'
    FIELDS = ['name', 'mimeType', 'id', 'parents']
    LIST_FIELDS = f"files({','.join(FIELDS + ['owners'])}),nextPageToken"

    def __init__(self, name: Optional[str]=None, mimeType: Optional[str]=None, id: Optional[str]=None, parents: List[str]=[], owners: List[str]=['me'], media_body: Optional[MediaFileUpload]=None):
        self.name = name
        self.mimeType = mimeType
        self.id = id
        self.parents = parents or ['root']
        self.owners = owners
        self.media_body = media_body

    def get(self):
        return api.set(self, Service.files.get(fileId=self.id))

    def body(self, id=True) -> dict:
        vars = self.__dict__.items()
        if 'owners' in vars and isinstance(vars['owners'], dict):
           vars['owners'] = 'me' 
        return {('fileId' if k == 'id' else k): v for k, v in vars if k in self.FIELDS and v and (id or not k == 'id')}

    def one(self):
        return self.first() or self.create()

    def first(self) -> Optional[File]:
        files = self.matches() 
        for f in files[1:]: f.delete()
        return obj.set(self, next(iter(files), None))

    def matches(self) -> List[File]:
        return File.list(Query.from_components(self.body(id=False)))

    @staticmethod
    def list(query) -> List[File]:
        results = []
        pageToken = None
        while pageToken != 'end':
            response = api.request(Service.files.list(q=query, pageSize=1000, fields=File.LIST_FIELDS, pageToken=pageToken))
            print(f'{pageToken = }\n{query = }\n{response = }\n')
            if not response:
                breakpoint()
            new_files = response.get('files', [])
            results += new_files
            pageToken = response.get('nextPageToken', 'end')
        return File.files(results)

    def prefixed(self, pattern: str):
        query_dict = self.body()
        if 'name' in query_dict: query_dict.pop('name')
        files = File.list(Query.from_components(query_dict, pattern=pattern))
        return [f for f in files if f.name.startswith(pattern)]

    @staticmethod
    def files(responses) -> List(File):
        return [File(**r) for r in responses]

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
    def folders(p: PurePath, action: str='list') -> List[str]:
        if path.top_level(p): return ['root']
        if parents := File.folders(p.parent):
            f = File(name=p.name, parents=parents)
            chosen = getattr(f, action)()
            return list(chosen) if hasattr(chosen, '__iter__') else [chosen]
        return []

    def delete_by_name(self, name: str):
        files = self.matches()
        for f in files:
            if f.name == name:
                f.delete()

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
    def __init__(self, local, drive: Path=Path('/'), action='one'):
        self.local = Path(local)
        self.drive = drive
        mimeType = magic.from_file(str(local), mime=True) if self.local.is_file() else File.FOLDER_MIMETYPE
        media = MediaFileUpload(str(self.local), mimetype=mimeType) if self.local.is_file() else None
        self.file = File(self.local.name, mimeType, media_body=media)
        self.file.parents = File.folders(drive, action)
        self.sync(action)

    def sync(self, action='one'):
        getattr(self.file, action)()
        if self.local.is_dir():
           for p in self.local.iterdir():
               Map(local=p, drive=self.drive / p.name)

    def list(self) -> List[File]:
        equivalent, matching_metadata = [], []
        for f in self.file.list():
            if f.equivalent(): equivalent.append()
            else: matching_metadata.append(f)
        return equivalent.extend(matching_metadata)

    def equivalent(self) -> bool:
        with open(self.local, 'rb') as local_file:
            return hashlib.md5(local_file.read()).hexdigest() == hashlib.md5(self.file.content()).hexdigest()
