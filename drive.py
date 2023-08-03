#!/usr/bin/env python3

import argparse
import io
import hashlib
from pathlib import Path
from typing import Optional, List, Set
from itertools import chain
from functools import partial

import magic
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

import processing
import google_api


def main():
    args = parsed_args()
    Drive.sync(Path(args.local_path).expanduser(), Path(args.drive_folder), args.only_contents)


def parsed_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--local_path', type=str)
    parser.add_argument('-d', '--drive_folder', type=str)
    parser.add_argument('-o', '--only_contents', action='store_true')
    return parser.parse_args()


class Drive:
    service = google_api.service('drive', 3)
    files = google_api.service('drive', 3).files()

    @staticmethod
    def sync(file_path: Path, drive_folder: Path, only_contents=False) -> str:
        drive_folder_id = Drive.keep_first(Drive.obtain_folders(drive_folder))
        sync_parameterized = partial(Drive.sync, drive_folder=drive_folder if only_contents else
        drive_folder / file_path.name, only_contents=only_contents)
        if file_path.is_dir():
            processing.recurse_on_subpaths(sync_parameterized, file_path)
            return drive_folder_id

        equivalent_file_ids = Drive.equivalents(file_path, drive_folder)
        if equivalent_file_ids:
            return Drive.keep_first(equivalent_file_ids)
       
        return Drive.try_write_file(vars(Metadata(file_path, [drive_folder_id])))

    @staticmethod
    def try_write_file(file_metadata: dict):
        try:
            Drive.write(file_metadata)            
        except HttpError as error:
            print(f'An error occurred: {error}')
            
    @staticmethod
    def write_file(file_metadata: dict):
        media = MediaFileUpload(str(file_path),
        mimetype=file_metadata.mimeType)
        file_id = Drive.service.files().create(body=file_metadata,
                                      media_body=media,
                                      fields='id').execute().get("id")
        return {file_id}

    @staticmethod
    def obtain_folders(path: Path) -> Optional[Set[str]]:
        path = '/' / path
        if len(path.parts) == 1:
            return ['root']
        folder_info = vars(Metadata(path.name, list(Drive.obtain_folders(path.parent)), 'application/vnd.google-apps.folder'))
        folder_ids = Drive.matching_files_in_parents(**folder_info)
        if folder_ids:
            print(f'Existing folder ids: {folder_ids}')
        else:
            folder_ids = [Drive.files.create(body=folder_info, fields='id').execute()['id']]
            print(f'Folder created, id: {folder_ids[0]}')
        return folder_ids

    @staticmethod
    def matching_files_in_parents(name: str, mimeType: str, parents: Optional[Set[str]]) -> Set[str]:
        return set(chain.from_iterable(map(lambda parent: Drive.matching_files(name, mimeType, parent), parents)))

    @staticmethod
    def matching_files(name: str, mimeType: str, parent: Optional[str]) -> Set[str]:
        query = f"name = '{name}' and mimeType = '{mimeType}' and '{parent}' in parents"
        return set(map(lambda id_dict: id_dict['id'], Drive.files.list(q=query, fields='files(id)').execute().get('files', [])))

    @staticmethod
    def print_permissions(folder_id):
        permissions = Drive.service.permissions().list(fileId=folder_id).execute()
        for permission in permissions.get('permissions', []):
            print(f"ID: {permission['id']}, Type: {permission['type']}, Role: {permission['role']}")

    @staticmethod
    def equivalents(local_file_path: Path, drive_parent_path: Path) -> Set[str]:
        file_ids_of_equivalents = set()
        local_file_name = local_file_path.name
        mimetype = magic.from_file(str(local_file_path), mime=True)
        for file_id in Drive.matching_files_in_parents(local_file_name, mimetype, Drive.obtain_folders(drive_parent_path)):
            if Drive.equivalent(local_file_path, file_id):
                file_ids_of_equivalents.add(file_id)
        return file_ids_of_equivalents

    @staticmethod
    def file_content(file_id: str) -> bytes:
        request = Drive.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        return fh.getvalue()

    @staticmethod
    def equivalent(local_file_path: Path, file_id: str) -> bool:
        google_file_content = Drive.file_content(file_id)
        with open(local_file_path, 'rb') as local_file:
            local_file_content = local_file.read()
        google_file_md5 = hashlib.md5(google_file_content).hexdigest()
        local_file_md5 = hashlib.md5(local_file_content).hexdigest()
        return google_file_md5 == local_file_md5

    @staticmethod
    def keep_first(file_ids: List[str]) -> str:
        for file_id in file_ids[1:]:
            Drive.try_delete(equivalent_file_id)
        return equivalent_file_ids[0]
        
    @staticmethod
    def try_delete(file_id: str):
        try:
           files.delete(fileId=file_id).execute() 
        except HttpError as e:
            print(e)

class Metadata():
    def __init__(self, file_path, parent_file_ids):
        self.filename = file_path.name
        self.parent = list(parent_file_ids)
        self.mimeType = magic.from_file(str(file_path), mime=True)

    
if __name__=="__main__":
    main()

