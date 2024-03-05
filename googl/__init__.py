from pathlib import Path

import arg
from .query import Query
from .api import request, files
from .response import Response
from .file import File
from .files import Files
from .map import Map


def results():
    return arg.act(parsed_args(), [listing, mapping])


def parsed_args():
    return arg.parse([
        (('-l', '--local-source-path'), {'type': str}),
        (('-d', '--drive-path'), {'default': '/', 'type': str}),
        (('-f', '--list-files'), {'action': 'store_true'})])


def listing(args):
    if args.list_files: return File.files(args.drive_path)


def mapping(args):
    if args.local_source_path:
        return Map(Path(args.local_source_path), Path(args.drive_path))
