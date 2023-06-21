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
    Drive.write_dir(Path(args.path).expanduser(), Path(args.folder))


def parsed_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', type=str)
    parser.add_argument('-f', '--folder', type=str)
    return parser.parse_args()


class Drive:
    service = google_api.service('drive', 3)

    @staticmethod
    def write_dir(local: Path, drive_folder: Path):
        for file_path in local.iterdir():
            if file_path.is_dir():
                Drive.write_dir(file_path, drive_folder / file_path.name)
            else:
                Drive.write_file(file_path, drive_folder)

    @staticmethod
    def write_file(file_path: Path, drive_folder: Path) -> Optional[str]:
        mimetype = magic.from_file(file_path, mime=True)
        try:
            folder = Drive.obtain_folder(drive_folder)
            
            file_metadata = {
                'name': file_path.name,
                'parents': folder['id']
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
    def obtain_folder(path: Path) -> Optional[dict]:
        existing = Drive.existing_folder(path) 
        if existing:
            return existing
        else:
            return Drive.create_folder(path, Drive.obtain_folder(path.parent)['id'])


    @staticmethod
    def existing_folder(drive_folder: Path) -> Optional[dict]:
        folder_id = 'root'
        for folder_name in drive_folder.parts:
            query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and '{folder_id}' in parents"
            response = Drive.service.files().list(q=query, fields='files(id)').execute()
            items = response.get('files', [])
            if not items:
                return None
            folder_id = items[0]['id']
        return {'id': folder_id}


    @staticmethod
    def create_folder(folder_path: Path, parent_folder_id='root') -> Optional[dict]:
        try:
            for folder_name in folder_path.parts:
                folder_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [parent_folder_id]
                }
                
                folder = Drive.service.files().create(body=folder_metadata, fields='id').execute()
                parent_folder_id = folder['id']
            
            print(f'Folder created for folder_path {folder_path}. ID: {parent_folder_id}')
            return {'id': parent_folder_id}
        except Exception as e:
            print(f'An error occurred: {str(e)}')
            return None


if __name__=="__main__":
    main()
