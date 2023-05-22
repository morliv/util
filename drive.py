from pathlib import Path
from typing import Optional

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


def write_file(file_path: Path, folder_path: Path) -> Optional[str]:
    if file_path.suffix == '.txt':
        mimetype = 'text/plain'
    elif file_path.suffix == '.pdb':
        mimetype = 'chemical/x-pdb'

    try:
        service = build('drive', 'v3', credentials=google.get_creds())
        folder = find_folder_by_path(service, folder_path)
        
        if folder is None:
            print(f"Folder '{folder_path}' not found.")
            return None

        file_metadata = {
            'name': file_path.name,
            'parents': [folder['id']]
        }
        media = MediaFileUpload(file_path, mimetype=mimetype)
        file = service.files().create(body=file_metadata,
                                      media_body=media,
                                      fields='id').execute()
        print(f'File ID: {file.get("id")}')
    except HttpError as error:
        print(f'An error occurred: {error}')
        file = None

    return file.get('id') if file else None


def find_folder_by_path(service, folder_path: Path) -> Optional[dict]:
    folders = folder_path.parts
    folder_id = 'root'
    for folder_name in folders:
        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and '{folder_id}' in parents"
        response = service.files().list(q=query, fields='files(id)').execute()
        items = response.get('files', [])
        if not items:
            return None
        folder_id = items[0]['id']
    return {'id': folder_id}

