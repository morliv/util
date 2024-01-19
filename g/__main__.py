#!/usr/bin/env python3

import argparse
from pathlib import Path

from g import Query, File, Map

def main():
    args = parsed_args()
    drive_folder_path = Path(args.drive_folder)
    if args.list_files:
        File.files(drive_folder_path)
    else:
        Map(Path(args.source).expanduser(), drive_folder_path)


def parsed_args():
    p = argparse.ArgumentParser()
    for a, k in [(('-l', '--source'), {'type': str}),
              (('-d', '--drive_folder'), {'default': '/', 'type': str}),
              (('-f', '--list-files'), {'action': 'store_true'})]:
        p.add_argument(*a, **k)
    return p.parse_args()


if __name__ == '__main__':
    main()
