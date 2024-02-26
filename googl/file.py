from __future__ import annotations
import io
from hashlib import md5
from functools import partial
from pathlib import Path, PurePath
from typing import Callable, Optional, List

from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from . import Query, api, Response


class File:
    FOLDER_MIMETYPE = 'application/vnd.google-apps.folder'

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
        return api.set(self, api.files.get(fileId=self.id))

    def create(self) -> File:
        return api.set(self, api.files.create(body=Query.body(vars(self)),
                                           media_body=self.media_body))

    def one(self) -> File:
        return self.first() or self.create()

    def first(self) -> Optional[File]:
        if len(fs := self.matches()):
            for f in fs[1:]: f.delete()
            return f[0]
        return None

    def matches(self, pattern=None) -> List[File]:
        return [File(**r) for r in \
                Response(Query.body(vars(self), {'id'}, pattern)).list()]

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
    def equivalent(self, local: Path) -> bool:
        if not local.name == self.name: return False
        return self._equivalent_content(local)

    def _equivalent_content(self, local) -> bool:
        with open(local, 'rb') as l:
            return md5(l.read()).hexdigest() \
                == md5(self.content()).hexdigest()

    def delete(self) -> Optional[str]:
        return self.id and api.request(api.files.delete(fileId=self.id))

    def content(self) -> bytes:
        request = self.id and api.files.get_media(fileId=self.id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        return fh.getvalue()

    @staticmethod
    def print_permissions(folder_id):
        permissions = File.service.permissions().list(fileId=folder_id) \
            .execute()
        for permission in permissions.get('permissions', []):
            print(f"ID: {permission['id']}, Type: {permission['type']}, \
                  Role: {permission['role']}")
