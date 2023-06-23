#!/usr/bin/env python3

import argparse
from pathlib import Path
from typing import Optional

import magic
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

import google_api


def main():
    args = parsed_args()
    Drive.write(Path(args.local_path).expanduser(), Path(args.drive_path))


def parsed_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--local_path', type=str)
    parser.add_argument('-d', '--drive_path', type=str)
    return parser.parse_args()


class Drive:
    service = google_api.service('drive', 3)

    @staticmethod
    def write(file_path: Path, drive_folder: Path) -> Optional[str]:
        drive_folder_id = Drive.obtain_folder(drive_folder)
        if file_path.is_dir():
            for path in file_path.iterdir():
                write_file(path, drive_folder / file_path.name)
        mimetype = magic.from_file(file_path, mime=True)
        try:
            file_metadata = {
                'name': file_path.name,
                'parents': drive_folder_id,
            }
            media = MediaFileUpload(file_path, mimetype=mimetype)
            file = Drive.service.files().create(body=file_metadata,
                                          media_body=media,
                                          fields='id').execute()
            print(f'File ID: {file.get("id")}')
        except HttpError as error:
            print(f'An error occurred: {error}')
            file = None

        return file.get('id') if file else None


    @staticmethod
    def obtain_folder(path: Path) -> Optional[str]:
        path = '/' / path
        if len(path.parts) == 1:
            return 'root'
        folder_info= {
            'name': path.name,
            'mimetype': 'application/vnd.google-apps.folder',
            'parents': [Drive.obtain_folder(path.parent)]
        }
        query = f"name = '{folder_info['name']}' and mimetype = {folder_info['mimetype']} and '{folder_info['parents'][0]}' in parents"
        items = drive.service.files().list(q=query, fields='files(id)').execute().get('files', [])
        if not items:
            folder_id = drive.service.files().create(body=folder_info, fields='id').execute()['id']
            print(f'folder created id: {folder_id}')
        return folder_id


if __name__=="__main__":
    main()
