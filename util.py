from pathlib import Path
import shutil
import difflib


def remove_occurances(string, file_path):
    with open(file_path, "r") as input_file:
        file_contents = input_file.readlines()
        
    modified_contents = [line.replace(string, "") for line in file_contents]

    with open(file_path, "w") as output_file:
        output_file.writelines(modified_contents)


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

def data_dir(file_attr: str):
    return mkdirs(Path(file_attr).resolve().parent / "data")
