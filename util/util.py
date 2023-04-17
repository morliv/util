import os
import shutil


def clean_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    else:
        for item in os.scandir(directory_path):
            if item.is_file():
                os.remove(item.path)
            elif item.is_dir():
                shutil.rmtree(item.path)
