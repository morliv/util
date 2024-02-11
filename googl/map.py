from pathlib import Path
from typing import List

from googleapiclient.http import MediaFileUpload

import file
from relation import Relation
from googl import File


class Map:
    def __init__(self, local: Path, drive: Path=Path('/')):
        self.local = Path(local)
        self.file = self.file(local, Path(drive))

    def file(local: Path, drive: Path) -> File:
        local_file = file.File(local, folder_mimetype=File.FOLDER_MIMETYPE)
        parents = [File.folder(drive).id]
        media = MediaFileUpload(str(local), mimetype=local_file.mimeType) \
            if local.is_file() else None
        return File(local.name, local_file.mimeType, parents=parents,
            media_body=media)

    def sync(self, action: File.Action=File.one):
        action()
        file.on_subpaths(
            lambda p: Map(local=p, drive=self.drive / p.name).sync(action)) 

    def list(self) -> List[File]:
        equivalent, matching_metadata = [], []
        for f in self.file.list():
            if f.equivalent(): equivalent.append()
            else: matching_metadata.append(f)
        return equivalent.extend(matching_metadata)

    def consistent(self) -> bool:
        return Relation([self.local], File.file(self.local, self.drive).matches(), \
                        partial(File.equivalent, drive=self.drive)).one_to_one()

    def file(self) -> File:
        return File(self.local.name, parents=[File.folder(self.drive).id])
