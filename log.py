from pathlib import Path
import logging


def setup(caller_path):
    logging.basicConfig(level=logging.INFO)
    file_handler = logging.FileHandler(Path(caller_path).parent / "logs.log")
    logging.getLogger().addHandler(file_handler)
