from pathlib import Path
from typing import Callable

import google.auth
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete token.json
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]
CREDENTIALS = Path.home() / "util/credentials.json"


def token_path():
    return Path.home() / "token.json"


def service(service_name, version):
    return build(service_name, "v" + str(version), credentials=creds())


def creds():
    creds = None
    if token_path().exists():
        creds = Credentials.from_authorized_user_file(token_path(), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path(), "w") as token:
            token.write(creds.to_json())
    return creds

def call(f: Callable):
    return request(f.execute)

def request(f: Callable):
    try:
        return f()
    except HttpError as e:
        handle_response_status(e)

def handle_response_status(e: HttpError):
    if e.resp.status == 404:
        return None
    raise

