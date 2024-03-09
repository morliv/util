from __future__ import annotations
import io
from typing import Optional, List, Callable
from pathlib import Path, PurePath
from hashlib import md5

from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

import path
from relation import Relation
from . import Query, api, Response


def _equal_content(p: Path, drive: File) -> bool:
    with open(p, 'rb') as l:
        return md5(l.read()).hexdigest() == md5(drive.content()).hexdigest()


def _equal_contents(p: Path, drive: File) -> bool:
    return Relation(list(p.iterdir()), \
        File(parents=[drive.id]).matches(), equal).bijection()


def _equivalency_func(are_dirs: bool) -> Callable:
    return _equal_contents if are_dirs else _equal_content


def equal(p: Path, drive: File) -> bool:
    return p.name == drive.name \
        and (p.is_dir() == (drive.mimeType == api.FOLDER_MIMETYPE)) \
        and _equivalency_func(p.is_dir())(p, drive)


class File:
    def __init__(self, name: Optional[str]=None, mimeType: Optional[str]=None,
                 id: Optional[str]=None, parents: List[str]=['root'],
                 owners: Optional[List[str]]=None):
        self.name = name
        self.mimeType = mimeType
        self.id = id
        self.parents = parents
        self.owners = owners
        if self.id: self.get()

    def get(self):
        return api.set(self, api.files.get(fileId=self.id))

    def create(self, media=None) -> File:
        return api.set(self, api.files.create(uploadType=media and 'multipart',
            body=self.body(), media_body=media))

    @staticmethod
    def load(p: Path, parents: List[str]=['root']):
        f = File(name=p.name, parents=parents)
        return f.one(MediaFileUpload(str(p))) if p.is_file() else f._dir(p)
    
    def _dir(self, p: Path) -> File:
        self.mimeType = api.FOLDER_MIMETYPE
        self.one()
        for s in p.iterdir(): File.load(s, parents=[self.id])
        return self

    def body(self) -> dict:
        return {('fileId' if k == 'id' else k): v for k, v \
                in vars(self).items() if k in api.FIELDS and v}

    def one(self, media: MediaFileUpload=None) -> File:
        if len(fs := self.equivalents()):
            for f in fs[1:]: f.delete()
            return fs[0]
        return self.create(media)

    def equivalents(self) -> List[File]:
        return list(filter(lambda f: self.content() != f.content(), \
            self.matches()))

    def files(self, action: Callable=None) -> List[File]:
        if not action: action = File.matches
        chosen = action(self)
        return list(chosen) if hasattr(chosen, '__iter__') else [chosen]
    
    def matches(self, pattern=None) -> List[File]:
        return [File(**r) for r in \
            Response(Query.build(self.body(), pattern=pattern)).list()]

    def delete(self) -> Optional[str]:
        return self.id and api.request(api.files.delete(fileId=self.id))

    def content(self) -> bytes:
        fh = io.BytesIO()
        request = self.id and api.files.get_media(fileId=self.id)
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
    def get(drive: PurePath=PurePath('/'), action: Callable=File.matches) \
            -> List[File]:
        if path.top_level(drive): return [File(id='root')]
        if parents := Files.get(drive.parent):
            return File(name=drive.name, parents=[f.id for f in parents]) \
                .files(action)
        return []

    @staticmethod
    def prefixed(fs: List[File], prefix) -> List[File]:
        return list(filter(lambda f: f.name.startswith(prefix), fs)) 

    @staticmethod
    def delete_by_prefix(fs: List[File], prefix: str):
        for f in fs:
            if f.name.startswith(prefix):
                f.delete()
