from __future__ import annotations
import io
from hashlib import md5
from functools import partial
from pathlib import Path, PurePath
from typing import Optional, List

from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

import obj
import path
from googl import api, Service, Query


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

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
    @staticmethod
    def folder(drive: Path) -> File:
        folders = File.files(drive)
        if len(folders) != 1 or folders[0] != File.FOLDER_MIMETYPE:
            raise Exception(f'{folders} should be singular & a folder')
        return folders[0]

    def equivalent(local: Path) -> bool:
        if not local.name == self.name: return False
        return File._equivalent_content(local, )

    def _equivalent_content(self, local) -> bool:
        with open(local, 'rb') as l:
            return md5(l.read()).hexdigest() \
                == md5(self.content()).hexdigest()

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
    def files(drive: PurePath, action: str='list') -> List[File]:
        if path.top_level(drive): return [File(id='root')]
        if parents := File.files(drive.parent):
            parent_ids = [f.id for f in parents]
            f = File(name=drive.name, parents=parent_ids)
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

    def prefixed(self, pattern: str):
        query_dict = self.body()
        if 'name' in query_dict: query_dict.pop('name')
        files = File.list(Query.from_components(query_dict, pattern=pattern))
        return [f for f in files if f.name.startswith(pattern)]

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

    @staticmethod
    def __files(responses) -> List[File]:
        return [File(**r) for r in responses]
