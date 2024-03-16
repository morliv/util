from __future__ import annotations
import io
import magic
from typing import Self
from pathlib import Path, PurePath
from hashlib import md5

from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

import path
import file
import obj
from relation import Relation
from . import Query, api, Response


def _equal_contents(p: Path, drive: File) -> bool:
    return Relation(list(p.iterdir()), \
        File(parents=[drive.id]).matches(), equal).bijection()


def equal(p: Path, drive: File) -> bool:
    return p.name == drive.name \
        and (p.is_dir() == (drive.mimeType == api.FOLDER_MIMETYPE)) \
        and _equal_contents(p, drive) if p.is_dir() else \
        file.content_equivalents(p, [drive], lambda f: File.content(f.id))


class File:
    def __init__(self, name: str | None=None, mimeType: str | None=None,
                 id: str | None=None, parents: list[str]=['root'],
                 owners: list[str] | None=None, p: Path=None):
        self.name = name or p.name if p else None
        self.mimeType = mimeType or (p and (api.FOLDER_MIMETYPE if p.is_dir() \
                else magic.from_file(p, mime=True)))
        self.id = id
        self.parents = parents
        self.owners = owners
        self.p = p 
        if id: self.get()
        if p: self.one()

    def get(self) -> Self:
        return api.set(self, api.files.get(fileId=self.id))
    
    def one(self) -> Self:
        if len(fs := self.matches()):
            for f in fs[1:]: f.delete()
            f = obj.update(self, fs[0])
            print(vars(f))
            return f.recurse()
        f = self.create()
        print(vars(f))
        return f

    def matches(self, pattern=None) -> list[File]:
        metadata_matches = [File(**r) for r in Response(Query.build(
            self.body(), pattern=pattern)).list()]
        if self.p and self.p.is_file():
            return file.content_equivalents(self.p, metadata_matches, \
                                            lambda f: File.content(f.id))
        return metadata_matches

    def recurse(self) -> Self:
        if self.p and self.p.is_dir():
            for s in self.p.iterdir(): File(p=s, parents=[self.id]).one()
        return self

    def create(self) -> Self:
        if not self.p or self.p.is_dir():
            self._create()
        elif self.p.is_file():
            self._create('multipart', MediaFileUpload(str(self.p)))
        return self.recurse()

    def _create(self, uploadType=None, media: MediaFileUpload=None) -> Self:
        return api.set(self, api.files.create(uploadType=uploadType,
            body=self.body(), media_body=media))

    def body(self) -> dict:
        return {('fileId' if k == 'id' else k): v for k, v \
                in vars(self).items() if k in api.FIELDS and v}

    def files(self, action: callable=None) -> list[File]:
        if not action: action = File.matches
        chosen = action(self)
        return list(chosen) if hasattr(chosen, '__iter__') \
            else [chosen]
    
    def delete(self) -> str | None:
        return self.id and api.request(api.files.delete(fileId=self.id))

    @staticmethod
    def content(id) -> bytes:
        if int(api.request(api.files.get(fileId=id, fields='size')) \
               .get('size'), 0) == 0: return None
        fh = io.BytesIO()
        request = api.files.get_media(fileId=id)
        downloader = MediaIoBaseDownload(fh, request)
        while not downloader.next_chunk()[1]: continue
        return fh.getvalue()

    @staticmethod
    def permissions(id):
        permissions = File.service.permissions().list(fileId=id).execute()
        for permission in permissions.get('permissions', []):
            print(f"ID: {permission['id']}, Type: {permission['type']}, \
                  Role: {permission['role']}")


class Files:
    @staticmethod
    def folder(drive: Path) -> File:
        folders = Files.get(drive, File.one)
        if len(folders) != 1 or folders[0].mimeType != api.FOLDER_MIMETYPE:
            raise Exception(f'{folders} should be singular & a folder')
        return folders[0]

    @staticmethod
    def get(drive: PurePath=PurePath('/'), action: callable=File.matches) \
            -> list[File]:
        if path.top_level(drive): return [File(id='root')]
        if parents := Files.get(drive.parent):
            return File(name=drive.name, parents=[f.id for f in parents]) \
                .files(action)
        return []

    @staticmethod
    def prefixed(fs: list[File], prefix) -> list[File]:
        return list(filter(lambda f: f.name.startswith(prefix), fs)) 

    @staticmethod
    def delete_by_prefix(fs: list[File], prefix: str):
        for f in fs:
            if f.name.startswith(prefix):
                f.delete()
