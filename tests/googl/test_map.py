import sys
from pathlib import Path
from typing import List, Callable
from hashlib import md5

import pytest

from relation import Relation
import file
from googl import results, api, File, Map


def _equal_contents(local: file.File, drive: File) -> bool:
    return Relation(list(local.p.iterdir()), \
        File(parents=[drive.id]).matches(), equal).bijection()


def _equal_content(local: file.File, drive: File) -> bool:
    with open(local.p, 'rb') as l:
        return md5(l.read()).hexdigest() \
            == md5(drive.content()).hexdigest()


def _equivalency_func(are_dirs: bool) -> Callable:
    return _equal_contents if are_dirs else _equal_content


def equal(local: file.File, drive: File) -> bool:
    return local.p.name == drive.name \
        and (local.p.is_dir() == (drive.mimeType == api.FOLDER_MIMETYPE)) \
        and _equivalency_func(local.p.is_dir())(local, drive)

def consistent(files) -> bool:
    possibilities = [drive_f for f in files \
                for drive_f in File(parents=['root']).matches(f.p.name)]
    assert Relation(files, possibilities, equal).one_to_one()


def finalize(files: List[Path], maps: List[Map]):
    consistent(files)
    for m in maps: m.drive.delete()


def test_drive_map(files):
    finalize(files, [Map(f.p).sync() for f in files])


@pytest.mark.skip
def test_command_line(files):
    maps = []
    for f in files:
        sys.argv = ['', '-l', f.p]
        maps.append(results()['mapping'])
    finalize(files, maps)
