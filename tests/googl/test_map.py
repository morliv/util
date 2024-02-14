import inspect
import pytest
from typing import Callable

from relation import Relation
from googl.file import File
from googl.map import Map

@pytest.fixture
def map(path):
    m = Map(path)
    m.sync()
    yield m.drive
    m.file.delete()

import subprocess
from pathlib import Path
def upload(path, monkeypatch):
    monkeypatch.setattr('sys.argv', ['-l', path]).file
    script_path = Path.home() / 'util/googl/__main__.py'
    subprocess.run(['python', '-m', 'googl', '-l', path])

@pytest.mark.parametrize('file_converter', [map, ])
def consistent(paths, file_converter: Callable=map) -> bool:
    return Relation(paths,
                    File.files(),
                    lambda p: Map(p).file()) \
        .one_to_one()
