#!/usr/bin/env python3

import argparse
from pathlib import Path

import drive

def main():
    args = parsed_args()
    drive_folder_path = Path(args.drive_folder)
    if args.list_files:
        drive.Service.files(drive_folder_path)
    else:
        drive.Map(Path(args.source).expanduser(), drive_folder_path)


def parsed_args():
    p = argparse.ArgumentParser()
    for a, k in [(('-l', '--source'), {type: str}),
              (('-d', '--drive_folder'), {type: str}),
              (('-f', '--list-files'), {action: 'store_true'})]:
        p.add_argument(*a, **k)
    return p.parse_args()


if __name__ == '__main__':
    main()
