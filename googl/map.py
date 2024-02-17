from pathlib import Path
from typing import List

from googleapiclient.http import MediaFileUpload

import file
from relation import Relation
from googl import File


class Map:
    def __init__(self, local: Path, destination: Path=Path('/')):
        self.local = file.File(local, folder_mimetype=File.FOLDER_MIMETYPE)
        self.destination = destination
        self.drive = self.file()

    def file(self) -> File:
        return File(self.local.p.name, self.local.mimetype,
                    parents=[File.folder(self.destination).id],
                    media_body=self.__media())
 
    def sync(self, action: str='matches'):
        getattr(self, action)
        file.on_subpaths(
            lambda p: Map(local=p, destination=self.destination / p.name) \
                .sync(action))

    def __media(self) -> MediaFileUpload:
        return MediaFileUpload(
            str(self.local.p), mimetype=self.local.mimetype) \
            if self.local.p.is_file() else None
