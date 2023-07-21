import time
import os
import logging
import subprocess
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def limit(process: subprocess.Popen, sec_limit: float, output_file: Path):
    stopped = False
    sec = 0
    while sec < sec_limit:
        time.sleep(1)
        poll = process.poll()
        #python>3.8: if (poll := process.poll()) is not None:
        if poll is not None:
            output_file.write(
                    f"Ran for {sec} sec; process poll value is {poll}"
                    )
            stopped = True
            logging.info(f"Finished: {Path(output_file.name).stem}")
            break
        sec += 1
    if not stopped:
        output_file.write(f"Terminated with {sec_limit} sec limit")


class CustomEventHandler(FileSystemEventHandler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def on_modified(self, event):
        if event.is_directory:
            for dirpath, dirnames, filenames in os.walk(event.src_path):
                for filename in filenames:
                    self.callback(Path(dirpath) / filename)
        else:
            self.callback(Path(event.src_path))


def call_upon_file_addition(directory_to_watch, callback):
    observer = Observer()
    observer.schedule(CustomEventHandler(callback), str(directory_to_watch), recursive=True)
    observer.start()
    return observer

