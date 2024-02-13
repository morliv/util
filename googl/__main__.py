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
    if args.list_files: File.files(args.drive_path)
    Map(Path(args.local_source_path), Path(args.drive_path)).sync()


if __name__ == '__main__':
    main(parsed_args())
