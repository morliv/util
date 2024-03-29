from __future__ import annotations
import io
import magic
from functools import partial
from typing import Self
from pathlib import Path, PurePath
from dataclasses import dataclass, field

from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

import l
import path
import file
from dictionary import gets
from relation import Relation
from . import Query, api, request


FOLDER_MIMETYPE = 'application/vnd.google-apps.folder'

files = api.drive.files()

def _equal_contents(p: Path, drive: File) -> bool:
    return Relation(list(p.iterdir()), \
        File(parents=[drive.id]).match(), equal).bijection()


def equal(p: Path, drive: File) -> bool:
    return p.name == drive.name \
        and (p.is_dir() == (drive.mimeType == FOLDER_MIMETYPE)) \
        and _equal_contents(p, drive) if p.is_dir() else \
        file.eq_contents(p, [drive], lambda f: f.content())


class File(dict):
    @staticmethod
    def sync(local: Path, folder: PurePath=PurePath('/')) -> File:
        return File._sync(local, l.one(File.at(folder), File.create,
                                       File.delete))
    
    @staticmethod
    def _sync(local: Path, parent: str='root') -> File:
        f = File(parents=[parent], name=local.name)
        if local.is_file():
            f.mimeType = magic.from_file(local, mime=True)
            with open(local, 'rb') as c:
                return l.one(sorted(f.match(), key=
                        lambda f: file.eq([c.read(), f.content()]),
                        reverse=True),
                    partial(f.create, MediaFileUpload(str(local))),
                    File.delete)
        if local.is_dir():
            f.mimeType = FOLDER_MIMETYPE
            f = l.one(f.match(), f.create, f.delete)
            for s in local.iterdir(): File._sync(s, f.id)
        return f

    def create(self, media_body: MediaFileUpload=None, uploadType='media') \
            -> Self:
        print(vars(self))
        if media_body: uploadType = 'multipart'
        self.__dict__ |= api.request(files.create(uploadType=uploadType,
            body=self, media_body=media_body))
        return self

    @staticmethod
    def at(drive=PurePath('/')) -> list[File] | None:
        drive = PurePath(drive)
        if path.top_level(drive): return [File(id='root')]
        if parents := [f['id'] for f in File.at(drive.parent)]:
            return File(parents=parents, name=drive.name).match()
        return None

    def delete(self):
        request(files.delete(fileId=self['id']))
        
    def match(self, attrs: set[str]=None, pattern=None) -> list[File]:
        if not attrs: attrs = set(self.keys()) | {'id'}
        return File.list(Query.build(self, pattern), attrs)

    @staticmethod
    def list(q: Query, attrs: set[str]=None, pageToken: str=None) \
            -> list[File]:
        r, pageToken = gets(request(files.list(q=q, fields= \
            f"files({','.join(attrs)}),nextPageToken", pageToken=pageToken)),
            {'files': [], 'nextPageToken': []})
        return r + (pageToken and File._list(q, attrs, pageToken))

    def content(self) -> bytes | None:
        if int(api.request(files.get(fileId=self.id, fields='size')) \
               .get('size'), 0) == 0: return None
        fh = io.BytesIO()
        request = files.get_media(fileId=self.id)
        downloader = MediaIoBaseDownload(fh, request)
        while not downloader.next_chunk()[1]: continue
        return fh.getvalue()

    @staticmethod
    def prefixed(fs: list[File], prefix) -> list[File]:
        return list(filter(lambda f: f.name.startswith(prefix), fs)) 

    @staticmethod
    def delete_by_prefix(fs: list[File], prefix: str):
        for f in fs:
            if f.name.startswith(prefix): f.delete()

    def permissions(self):
        permissions = File.service.permissions().list(fileId=self.id).execute()
        for permission in permissions.get('permissions', []):
            print(f"ID: {permission['id']}, Type: {permission['type']}, \
                  Role: {permission['role']}")
