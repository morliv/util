#!/usr/bin/env python3

from pathlib import Path

import arg
from googl import File, Map


def parsed_args():
    args = [(('-l', '--local-source-path'), {'type': str}),
            (('-d', '--drive-path'), {'default': '/', 'type': str}),
            (('-f', '--list-files'), {'action': 'store_true'})]
    return arg.parse(args)


def main(args):
    run(args.list_files, Path(args.local_source_path), Path(args.drive_path))


def run(list_files, local_source_path, drive_path):
    if list_files:
        File.files(drive_path)
    Map(local_source_path.expanduser(), drive_path)


if __name__ == '__main__':
    main(parsed_args())
