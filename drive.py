#!/usr/bin/env python3

import argparse
from pathlib import Path
from typing import Optional, List

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
    files = google_api.service('drive', 3).files()

    @staticmethod
    def write(file_path: Path, drive_folder: Path) -> Optional[str]:
        drive_folder_ids = Drive.obtain_folders(drive_folder)
        if file_path.is_dir():
            for path in file_path.iterdir():
                Drive.write(path, drive_folder / file_path.name)
        mimetype = magic.from_file(file_path, mime=True)
        try:
            file_metadata = {
                'name': file_path.name,
                'parents': drive_folder_ids,
            }
            media = MediaFileUpload(file_path, mimetype=mimetype)
            file_id = Drive.service.files().create(body=file_metadata,
                                          media_body=media,
                                          fields='id').execute().get("id")
        except HttpError as error:
            print(f'An error occurred: {error}')

        return file_id if file_id else None


    @staticmethod
    def list_files(name: str, mimeType: str, parent: Path) -> List:
        query = f"name = '{name}' and mimeType = '{mimeType}' and '{parent}' in parents"
        return Drive.files.list(q=query, fields='files(id)').execute().get('files', [])


    @staticmethod
    def matching_items(name: str, mimeType: str, parents: List) -> List:
        return [file_dict['id'] for parent in parents for file_dict in Drive.list_files(name, mimeType, parent)]


    @staticmethod
    def obtain_folders(path: Path) -> Optional[List[str]]:
        path = '/' / path
        breakpoint()
        if len(path.parts) == 1:
            return ['root']
        folder_info = {
            'name': path.name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': Drive.obtain_folders(path.parent)
        }
        folder_ids = Drive.matching_items(**folder_info)
        if folder_ids:
            print(f'Existing folder ids: {folder_ids}')
        else:
            breakpoint()
            folder_ids = [Drive.files.create(body=folder_info, fields='id').execute()['id']]
            print(f'folder created, id: {folder_ids[0]}')
        return folder_ids


    @staticmethod
    def print_permissions(folder_id):
        permissions = Drive.service.permissions().list(fileId=folder_id).execute()
        for permission in permissions.get('permissions', []):
            print(f"ID: {permission['id']}, Type: {permission['type']}, Role: {permission['role']}")


if __name__=="__main__":
    main()

