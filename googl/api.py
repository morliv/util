from __future__ import annotations
from pathlib import Path
from typing import Callable, List

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

import obj
from dictionary import gets
from . import Query


# If modifying these scopes, delete token.json
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
DIR = Path(__file__).resolve().parent
CREDENTIALS = DIR / "credentials.json"
TOKEN = DIR / "token.json"

def service(service_name, version):
    return build(service_name, "v" + str(version), credentials=_creds())


def _creds():
    creds = None
    if TOKEN.exists():
        creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN, "w") as token:
            token.write(creds.to_json())
    return creds


def handle_response(e: HttpError):
    if e.resp.status == 404:
        return None
    raise


def request(f: Callable) -> dict:
    try:
        return f.execute()
    except HttpError as e:
        handle_response(e)


def set(the_obj, f: Callable) -> type:
    return obj.set(the_obj, request(f))



sheets = service('sheets', 4)
drive = service('drive', 3)
files = drive.files()


class Response:
    def __init__(self, query: Query):
        self.q = query

    def list(self, pageToken: str=None) -> tuple[list, str]:
        fs, t = gets(self._page(pageToken), {'files': [], 'nextPageToken': []})
        return fs + (t and self.list(t))

    def _page(self, pageToken):
        FS = f"files({','.join(Query.FIELDS | {'owners'})}),nextPageToken"
        return request(files.list(q=self.q, fields=FS, pageToken=pageToken))
