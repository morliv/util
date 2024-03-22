from pathlib import Path, PurePath

import arg
from .query import Query
from .api import request
from .file import File


def results():
    return arg.act(parsed_args(), [listing, mapping])


def parsed_args():
    args = arg.parse([
        (('-l', '--local-source-path'), {'type': str}),
        (('-d', '--drive-path'), {'default': '/', 'type': str}),
        (('-f', '--list-files'), {'action': 'store_true'})])
    args.local_source_path = Path(args.local_source_path).expanduser()
    args.drive_path = PurePath(args.drive_path)
    return args


def listing(args):
    if args.list_files: return File.path(args.drive_path)


def mapping(args):
    if args.local_source_path: return File.sync(args.local_source_path,
                                                args.drive_path)
