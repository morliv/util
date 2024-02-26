from __future__ import annotations
from pathlib import Path, PurePath
from typing import Callable, List, Optional
from enum import StrEnum, auto

from googleapiclient.http import MediaFileUpload

import path
from . import File

class Files:
    @staticmethod
    def folder(drive: Path) -> File:
        folders = Files.get(drive)
        if len(folders) != 1 or folders[0].mimeType != File.FOLDER_MIMETYPE:
            raise Exception(f'{folders} should be singular & a folder')
        return folders[0]

    @staticmethod
    def get(drive: PurePath=PurePath('/'),
            action: Callable=File.matches) -> List[File]:
        if path.top_level(drive): return [File(id='root')]
        if parents := Files.get(drive.parent):
            return Files(File(name=drive.name,
                              parents=[f.id for f in parents]))._files(action)
        return []

    @staticmethod
    def _files(action: Callable=File.matches) -> List[File]:
        chosen = action()
        return list(chosen) if hasattr(chosen, '__iter__') else [chosen]
    
    @staticmethod
    def prefixed(fs: List[File], prefix) -> List[File]:
        return list(filter(lambda f: f.name.startswith(prefix), fs)) 

    @staticmethod
    def delete_by_prefix(fs: List[File], prefix: str):
        for f in fs:
            if f.name.startswith(prefix):
                f.delete()
