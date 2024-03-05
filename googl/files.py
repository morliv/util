from __future__ import annotations
from pathlib import Path, PurePath
from typing import Callable, List, Optional

import path
from . import api, File

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
