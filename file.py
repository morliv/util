import shutil
import difflib
import tempfile
from pathlib import Path
from typing import List


def temp_file(self, content, root=None):
    file = tempfile.NamedTemporaryFile(mode='w+t', dir=root, delete=False)
    file.write(content)
    file.flush()
    return file
 
class Dir:
    def __init__(self, structure={}, name=None, dir=None):
        self.structure = structure
        self.name = name
        self.dir = dir
        self.f = tempfile.TemporaryDirectory(name=name, dir=dir)
        self.files = self._files()
    
    def _files(self):
        return [self._file(name, content) for name, content
                in self.structure.items()]
    
    def _file(self, name, content):
        return Dir(content, name, self.name) if isinstance(content, dict) else \
            temp_file(name, dir)

    def clean(self):
        for f in self.files:
            f.clean() if isinstance(f, Dir) else f.unlink()

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

