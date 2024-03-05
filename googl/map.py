from pathlib import Path
from typing import Callable, List

from googleapiclient.http import MediaFileUpload

import file
from . import api, Files, File


class Map:
    def __init__(self, p: Path, destination: Path=Path('/'), \
                 action: Callable[[File], File | List[File]]=File.one):
        self.local = file.File(p, folder_mimetype=api.FOLDER_MIMETYPE)
        self.destination = destination
        self.drive = action(self._drive())
        if p.is_dir():
            self.submaps = [Map(sub_p, destination / p.name, action) \
                            for sub_p in p.iterdir()]

    def _drive(self) -> File:
        return File(self.local.p.name, self.local.mimetype,
                    parents=[Files.folder(self.destination).id],
                    media_body=self.__media())

    def __media(self) -> MediaFileUpload:
        return MediaFileUpload(
            str(self.local.p), mimetype=self.local.mimetype) \
            if self.local.p.is_file() else None
