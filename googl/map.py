from pathlib import Path
from typing import List
import magic

from googleapiclient.http import MediaFileUpload

from googl import File


class Map():
    def __init__(self, local: Path, drive: Path=Path('/'), action='one'):
        self.local = Path(local)
        self.drive = Path(drive)
        mimeType = magic.from_file(str(local), mime=True) \
            if self.local.is_file() else File.FOLDER_MIMETYPE
        parents = []
        for f in File.files(drive, action):
            parents.append(f.id)
        media = MediaFileUpload(str(self.local), mimetype=mimeType) \
            if self.local.is_file() else None
        self.file = File(self.local.name, mimeType, parents=parents,
                         media_body=media)
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
