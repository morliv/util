from __future__ import annotations
import io
import magic
from functools import partial
from typing import Self
from pathlib import Path, PurePath
from dataclasses import dataclass, field, asdict

from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

import l
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
        return File._sync(local, l.one(File.at(folder), File.create,
                                       File.delete).id)
    
    @staticmethod
    def _sync(local: Path, parent: str='root') -> File:
        f = File(parents=[parent], name=local.name)
        if local.is_file():
            f.mimeType = magic.from_file(local, mime=True)
            with open(local, 'rb') as c:
                return l.one(sorted(f.list(), key=
                        lambda f: file.eq([c.read(), File.content(f.id)]),
                        reverse=True),
                    partial(f.create, MediaFileUpload(str(local))),
                    File.delete)
        if local.is_dir():
            f.mimeType = FOLDER_MIMETYPE
            f = l.one(f.list(), f.create, f.delete)
            for s in local.iterdir(): File._sync(s, f.id)
        return f

    def create(self, media_body: MediaFileUpload=None, uploadType='media') \
            -> Self:
        print(vars(self))
        if media_body: uploadType = 'multipart'
        self.__dict__ |= api.request(files.create(uploadType=uploadType,
            body=asdict(self), media_body=media_body))
        return self

    @staticmethod
    def at(drive=PurePath('/')) -> list[File] | None:
        drive = PurePath(drive)
        if path.top_level(drive): return [File(id='root')]
        if parents := [f.id for f in File.at(drive.parent)]:
            return File(parents=parents, name=drive.name).list()
        return None

    def delete(self):
        self.__dict__ |= request(files.delete(fileId=self.id))
        
    def list(self, pattern=None) -> list[File]:
        return [File(**d) for d in File._list(Query.build(asdict(self),
            pattern))]

    @staticmethod
    def _list(q: Query, pageToken: str=None) -> list[dict]:
        ds, t = gets(File._page(q, pageToken), {'files': [],
                                                'nextPageToken': []})
        return ds + (t and File._list(q, t))

    @staticmethod
    def _page(q: Query, pageToken: str) -> list[dict]:
        return request(files.list(q=q, fields=("files(" \
            + ','.join(File.__dataclass_fields__.keys()) + "),nextPageToken"),
            pageToken=pageToken))

    @staticmethod
    def content(id: str) -> bytes:
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
