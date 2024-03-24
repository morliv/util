from __future__ import annotations
import io
import magic
from typing import Self
from pathlib import Path, PurePath
from dataclasses import dataclass, field, asdict

from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

import path
import file
from dictionary import gets
from relation import Relation
from . import Query, api, request

FIELDS = {'name', 'mimeType', 'id', 'parents'}
FOLDER_MIMETYPE = 'application/vnd.google-apps.folder'

files = api.drive.files()

def _equal_contents(p: Path, drive: File) -> bool:
    return Relation(list(p.iterdir()), \
        File(parents=[drive.id]).list(), equal).bijection()


def equal(p: Path, drive: File) -> bool:
    return p.name == drive.name \
        and (p.is_dir() == (drive.mimeType == FOLDER_MIMETYPE)) \
        and _equal_contents(p, drive) if p.is_dir() else \
        file.eq_contents(p, [drive], lambda f: File.content(f.id))


@dataclass
class File:
    mimeType: str | None = field(default=None)
    parents: list[str] | None = field(default=None)
    owners: dict | None = field(default=None)
    id: str = field(default=None)
    name: str = field(default=None)

    @staticmethod
    def sync(local: Path, folder: PurePath=PurePath('/')) -> File:
        return File._sync(local, File.at(folder, File.one).id)
    
    @staticmethod
    def _sync(local: Path, parent: str='root') -> File:
        f = File(parents=[parent], name=local.name)
        if local.is_file():
            f.mimeType = magic.from_file(local, mime=True)
            f.one(local)
        if local.is_dir():
            f.mimeType = FOLDER_MIMETYPE
            f.one()
            for s in local.iterdir(): File._sync(s, f.id)
        return f

    def one(self, content: Path=None) -> Self:
        for i, f in reversed(list(enumerate(self.list(content)))):
            if i == 0: self.__dict__ |= f.__dict__; return self
            f.delete()
        return self.create(content)

    def create(self, content: Path=None, uploadType='media') -> Self:
        print(vars(self))
        if content: uploadType = 'multipart'
        self.__dict__ |= api.request(files.create(uploadType=uploadType,
            body=asdict(self), media_body=content and \
                MediaFileUpload(str(content))))
        return self

    @staticmethod
    def at(drive: PurePath=PurePath('/'), action: callable=None) -> \
            list[File] | File | None:
        if not action: action = File.one
        if path.top_level(drive): return File(id='root')
        if parents := File.at(drive.parent, action):
            return action(File(name=drive.name,
                parents=[parents.id] if isinstance(parents, File) \
                else [p.id for p in parents]))
        return None

    def list(self, content: Path=None, pattern=None) -> list[File]:
        fs = [File(**d) for d in File._list(Query.build(asdict(self),
            pattern))]
        if not content: return fs
        with open(content, 'rb') as c:
            return list(filter(lambda f: file.equivalent([c.read(),
                File.content(f.id)]), fs))

    def delete(self):
        self.__dict__ |= request(files.delete(fileId=self.id))
        
    @staticmethod
    def _list(q: Query, pageToken: str=None) -> list[dict]:
        ds, t = gets(File._page(q, pageToken), {'files': [],
                                                'nextPageToken': []})
        return ds + (t and File._list(q, t))

    @staticmethod
    def _page(q: Query, pageToken: str) -> list[dict]:
        FS = f"files({','.join(FIELDS | {'owners'})}),nextPageToken"
        return request(files.list(q=q, fields=FS, pageToken=pageToken))

    @staticmethod
    def content(id) -> bytes | None:
        if int(api.request(files.get(fileId=id, fields='size')) \
               .get('size'), 0) == 0: return None
        fh = io.BytesIO()
        request = files.get_media(fileId=id)
        downloader = MediaIoBaseDownload(fh, request)
        while not downloader.next_chunk()[1]: continue
        return fh.getvalue()

    @staticmethod
    def prefixed(fs: list[File], prefix) -> list[File]:
        return list(filter(lambda f: f.name.startswith(prefix), fs)) 

    @staticmethod
    def delete_by_prefix(fs: list[File], prefix: str):
        for f in fs:
            if f.name.startswith(prefix):
                f.delete()

    @staticmethod
    def permissions(id):
        permissions = File.service.permissions().list(fileId=id).execute()
        for permission in permissions.get('permissions', []):
            print(f"ID: {permission['id']}, Type: {permission['type']}, \
                  Role: {permission['role']}")
