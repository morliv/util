from pathlib import Path
import shutil
import difflib
from typing import List, Set


def prepend_path(dir_path, paths) -> Set[Path]:
    return {Path(dir_path) / path for path in paths}

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


def mkdirs(path: Path, clean=False):
    if path.exists() and clean:
        if path.is_file():
            path.unlink()
        else:
            shutil.rmtree(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    return path


def local_data_dir(file_attr: str):
    return mkdirs(Path(file_attr).resolve().parent / "data")
