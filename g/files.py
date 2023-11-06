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
    LIST_FIELDS = f"files({','.join(FIELDS)}),nextPageToken"

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
        files = self.matches() 
        for f in files[1:]:f.delete()
        return obj.set(self, next(iter(files), None))

    def matches(self) -> List[File]:
        return File.list(Query.from_components(self.body(id=False)))

    @staticmethod
    def list(query) -> List[File]:
        results = []
        pageToken = None
        while pageToken != 'end':
            response = api.request(Service.files.list(q=query, pageSize=1000, fields=File.LIST_FIELDS, pageToken=pageToken))
            new_files = response.get('files', [])
            results += new_files
            pageToken = response.get('nextPageToken', 'end')
        return File.files(results)

    @staticmethod
    def prefixed(pat: str, query: Query):
        if not query: query = Query()
        files = File.list(query.from_components(pat=pat))
        return list(filter(lambda s: s.startswith(pat), files))

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
    def folders(p: PurePath, action: Callable=lambda f: f.list) -> List[File]:
        if path.top_level(p): return [File(id='root')]
        if parents := File.folders(p.parent):
            return list(File(name=path.name, parents=parents).action())
        return []

    @staticmethod
    def ids(fs: List[File]):
        return [f.id for f in fs]

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
    def __init__(self, local, drive: Path=Path('/')):
        self.local = Path(local)
        mimeType = magic.from_file(str(local), mime=True) if self.local.is_file() else File.FOLDER_MIMETYPE
        media = MediaFileUpload(str(self.local), mimetype=mimeType) if self.local.is_file() else None
        self.file = File(self.local.name, mimeType, media_body=media)
        self.file.parents = File.ids(File.folders(drive, self.file.one))
        self.sync()

    def sync(self):
        self.file.one()
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

