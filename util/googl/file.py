from __future__ import annotations
import io
import magic
from functools import partial
from typing import Self
from pathlib import Path, PurePath
from dataclasses import dataclass, field

from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from util import l, path, file
from util.dictionary import gets
from util.relation import Relation
from . import Query, api, request


FOLDER_MIMETYPE = 'application/vnd.google-apps.folder'

files = api.drive.files()

def _equal_contents(p: Path, drive: File) -> bool:
    return Relation(list(p.iterdir()), \
        File(parents=[drive['id']]).match(), equal).bijection()


def equal(p: Path, drive: File) -> bool:
    return p.name == drive['name'] \
        and (p.is_dir() == (drive['mimeType'] == FOLDER_MIMETYPE)) \
        and _equal_contents(p, drive) if p.is_dir() else \
        file.eq_contents(p, [drive], File.content)


class File(dict):
    @staticmethod
    def sync(local: Path, folder: PurePath=PurePath('/')) -> File:
        return File._sync(local, File.at(folder)['id'])
  
    @staticmethod
    def _sync(local: Path, parent: str='root') -> File:
        f = File(parents=[parent], name=local.name)
        if local.is_file():
            f['mimeType'] = magic.from_file(local, mime=True)
            with open(local, 'rb') as c:
                return l.one(sorted(f.match(), key=
                        lambda f: file.eq([c.read(), f.content()]),
                        reverse=True),
                    partial(f.create, MediaFileUpload(str(local))),
                    File.delete)
        if local.is_dir():
            f['mimeType'] = FOLDER_MIMETYPE
            f = l.one(f.match(), f.create, f.delete)
            for s in local.iterdir(): File._sync(s, f['id'])
        return f

    @staticmethod
    def at(drive=PurePath('/')) -> File:
        drive = PurePath(drive)
        if path.top_level(drive): return File(id='root')
        f = File(parents=[File.at(drive.parent)['id']], name=drive.name)
        return l.one(f.match(), f.create, f.delete)

    def create(self, media_body: MediaFileUpload=None, uploadType='media') \
            -> File:
        print(vars(self))
        if media_body: uploadType = 'multipart'
        return api.request(files.create(uploadType=uploadType,
            body=self, media_body=media_body))

    def delete(self):
        request(files.delete(fileId=self['id']))
        
    def match(self, attrs: set[str]=None, pattern=None) -> list[File]:
        if not attrs: attrs = set(self.keys()) | {'mimeType', 'id', 'name'}
        return File.list(Query.build(self, pattern), attrs)

    @staticmethod
    def list(q: Query, attrs: set[str]=None, pageToken: str=None) \
            -> list[File]:
        r, pageToken = gets(request(files.list(q=q, fields= \
            f"files({','.join(attrs)}),nextPageToken", pageToken=pageToken)),
            {'files': [], 'nextPageToken': []})
        return [File(r) for r in
            r + (pageToken and File.list(q, attrs, pageToken))]

    def content(self) -> bytes | None:
        if int(api.request(files.get(fileId=self['id'], fields='size')) \
               .get('size'), 0) == 0: return None
        fh = io.BytesIO()
        request = files.get_media(fileId=self['id'])
        downloader = MediaIoBaseDownload(fh, request)
        while not downloader.next_chunk()[1]: continue
        return fh.getvalue()

    def permissions(self):
        permissions = File.service.permissions().list(fileId=self.id).execute()
        for permission in permissions.get('permissions', []):
            print(f"ID: {permission['id']}, Type: {permission['type']}, \
                  Role: {permission['role']}")
