from __future__ import annotations
import io
from hashlib import md5
from pathlib import Path, PurePath
from typing import Optional, List
from dataclasses import dataclass, field

from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

import obj, path
from googl import api, Service, Query
from relation import Relation


class File:
    FOLDER_MIMETYPE = 'application/vnd.google-apps.folder'
    FIELDS = ['name', 'mimeType', 'id', 'parents']

    def __init__(self, name: Optional[str]=None, mimeType: Optional[str]=None,
                 id: Optional[str]=None, parents: List[str]=None,
                 owners: Optional[List[str]]=None,
                 media_body: Optional[MediaFileUpload]=None):
        self.name = name
        self.mimeType = mimeType
        self.id = id
        self.parents = parents
        self.owners = owners
        self.media_body = media_body
        if self.id: self.get()

    def get(self):
        return api.set(self, Service.files.get(fileId=self.id))

    def create(self) -> File:
        return api.set(self, Service.files.create(body=self.body(),
                                                  media_body=self.media_body))

    def body(self, id=True) -> dict:
        vars = self.__dict__.items()
        if 'owners' in vars and isinstance(vars['owners'], dict):
           vars['owners'] = 'me'
        return {('fileId' if k == 'id' else k): v for k, v in vars \
                if k in self.FIELDS and v and (id or not k == 'id')}

    @staticmethod
    def files(drive_path: PurePath, action: str='list') -> List[File]:
        if path.top_level(drive_path): return [File(id='root')]
        if parents := [f.id for f in File.files(drive_path.parent)]:
            f = File(name=drive_path.name, parents=parents)
            chosen = getattr(f, action)()
            return list(chosen) if hasattr(chosen, '__iter__') else [chosen]
        return []

    @staticmethod
    def list(query) -> List[File]:
        results = []
        pageToken = None
        while pageToken != 'end':
            response = api.request(Service.files.list(q=query, pageSize=1000,
                fields=File.LIST_FIELDS, pageToken=pageToken))
            new_files = response.get('files', [])
            results += new_files
            pageToken = response.get('nextPageToken', 'end')
        return File.__files(results)

    def one(self) -> File:
        return self.first() or self.create()

    def first(self) -> Optional[File]:
        files = self.matches()
        for f in files[1:]: f.delete()
        return obj.set(self, next(iter(files), None))

    def matches(self) -> List[File]:
        return File.list(Query.from_components(self.body(id=False)))

    LIST_FIELDS = f"files({','.join(FIELDS + ['owners'])}),nextPageToken"

    def prefixed(self, pattern: str):
        query_dict = self.body()
        if 'name' in query_dict: query_dict.pop('name')
        files = File.list(Query.from_components(query_dict, pattern=pattern))
        return [f for f in files if f.name.startswith(pattern)]

    @staticmethod
    def __files(responses) -> List[File]:
        return [File(**r) for r in responses]

    def delete(self) -> Optional[str]:
        return self.id and api.request(Service.files.delete(fileId=self.id))

    def content(self) -> bytes:
        request = self.id and Service.files.get_media(fileId=self.id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        return fh.getvalue()

    def equivalent(self, local: Path) -> bool:
        if not self.name == local.name: return False
        if local.is_file():
            return self._equivalent_content(local)
        elif local.is_dir():
            return self._equivalent_dir(local)
        return False
 
    def _equivalent_dir(self, local) -> bool:
        X = File.list(Query.from_components({"parents": [self.id]}))
        Y = list(local.iterdir())
        return Relation(X, Y, File.equivalent).bijection()

    def _equivalent_content(self, local) -> bool:
        with open(local, 'rb') as l:
            return md5(l.read()).hexdigest() \
                == md5(self.content()).hexdigest()

    def delete_by_prefix(self, prefix: str):
        for f in self.matches():
            if f.name.startswith(prefix):
                f.delete()

    @staticmethod
    def print_permissions(folder_id):
        permissions = File.service.permissions().list(fileId=folder_id) \
            .execute()
        for permission in permissions.get('permissions', []):
            print(f"ID: {permission['id']}, Type: {permission['type']}, \
                  Role: {permission['role']}")
