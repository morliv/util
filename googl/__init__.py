from pathlib import Path

import arg
from googl.api import Service
from googl.query import Query
from googl.file import File
from googl.map import Map


def results():
    return act(parsed_args())


def parsed_args():
    args = [(('-l', '--local-source-path'), {'type': str}),
            (('-d', '--drive-path'), {'default': '/', 'type': str}),
            (('-f', '--list-files'), {'action': 'store_true'})]
    return arg.parse(args)


def act(args):
    return {f.__name__: f(args) for f in (listing, mapping)}


def listing(args):
    if args.list_files: return File.files(args.drive_path)


def mapping(args):
    if args.local_source_path:
        return Map(Path(args.local_source_path), Path(args.drive_path))
