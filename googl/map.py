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
        return File(self.local.p.name, self.local.mimeType,
                    parents=[File.folder(self.destination).id],
                    media_body=self.media())
 
    def media(self) -> MediaFileUpload:
        return MediaFileUpload(
            str(self.local.p), mimetype=self.local.mimetype) \
            if self.local.p.is_file() else None

    def sync(self, action: File.Action=File.one):
        action()
        file.on_subpaths(
            lambda p: Map(local=p, destination=self.destination / p.name) \
                .sync(action))

    def consistent(self) -> bool:
        return Relation([self.local],
                        Map(self.local.p, self.drive).file.matches(), 
                        lambda local: self.file(local, self.destination)) \
            .one_to_one()
