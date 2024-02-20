from pathlib import Path, PurePath
from typing import List, Optional
from enum import StrEnum, auto

from googleapiclient.http import MediaFileUpload

import path
from googl import api, Service, Query, File

class Files:
    Action = StrEnum('Action', {a: auto() for a in ['MATCHES', 'LIST', 'ONE']})

    def __init__(self, start: File=dict()):
        self.q = Files.body(vars(start))
        
    @staticmethod
    def create(body: Query, media_body: MediaFileUpload) -> File:
        return File(**Service.files.create(body=body, media_body=media_body))

    @staticmethod
    def body(d: dict, skip: set=set(), pattern=None, logic_op='and') -> Query:
        if 'owners' in d and isinstance(d['owners'], dict):
           d['owners'] = 'me'
        d = {('fileId' if k == 'id' else k): v for k, v in d \
                if k in Query.FIELDS - skip and v}
        return Query.build(d, pattern, logic_op)
    
    @staticmethod
    def folder(drive: Path) -> File:
        folders = Files.get(drive)
        if len(folders) != 1 or folders[0].mimeType != File.FOLDER_MIMETYPE:
            raise Exception(f'{folders} should be singular & a folder')
        return folders[0]

    @staticmethod
    def get(drive: PurePath=PurePath('/'), action: str='matches') -> \
            List[File]:
        if path.top_level(drive): return [File(id='root')]
        if parents := Files.get(drive.parent):
            return Files(File(name=drive.name,
                              parents=[f.id for f in parents]))._files(action)
        return []

    def _files(self, action: str='matches'):
        chosen = getattr(self, action)()
        return list(chosen) if hasattr(chosen, '__iter__') else [chosen]

    def matches(self, prefix: str=None) -> List[File]:
        skip = {'id'}
        if prefix: skip |= 'name'
        files = Files(Query.body(self, skip, pattern=prefix)).list()
        return list(filter(lambda f: f.name.startswith(prefix), files)) \
            if prefix else files

    def list(self) -> List[File]:
        results = []
        pageToken = None
        while pageToken != 'end':
            files, pageToken = self._list_page(pageToken)
            results += files
        return [File(**r) for r in results]

    def one(self) -> File:
        return self.first() or self.create()

    def first(self) -> Optional[File]:
        if len(files := self.matches()):
            for f in files[1:]: f.delete()
            return f[0]
        return None

    def _list_page(self, pageToken: str='end'):
        LISTING = f"files({','.join(Query.FIELDS | ['owners'])}),nextPageToken"
        response = api.request(Service.files.list(q=self, pageSize=1000,
            fields=LISTING, pageToken=pageToken))
        return response['files'], response['nextPageToken']

    def delete_by_prefix(self, prefix: str):
        for f in self.matches():
            if f.name.startswith(prefix):
                f.delete()
