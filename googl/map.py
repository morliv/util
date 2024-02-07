from pathlib import Path
from typing import List

import file
from googl import File


class Map():
    def __init__(self, local: Path, drive: Path=Path('/'), action='one'):
        self.local, self.drive  = Path(local), Path(drive)
        self.file = File.local(local, drive, action)
        self.sync(action)

    def sync(self, action='one'):
        getattr(self.file, action)()
        if self.local.is_dir():
           for p in self.local.iterdir():
               Map(local=p, drive=self.drive / p.name, action=action)

    def list(self) -> List[File]:
        equivalent, matching_metadata = [], []
        for f in self.file.list():
            if f.equivalent(): equivalent.append()
            else: matching_metadata.append(f)
        return equivalent.extend(matching_metadata)

    def local(local: Path, drive: Path, action='list') -> File:
        local, drive = Path(local), Path(drive)
        mimeType = file.File(local).mimetype(File.FOLDER_MIMETYPE)
        parents = [File.folder()]
        media = MediaFileUpload(str(local), mimetype=mimeType) \
            if local.is_file() else None
        return File(local.name, mimeType, parents=parents, media_body=media)
    
    def consistent(local: Path, drive: Path) -> bool:
        return Relation([local], File.file(local, drive).matches(), \
                        partial(File.equivalent, drive=drive)).one_to_one()

    def file(local: Path, drive_parent: Path) -> File:
        return File(local.name, parents=[File.folder(drive_parent).id])
