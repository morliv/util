import time
import logging
import subprocess
from pathlib import Path


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
            logging.info(f"Finished: {output_file.name}")
            break
        sec += 1
    if not stopped:
        output_file.write(f"Terminated with {sec_limit} sec limit")

