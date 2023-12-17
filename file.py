from __future__ import annotations
import shutil
import difflib
import tempfile
from pathlib import Path
from typing import List


def temp_file(content, dir=None):
    file = tempfile.NamedTemporaryFile(mode='w+t', dir=dir, delete=False)
    file.write(content)
    file.flush()
    return file
 

class File:
    def __init__(self, content=None, dir=None, create=temp_file):
        self.f = create(content='', dir=dir) if content else create(dir=dir)
        self.p = Path(self.f.name)


class Structure:
    def __init__(self, blueprint=[], dir=None):
        self.blueprint = blueprint
        self.dir = dir
        self.files = self._files()
    
    def _files(self):
        return [self._file(content) for content in self.blueprint]

    def _file(self, content):
        return Dir(self.dir, content) \
            if isinstance(content, list) else \
            File(content, self.dir)

    def clean(self):
        for f in self.files:
            f.clean() if isinstance(f, Dir) else f.f.close()
    
    def representation(self):
        return [self.representation(f.structure) if isinstance(f, Dir) else f.f.read() \
        for f in self.files]
        

class Dir(File):
    def __init__(self, blueprint=[], dir=None,
                 create=tempfile.TemporaryDirectory):
        super().__init__(create=create, dir=dir) 
        self.structure = Structure.__init__(blueprint, dir)
   

def remove_occurances(string, file_path):
    with open(file_path, "r") as input_file:
        file_contents = input_file.readlines()

    modified_contents = [line.replace(string, "") for line in file_contents]

    with open(file_path, "w") as output_file:
        output_file.writelines(modified_contents)


def remove_spaces_and_line_symbols(name: str):
    for symbol in [" ", "_", "-"]:
        name = name.replace(symbol, "")
    return name


def matches_ignoring_spaces_and_line_symbols(name: str, strings: List[str]):
    return remove_spaces_and_line_symbols(name) in [
        remove_spaces_and_line_symbols(string) for string in strings
    ]


def read_file(file_path):
    with open(file_path) as file:
        return file.readlines()


def files_are_equivalent(file1_path: Path, file2_path: Path, print_diff=True):
    diff = difflib.ndiff(read_file(file1_path), read_file(file2_path))

    def analyze_line(line):
        print(line)
        return line.startswith("  ")

    return all(analyze_line(line) for line in diff)


def renew(path: Path, mkdirs=True, clean=False, match_as_prefix=False):
    if clean:
        if path.is_file():
            originally_file = True
            path.unlink()
        if path.is_dir():
            shutil.rmtree(path)
        if match_as_prefix:
            for match in path.glob('*'):
                renew(match, clean)
    originally_file = False
    if mkdirs:
        if originally_file:
            path.parent.mkdir(parents=True, exist_ok=True)
        else:
            path.mkdir(parents=True, exist_ok=True)
    return path


def local_data_dir(file_attr: str):
    return renew(Path(file_attr).resolve().parent / "data", mkdirs=True)
