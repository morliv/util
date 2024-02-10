from pathlib import Path
from typing import List

from googleapiclient.http import MediaFileUpload

import file
from relation import Relation
from googl import File


class Map:
    def __init__(self, local: Path, drive: Path=Path('/'), action='one'):
        self.local, self.drive  = Path(local), Path(drive)
        self.file = File.local(local, drive, action)

    def sync(self, action='one'):
        getattr(self.file, action)()
        if self.local.is_dir():
           for p in self.local.iterdir():
               Map(local=p, drive=self.drive / p.name, action=action) \
                .sync(action)

    def list(self) -> List[File]:
        equivalent, matching_metadata = [], []
        for f in self.file.list():
            if f.equivalent(): equivalent.append()
            else: matching_metadata.append(f)
        return equivalent.extend(matching_metadata)

    def file(self, action='list') -> File:
        mimeType = file.File(self.local).mimetype(File.FOLDER_MIMETYPE)
        parents = [File.folder()]
        media = MediaFileUpload(str(self.local), mimetype=mimeType) \
            if self.local.is_file() else None
        return File(self.local.name, mimeType, parents=parents, media_body=media)
    
    def consistent(self) -> bool:
        return Relation([self.local], File.file(self.local, self.drive).matches(), \
                        partial(File.equivalent, drive=self.drive)).one_to_one()

    def file(self) -> File:
        return File(self.local.name, parents=[File.folder(self.drive).id])
