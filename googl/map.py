from pathlib import Path
from typing import Callable, List

from googleapiclient.http import MediaFileUpload

import file
from . import api, Files, File


class Map:
    def __init__(self, local: Path, destination: Path=Path('/')):
        self.local = file.File(local, folder_mimetype=api.FOLDER_MIMETYPE)
        self.destination = destination
        self.drive = self._drive()

    def sync(self, action: Callable=File.one):
        action(self.drive)
        self.local.on_subpaths(
            lambda p: Map(local=p, destination=self.destination / p.name) \
                .sync(action))
        return self

    def _drive(self) -> File:
        return File(self.local.p.name, self.local.mimetype,
                    parents=[Files.folder(self.destination).id],
                    media_body=self.__media())

    def __media(self) -> MediaFileUpload:
        return MediaFileUpload(
            str(self.local.p), mimetype=self.local.mimetype) \
            if self.local.p.is_file() else None
