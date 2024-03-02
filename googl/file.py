from __future__ import annotations
import io
from typing import Optional, List

from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from dictionary import removed
import file
from . import Query, api, Response


class File:
    def __init__(self, name: Optional[str]=None, mimeType: Optional[str]=None,
                 id: Optional[str]=None, parents: List[str]=['root'],
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

    def create(self, uploadType=None) -> File:
        uploadType = 'multipart' if self.media_body else 'media'
        return api.set(self, api.files.create(uploadType=uploadType,
            body=self.body(), media_body=self.media_body))

    def body(self) -> dict:
        return {('fileId' if k == 'id' else k): v for k, v \
                in vars(self).items() if k in api.FIELDS and v}

    def one(self) -> File:
        return self.first() or self.create()

    def first(self) -> Optional[File]:
        if len(fs := self.matches()):
            for f in fs[1:]: f.delete()
            return f[0]
        return None

    def matches(self, pattern=None) -> List[File]:
        return [File(**r) for r in \
                Response(Query.build(self.body(), pattern=pattern)).list()]

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
